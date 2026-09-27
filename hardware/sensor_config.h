/*
 * Smart Waste System - Hardware Configuration
 * Update these values based on your setup
 */

#ifndef SENSOR_CONFIG_H
#define SENSOR_CONFIG_H

// ============================================================
// WIFI SETTINGS - MUST UPDATE!
// ============================================================
#define WIFI_SSID "YOUR_WIFI_NETWORK_NAME"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// ============================================================
// BACKEND SERVER - MUST UPDATE!
// ============================================================
// Find your laptop IP: Open Command Prompt, type "ipconfig"
// Look for "IPv4 Address" under your WiFi adapter
#define BACKEND_IP "192.168.1.100"
#define BACKEND_PORT 5000
#define BIN_ID "A1"

// ============================================================
// PIN ASSIGNMENTS (ESP32 DevKit)
// ============================================================
// Ultrasonic Sensor (HC-SR04)
#define ULTRASONIC_TRIG 5
#define ULTRASONIC_ECHO 18

// Gas Sensors (Analog Pins)
#define MQ135_PIN 35   // Air Quality
#define MQ4_PIN 34     // Methane

// Status LED
#define STATUS_LED 2   // Built-in LED

// ============================================================
// SENSOR CALIBRATION
// ============================================================
// Bin dimensions (centimeters)
#define BIN_HEIGHT_CM 50.0
#define BIN_DIAMETER_CM 30.0

// MQ Sensor baselines (adjust after testing in clean air)
#define MQ135_CLEAN_AIR 100
#define MQ4_CLEAN_AIR 200

// ============================================================
// TIMING SETTINGS (milliseconds)
// ============================================================
#define SENSOR_READ_INTERVAL 10000   // 10 seconds between readings
#define WIFI_RETRY_DELAY 5000        // 5 seconds between WiFi retries
#define SENSOR_WARMUP_TIME 30000     // 30 seconds warmup for MQ sensors

// ============================================================
// THRESHOLDS FOR LOCAL ALERTS
// ============================================================
#define FILL_WARNING_THRESHOLD 70
#define FILL_CRITICAL_THRESHOLD 90
#define METHANE_WARNING_THRESHOLD 300
#define METHANE_CRITICAL_THRESHOLD 500

#endif
