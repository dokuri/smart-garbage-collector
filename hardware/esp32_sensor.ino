/*
 * Smart Waste Management System - ESP32 DevKit Sensor Code
 * Hardware: ESP32 DevKit V1 + HC-SR04 (Ultrasonic) + MQ-4 (Methane) + MQ-135 (Air Quality)
 * 
 * This code reads sensor data and sends it to the backend API
 * Bin A1_WET is configured to accept real hardware data
 * 
 * ESP32 DevKit V1 Pin Reference:
 * - GPIO 2  = Built-in LED (active HIGH)
 * - GPIO 4  = Safe for output (Trig)
 * - GPIO 5  = Safe for I/O (Echo) 
 * - GPIO 34 = Input only, ADC1_CH6 (MQ-4)
 * - GPIO 35 = Input only, ADC1_CH7 (MQ-135)
 * - GPIO 32 = ADC1_CH4 (alternative analog)
 * - GPIO 33 = ADC1_CH5 (alternative analog)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ============================================================
// PIN CONFIGURATION - ESP32 DevKit V1
// ============================================================
#define TRIG_PIN 4       // HC-SR04 Trigger Pin (GPIO4 - safe for output)
#define ECHO_PIN 5       // HC-SR04 Echo Pin (GPIO5 - safe for I/O)
#define MQ135_PIN 35     // MQ-135 Analog Pin - Air Quality (ADC1_CH7, input only)
#define MQ4_PIN 34       // MQ-4 Analog Pin - Methane (ADC1_CH6, input only)
#define LED_PIN 2        // Built-in Blue LED for status

// ============================================================
// WIFI CONFIGURATION - ⚠️ UPDATE THESE!
// ============================================================
const char* WIFI_SSID = "YOUR_WIFI_SSID";        // Your WiFi network name
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"; // Your WiFi password

// Backend API URL - ⚠️ Update with your laptop's IP address
// Find it using: ipconfig (Windows) or ifconfig (Mac/Linux)
// Example: If your laptop IP is 192.168.1.50, use that below
const char* BACKEND_URL = "http://192.168.1.100:5000/api/locations/A1/bins/A1_WET/hardware";

// ============================================================
// SENSOR CALIBRATION
// ============================================================
const float BIN_HEIGHT_CM = 50.0;      // Total height of bin in cm (measure your bin)
const int MQ135_BASELINE = 100;         // Baseline reading in clean air (calibrate)
const int MQ4_BASELINE = 200;           // Baseline reading in clean air (calibrate)

// ============================================================
// TIMING
// ============================================================
const unsigned long SEND_INTERVAL = 10000;  // Send data every 10 seconds
unsigned long lastSendTime = 0;

// ============================================================
// SETUP
// ============================================================
void setup() {
    Serial.begin(115200);
    
    // Initialize pins
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    pinMode(MQ135_PIN, INPUT);
    pinMode(MQ4_PIN, INPUT);
    pinMode(LED_PIN, OUTPUT);
    
    Serial.println("\n");
    Serial.println("╔════════════════════════════════════════════════╗");
    Serial.println("║  Smart Waste System - ESP32 Sensor Module      ║");
    Serial.println("║  Bin ID: A1 (Hardware Enabled)                 ║");
    Serial.println("╚════════════════════════════════════════════════╝");
    
    // Connect to WiFi
    connectWiFi();
    
    // Warm up sensors (MQ sensors need ~2 minutes to stabilize)
    Serial.println("\n⏳ Warming up gas sensors (30 seconds)...");
    for (int i = 30; i > 0; i--) {
        Serial.printf("   %d seconds remaining...\n", i);
        digitalWrite(LED_PIN, !digitalRead(LED_PIN));
        delay(1000);
    }
    
    Serial.println("\n✅ System ready! Starting sensor readings...\n");
}

// ============================================================
// MAIN LOOP
// ============================================================
void loop() {
    // Check WiFi connection
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("⚠️ WiFi disconnected! Reconnecting...");
        connectWiFi();
    }
    
    // Send data at intervals
    if (millis() - lastSendTime >= SEND_INTERVAL) {
        // Read all sensors
        float fillLevel = readFillLevel();
        float methane = readMethane();
        float airQuality = readAirQuality();
        
        // Display readings
        Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        Serial.printf("📊 Fill Level:  %.1f%%\n", fillLevel);
        Serial.printf("🔥 Methane:     %.1f ppm\n", methane);
        Serial.printf("💨 Air Quality: %.1f\n", airQuality);
        
        // Send to backend
        sendDataToBackend(fillLevel, methane, airQuality);
        
        lastSendTime = millis();
    }
    
    // Blink LED to show activity
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    delay(100);
}

// ============================================================
// WIFI CONNECTION
// ============================================================
void connectWiFi() {
    Serial.printf("\n📶 Connecting to WiFi: %s", WIFI_SSID);
    
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi Connected!");
        Serial.printf("   IP Address: %s\n", WiFi.localIP().toString().c_str());
    } else {
        Serial.println("\n❌ WiFi connection failed!");
        Serial.println("   Check SSID and password, then restart.");
    }
}

// ============================================================
// ULTRASONIC SENSOR - Fill Level
// ============================================================
float readFillLevel() {
    // Send trigger pulse
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    
    // Read echo duration
    long duration = pulseIn(ECHO_PIN, HIGH, 30000);  // 30ms timeout
    
    if (duration == 0) {
        Serial.println("⚠️ Ultrasonic sensor timeout!");
        return -1;
    }
    
    // Calculate distance in cm
    float distance = duration * 0.034 / 2;
    
    // Convert to fill level percentage
    // When distance is small, bin is full; when large, bin is empty
    float fillLevel = ((BIN_HEIGHT_CM - distance) / BIN_HEIGHT_CM) * 100;
    
    // Clamp to valid range
    fillLevel = constrain(fillLevel, 0, 100);
    
    return fillLevel;
}

// ============================================================
// MQ-4 SENSOR - Methane Detection
// ============================================================
float readMethane() {
    // Read analog value (0-4095 on ESP32)
    int rawValue = analogRead(MQ4_PIN);
    
    // Convert to PPM (simplified conversion)
    // In real application, use proper calibration curve
    float ppm = map(rawValue, MQ4_BASELINE, 4095, 0, 1000);
    ppm = constrain(ppm, 0, 1000);
    
    return ppm;
}

// ============================================================
// MQ-135 SENSOR - Air Quality
// ============================================================
float readAirQuality() {
    // Read analog value
    int rawValue = analogRead(MQ135_PIN);
    
    // Convert to air quality index (0-500)
    float aqi = map(rawValue, MQ135_BASELINE, 4095, 0, 500);
    aqi = constrain(aqi, 0, 500);
    
    return aqi;
}

// ============================================================
// SEND DATA TO BACKEND API
// ============================================================
void sendDataToBackend(float fillLevel, float methane, float airQuality) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("❌ Cannot send data - WiFi not connected");
        return;
    }
    
    HTTPClient http;
    http.begin(BACKEND_URL);
    http.addHeader("Content-Type", "application/json");
    
    // Create JSON payload
    StaticJsonDocument<200> doc;
    doc["fill_level"] = fillLevel;
    doc["methane"] = methane;
    doc["air_quality"] = airQuality;
    
    String jsonPayload;
    serializeJson(doc, jsonPayload);
    
    Serial.printf("📤 Sending to: %s\n", BACKEND_URL);
    Serial.printf("   Payload: %s\n", jsonPayload.c_str());
    
    // Send POST request
    int httpCode = http.POST(jsonPayload);
    
    if (httpCode > 0) {
        if (httpCode == HTTP_CODE_OK) {
            String response = http.getString();
            Serial.println("✅ Data sent successfully!");
            Serial.printf("   Response: %s\n", response.c_str());
        } else {
            Serial.printf("⚠️ HTTP Error: %d\n", httpCode);
        }
    } else {
        Serial.printf("❌ Connection failed: %s\n", http.errorToString(httpCode).c_str());
    }
    
    http.end();
}
