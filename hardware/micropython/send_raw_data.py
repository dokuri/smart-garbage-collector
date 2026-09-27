"""
Smart Waste Bin - Sensor Data Sender for A1 Location
=====================================================

Reads data from sensors and posts to backend for A1 bins:
- A1_WET: methane (MQ-4 + MQ-135)
- A1_DRY: fill_level (ultrasonic), weight (HX711)

Wiring:
- Ultrasonic: TRIG=D18, ECHO=D5
- MQ-4: AO=D26
- MQ-135: AO=D27
- HX711: DT=D22, SCK=D23
"""

from machine import Pin, ADC, time_pulse_us
import time
import network
import urequests
import ujson

# ============================================================
# CONFIGURATION
# ============================================================

WIFI_SSID = "CMF by Nothing Phone 1"
WIFI_PASSWORD = "alliswell"

SERVER_IP = "10.170.82.107"
SERVER_PORT = 5000
API_ENDPOINT = "/api/locations/A1/hardware"

SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}{API_ENDPOINT}"

SEND_INTERVAL = 5

# ============================================================
# SENSOR CALIBRATION
# ============================================================

TARE_VALUE = 338611
SCALE_FACTOR = 473.48

# Calibrated for 30cm bin - measured empty distance ~28.5cm
BIN_HEIGHT_CM = 27.0
SENSOR_OFFSET_CM = 2.0

# ============================================================
# PIN CONFIGURATION
# ============================================================

TRIG_PIN = 18
ECHO_PIN = 5
MQ4_PIN = 26
MQ135_PIN = 27
HX711_DT_PIN = 22
HX711_SCK_PIN = 23

# ============================================================
# SENSOR INITIALIZATION
# ============================================================

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)
trig.value(0)

mq4 = ADC(Pin(MQ4_PIN))
mq4.atten(ADC.ATTN_11DB)
mq4.width(ADC.WIDTH_12BIT)

mq135 = ADC(Pin(MQ135_PIN))
mq135.atten(ADC.ATTN_11DB)
mq135.width(ADC.WIDTH_12BIT)

dt_pin = Pin(HX711_DT_PIN, Pin.IN)
sck_pin = Pin(HX711_SCK_PIN, Pin.OUT)
sck_pin.value(0)

wlan = None

# ============================================================
# WIFI FUNCTIONS
# ============================================================

def connect_wifi():
    global wlan
    print(f"Connecting to WiFi: {WIFI_SSID}")
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print(f"Already connected. IP: {wlan.ifconfig()[0]}")
        return True
    
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    timeout = 15
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
    
    if wlan.isconnected():
        print(f"WiFi connected. IP: {wlan.ifconfig()[0]}")
        return True
    
    print("WiFi connection failed")
    return False

def is_wifi_connected():
    return wlan and wlan.isconnected()

# ============================================================
# SENSOR READING FUNCTIONS
# ============================================================

def read_distance_cm():
    try:
        trig.value(0)
        time.sleep_us(5)
        trig.value(1)
        time.sleep_us(10)
        trig.value(0)
        
        duration = time_pulse_us(echo, 1, 30000)
        
        if duration > 0:
            return round(duration / 58.0, 2)
        return None
    except:
        return None

def read_hx711_raw():
    try:
        timeout = 50
        while dt_pin.value() == 1:
            time.sleep_ms(5)
            timeout -= 1
            if timeout <= 0:
                return None
        
        value = 0
        for i in range(24):
            sck_pin.value(1)
            time.sleep_us(1)
            value = (value << 1) | dt_pin.value()
            sck_pin.value(0)
            time.sleep_us(1)
        
        sck_pin.value(1)
        time.sleep_us(1)
        sck_pin.value(0)
        
        if value & 0x800000:
            value -= 0x1000000
        
        return value
    except:
        return None

def read_weight_grams():
    raw = read_hx711_raw()
    if raw is None:
        return None
    weight = (raw - TARE_VALUE) / SCALE_FACTOR
    return round(max(0, weight), 2)

def read_mq4_raw():
    try:
        total = 0
        for _ in range(10):
            total += mq4.read()
            time.sleep_ms(5)
        return total // 10
    except:
        return None

def read_mq135_raw():
    try:
        total = 0
        for _ in range(10):
            total += mq135.read()
            time.sleep_ms(5)
        return total // 10
    except:
        return None

def estimate_methane_ppm(mq4_adc, mq135_adc):
    """
    Estimate methane PPM from MQ-4 and MQ-135 sensors.
    MQ-4: Primary methane sensor (more sensitive to CH4)
    MQ-135: Air quality sensor (less sensitive to CH4, more to CO2/NH3)
    
    Typical ADC values at clean air: 300-600
    Higher values indicate gas presence.
    """
    methane = 0.0
    
    # MQ-4 is the primary methane sensor
    # Clean air baseline ~400-600, methane presence increases value
    if mq4_adc and mq4_adc > 600:
        # Scale: 600-4095 ADC -> 0-800 ppm (approximate)
        methane += (mq4_adc - 600) * 0.23
    
    # MQ-135 has slight methane sensitivity, add small contribution
    # Clean air baseline ~400-700
    if mq135_adc and mq135_adc > 700:
        # Much smaller contribution than MQ-4
        methane += (mq135_adc - 700) * 0.05
    
    return round(max(0, methane), 1)

def calculate_fill_level(distance_cm):
    if distance_cm is None or distance_cm <= 0:
        return 0.0
    
    empty_space = distance_cm - SENSOR_OFFSET_CM
    fill_height = BIN_HEIGHT_CM - empty_space
    fill_percent = (fill_height / BIN_HEIGHT_CM) * 100
    
    return round(max(0, min(100, fill_percent)), 1)

# ============================================================
# DATA FUNCTIONS
# ============================================================

def read_all_sensors():
    distance_cm = read_distance_cm()
    mq4_raw = read_mq4_raw()
    mq135_raw = read_mq135_raw()
    weight_grams = read_weight_grams()
    
    fill_level = calculate_fill_level(distance_cm)
    methane = estimate_methane_ppm(mq4_raw, mq135_raw)
    
    return {
        "fill_level": fill_level,
        "methane": methane,
        "weight": weight_grams if weight_grams else 0.0,
        "mq4_raw": mq4_raw,
        "mq135_raw": mq135_raw,
        "distance_cm": distance_cm
    }

def post_to_server(data):
    if not is_wifi_connected():
        return False, "WiFi not connected"
    
    try:
        payload = {
            "fill_level": data["fill_level"],
            "methane": data["methane"]
        }
        
        # Only include weight if sensor read was successful (not None/0)
        if data["weight"] and data["weight"] > 0:
            payload["weight"] = data["weight"]
        
        json_data = ujson.dumps(payload)
        print(f"Sending: {json_data}")
        
        response = urequests.post(
            SERVER_URL,
            data=json_data,
            headers={"Content-Type": "application/json"}
        )
        
        status = response.status_code
        response.close()
        
        if status == 200 or status == 201:
            return True, f"HTTP {status}"
        return False, f"HTTP {status}"
    
    except OSError as e:
        return False, f"Network Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

# ============================================================
# MAIN
# ============================================================

def main():
    print("\n" + "="*50)
    print("Smart Waste Bin - A1 Location Sensors")
    print(f"Server: {SERVER_URL}")
    print("="*50)
    
    connect_wifi()
    
    print("Warming up sensors (3s)...")
    time.sleep(3)
    
    reading_count = 0
    
    while True:
        reading_count += 1
        
        sensor_data = read_all_sensors()
        
        print(f"\n--- Reading #{reading_count} ---")
        print(f"Fill Level: {sensor_data['fill_level']}%")
        print(f"Methane: {sensor_data['methane']} ppm")
        print(f"Weight: {sensor_data['weight']} g")
        print(f"MQ4 Raw: {sensor_data['mq4_raw']}, MQ135 Raw: {sensor_data['mq135_raw']}")
        
        if is_wifi_connected():
            success, msg = post_to_server(sensor_data)
            print(f"Send: {'OK' if success else 'FAIL'} - {msg}")
        else:
            print("WiFi disconnected, reconnecting...")
            connect_wifi()
        
        time.sleep(SEND_INTERVAL)

if __name__ == "__main__":
    main()
