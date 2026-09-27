# 🔌 Hardware to Backend Connection Guide

## Overview
This guide shows you how to connect your ESP32 sensor data (running in Thonny) to the backend server, so the data appears in your web dashboard.

---

## 🎯 Connection Flow

```
ESP32 (Thonny) → WiFi → Backend (Flask) → Frontend (Web Dashboard)
```

---

## ⚙️ Step-by-Step Setup

### **Step 1: Configure WiFi in the Script**

Open `hardware/micropython/send_raw_data.py` and update:

```python
# Line 38-39: Your WiFi credentials
WIFI_SSID = "YourWiFiName"              # ← Replace with your WiFi name
WIFI_PASSWORD = "YourWiFiPassword"      # ← Replace with your WiFi password
```

**Important:** Both your computer (running backend) and ESP32 must be on the **same WiFi network**.

---

### **Step 2: Verify Server IP (Already Configured)**

The script is already configured to connect to your laptop:

```python
SERVER_IP = "10.62.147.196"             # ✅ Your laptop's IP
SERVER_PORT = 5000                      # ✅ Backend port
API_ENDPOINT = "/api/locations/A1/bins/A1_WET/hardware"  # ✅ Correct endpoint
```

**If your IP changes**, find your new IP by running:
```powershell
ipconfig
```
Look for "IPv4 Address" under your WiFi adapter.

---

### **Step 3: Ensure Backend is Running**

Make sure your Flask backend is running:

```bash
# In VSCode terminal
cd backend
python app.py
```

You should see:
```
🚀 Smart Waste Management API Running
📡 Server: http://10.62.147.196:5000
```

---

### **Step 4: Run the Script on ESP32**

1. Open **Thonny**
2. Make sure ESP32 is connected
3. Open `send_raw_data.py`
4. Click **Run** (or press F5)

---

## 📊 What You'll See

### **In Thonny Output:**

When WiFi is **NOT connected** (or disabled):
```json
{"timestamp": 12345, "ultrasonic": {"distance_cm": 25.5}, "weight": {...}, ...}
```

When WiFi **IS connected**:
```json
{"timestamp": 12345, "ultrasonic": {"distance_cm": 25.5}, "weight": {...}, ...}
```
*(Same output, but data is also POSTed to backend)*

---

### **In Backend Terminal:**

You'll see incoming requests:
```
127.0.0.1 - - [03/Feb/2026] "POST /api/locations/A1/bins/A1_WET/hardware HTTP/1.1" 200
```

---

### **In Frontend Dashboard:**

1. Open your web dashboard: `http://localhost:5000` or `http://10.62.147.196:5000`
2. Navigate to **Location A1** (Koregaon Park Corner)
3. You'll see the **A1_WET** bin updating with **real-time sensor data**:
   - Fill Level (from ultrasonic distance)
   - Methane Level (from MQ-4 sensor)
   - Hardware Status: **CONNECTED** 🟢

---

## 🔧 Troubleshooting

### **Problem: WiFi won't connect**

**Check:**
- ✅ WiFi SSID and password are correct (case-sensitive!)
- ✅ ESP32 is within WiFi range
- ✅ WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
- ✅ `WIFI_ENABLED = True` in the script

---

### **Problem: Data not appearing in frontend**

**Check:**
1. ✅ Backend is running (`python app.py`)
2. ✅ ESP32 is connected to WiFi (check Thonny output)
3. ✅ Backend terminal shows POST requests
4. ✅ Server IP matches your laptop's current IP
5. ✅ Both devices on same network

**Verify connection:**
```bash
# Check if ESP32 can reach your server
# In browser, visit: http://10.62.147.196:5000/api/hardware/status
```

You should see:
```json
{
  "status": "success",
  "hardware_connected": true,
  "last_update": "2026-02-03T..."
}
```

---

### **Problem: Script runs but only prints data**

This is **normal** when:
- WiFi is disabled (`WIFI_ENABLED = False`)
- WiFi credentials not configured (`YOUR_WIFI_NAME`)
- WiFi connection failed

The script is designed to work **offline** - it will print data even without WiFi.

---

## 📝 Data Format

### **What ESP32 Sends:**

The script sends only the data backend needs:
```json
{
  "fill_level": 45.3,    // Percentage (0-100%) calculated from ultrasonic distance
  "methane": 175.0       // PPM from MQ-4 sensor
}
```

### **What's Printed (Full Sensor Data):**

```json
{
  "timestamp": 12345,
  "ultrasonic": {"distance_cm": 25.5},
  "weight": {"raw_value": 12345, "grams": 150.5},
  "mq4_methane": {"raw_adc": 850, "methane_ppm": 175.0},
  "mq135": {
    "raw_adc": 650,
    "co2_ppm": 775.0,
    "ammonia_ppm": 30.5,
    "air_quality": "MODERATE"
  }
}
```

---

## 🎛️ Configuration Options

### **Adjust Reading Interval:**

```python
SEND_INTERVAL = 5    # Change to any number (seconds)
```

### **Disable WiFi (Offline Mode):**

```python
WIFI_ENABLED = False    # Only prints data, doesn't send
```

### **Adjust Fill Level Calculation:**

```python
BIN_HEIGHT_CM = 50.0        # Total height of your bin
SENSOR_OFFSET_CM = 2.0      # Distance from sensor to bin top
```

---

## ✅ Connection Success Indicators

| Indicator | Location | Status |
|-----------|----------|--------|
| WiFi Connected | Thonny (silent) | Script runs without errors |
| Backend Receiving | Backend terminal | POST requests appearing |
| Data Updating | Frontend dashboard | A1_WET bin shows live data |
| Hardware Status | Dashboard | Shows 🟢 CONNECTED |

---

## 🚀 Quick Start Checklist

- [ ] Update WiFi credentials in `send_raw_data.py`
- [ ] Start backend: `python backend/app.py`
- [ ] Connect ESP32 to computer
- [ ] Run script in Thonny
- [ ] Check backend terminal for POST requests
- [ ] Open frontend dashboard
- [ ] Navigate to Location A1
- [ ] Verify A1_WET bin updates in real-time

---

## 🆘 Still Having Issues?

1. **Check Firewall:** Windows Firewall might block port 5000
   - Allow Python through firewall when prompted
   
2. **Check Network:** Ensure both devices can ping each other
   ```
   ping 10.62.147.196
   ```

3. **Check Backend Logs:** Look for error messages in backend terminal

4. **Test Endpoint Manually:** Use browser or curl:
   ```
   curl -X POST http://10.62.147.196:5000/api/locations/A1/bins/A1_WET/hardware \
        -H "Content-Type: application/json" \
        -d '{"fill_level": 50, "methane": 200}'
   ```

---

**Note:** The hardware connection is designed to be **optional**. The system works in simulation mode if hardware isn't connected, so you can develop and test without the physical sensors.
