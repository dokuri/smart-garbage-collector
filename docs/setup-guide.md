# 🚀 Complete Setup Guide - Smart Waste Management System

This guide covers everything from software setup to hardware integration.

---

## 📋 Table of Contents

1. [Software Requirements](#1-software-requirements)
2. [Backend Setup](#2-backend-setup)
3. [Frontend Setup](#3-frontend-setup)
4. [Running the System](#4-running-the-system)
5. [Hardware Setup (ESP32)](#5-hardware-setup-esp32)
6. [Testing & Verification](#6-testing--verification)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Software Requirements

### Must Have
| Software | Version | Download Link |
|----------|---------|---------------|
| Python | 3.8 or higher | [python.org/downloads](https://python.org/downloads) |
| Web Browser | Any modern | Chrome/Firefox/Edge |

### For Hardware (Optional)
| Software | Purpose | Download Link |
|----------|---------|---------------|
| Arduino IDE | Upload code to ESP32 | [arduino.cc/en/software](https://arduino.cc/en/software) |
| CP210x Driver | ESP32 USB driver | [Silicon Labs](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers) |

### Check Python Installation
Open Command Prompt and run:
```bash
python --version
```
Should show: `Python 3.8.x` or higher

---

## 2. Backend Setup

### Step 2.1: Open Terminal
```bash
cd "c:\Users\Pratik\Documents\VSCode\Smart Bin 2\backend"
```

### Step 2.2: Install Dependencies
```bash
pip install flask flask-cors
```

Or using requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 2.3: Verify Installation
```bash
python -c "import flask; print('Flask OK:', flask.__version__)"
```

---

## 3. Frontend Setup

The frontend is a single HTML file - no installation needed!

It uses:
- **Tailwind CSS** (loaded from CDN)
- **Vanilla JavaScript** (no framework)

---

## 4. Running the System

### Option A: One-Click Start (Easiest)

**Double-click:** `start_system.bat`

This will:
1. Start the backend server
2. Open the dashboard in your browser

### Option B: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```

You should see:
```
╔═══════════════════════════════════════════════════════════════╗
║   🌍 Smart City Waste Management System - Backend API         ║
║   Running on http://localhost:5000                            ║
╠═══════════════════════════════════════════════════════════════╣
║   ENVIRONMENTAL: WET 70% | DRY 30% (methane priority)         ║
║   METHANE: >500ppm = URGENT | >800ppm = EMERGENCY             ║
╚═══════════════════════════════════════════════════════════════╝
```

**Terminal 2 - Frontend (Optional):**
```bash
cd frontend
python -m http.server 8000
```

### Step 4.3: Open Dashboard

🌐 **URL:** http://localhost:5000

The backend serves the frontend automatically!

---

## 5. Hardware Setup (ESP32)

### 5.1 Required Components

| # | Component | Quantity | Purpose |
|---|-----------|----------|---------|
| 1 | ESP32 DevKit V1 | 1 | Main microcontroller |
| 2 | HC-SR04 Ultrasonic | 1 | Measure fill level (distance) |
| 3 | MQ-4 Gas Sensor | 1 | Detect methane gas |
| 4 | MQ-135 Gas Sensor | 1 | Air quality (optional) |
| 5 | Breadboard | 1 | For connections |
| 6 | Jumper Wires (M-M) | 15+ | Connections |
| 7 | Micro USB Cable | 1 | Power & programming |

### 5.2 Wiring Connections

```
┌────────────────────────────────────────────────────────────────┐
│                        WIRING DIAGRAM                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   ESP32 DevKit V1                                              │
│   ┌──────────────┐                                             │
│   │              │                                             │
│   │  3V3  ●──────┼───────┬─────────┬─────────┐                │
│   │              │       │         │         │                │
│   │  GND  ●──────┼───┬───┼────┬────┼────┬────┼────┐           │
│   │              │   │   │    │    │    │    │    │           │
│   │  GPIO4 ●─────┼───┼───┼────┼────┼────┼────┼────┼── TRIG    │
│   │              │   │   │    │    │    │    │    │           │
│   │  GPIO5 ●─────┼───┼───┼────┼────┼────┼────┼────┼── ECHO    │
│   │              │   │   │    │    │    │    │    │           │
│   │  GPIO34 ●────┼───┼───┼────┼────┼────┼────┼────┼── MQ-4 AO │
│   │              │   │   │    │    │    │    │    │           │
│   │  GPIO35 ●────┼───┼───┼────┼────┼────┼────┼────┼── MQ135 AO│
│   │              │   │   │    │    │    │    │    │           │
│   └──────────────┘   │   │    │    │    │    │    │           │
│                      │   │    │    │    │    │    │           │
│   ┌──────────────┐   │   │    │    │    │    │    │           │
│   │   HC-SR04    │   │   │    │    │    │    │    │           │
│   │  ┌────────┐  │   │   │    │    │    │    │    │           │
│   │  │VCC     │──┼───┼───┘    │    │    │    │    │           │
│   │  │TRIG    │──┼───┼────────┼────┼────┼────┼────┘ (GPIO4)   │
│   │  │ECHO    │──┼───┼────────┼────┼────┼────┘ (GPIO5)        │
│   │  │GND     │──┼───┘        │    │    │                     │
│   │  └────────┘  │            │    │    │                     │
│   └──────────────┘            │    │    │                     │
│                               │    │    │                     │
│   ┌──────────────┐            │    │    │                     │
│   │    MQ-4      │            │    │    │                     │
│   │  ┌────────┐  │            │    │    │                     │
│   │  │VCC     │──┼────────────┘    │    │                     │
│   │  │AO      │──┼─────────────────┼────┼────── (GPIO34)      │
│   │  │DO      │  │ (not used)      │    │                     │
│   │  │GND     │──┼─────────────────┘    │                     │
│   │  └────────┘  │                      │                     │
│   └──────────────┘                      │                     │
│                                         │                     │
│   ┌──────────────┐                      │                     │
│   │   MQ-135     │                      │                     │
│   │  ┌────────┐  │                      │                     │
│   │  │VCC     │──┼──────────────────────┤                     │
│   │  │AO      │──┼──────────────────────┼────── (GPIO35)      │
│   │  │DO      │  │ (not used)           │                     │
│   │  │GND     │──┼──────────────────────┘                     │
│   │  └────────┘  │                                            │
│   └──────────────┘                                            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 5.3 Connection Table

| ESP32 Pin | Component | Pin | Wire Color (Suggested) |
|-----------|-----------|-----|------------------------|
| 3V3 | HC-SR04 | VCC | 🔴 Red |
| GND | HC-SR04 | GND | ⚫ Black |
| GPIO4 | HC-SR04 | TRIG | 🟡 Yellow |
| GPIO5 | HC-SR04 | ECHO | 🟢 Green |
| 3V3 | MQ-4 | VCC | 🔴 Red |
| GND | MQ-4 | GND | ⚫ Black |
| GPIO34 | MQ-4 | AO | 🔵 Blue |
| 3V3 | MQ-135 | VCC | 🔴 Red |
| GND | MQ-135 | GND | ⚫ Black |
| GPIO35 | MQ-135 | AO | 🟣 Purple |

### 5.4 Install Arduino IDE & ESP32 Support

1. **Download Arduino IDE:** https://arduino.cc/en/software

2. **Add ESP32 Board URL:**
   - Open Arduino IDE
   - Go to: **File → Preferences**
   - In "Additional Board Manager URLs" add:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
   - Click OK

3. **Install ESP32 Board:**
   - Go to: **Tools → Board → Boards Manager**
   - Search: "ESP32"
   - Install: "ESP32 by Espressif Systems"

4. **Install USB Driver (if needed):**
   - If ESP32 not detected, install CP210x driver
   - Download from: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

### 5.5 Configure & Upload Code

1. **Open the code:**
   - File → Open → `hardware/esp32_sensor.ino`

2. **Find your laptop's IP address:**
   ```bash
   # In Command Prompt
   ipconfig
   ```
   Look for **IPv4 Address** under your WiFi adapter (e.g., `192.168.1.50`)

3. **Edit WiFi settings** (lines 34-40 in esp32_sensor.ino):
   ```cpp
   // ⚠️ UPDATE THESE VALUES
   const char* WIFI_SSID = "YourWiFiName";          // Your WiFi network
   const char* WIFI_PASSWORD = "YourWiFiPassword";  // Your WiFi password
   
   // Update with YOUR laptop's IP
   const char* BACKEND_URL = "http://192.168.1.50:5000/api/locations/A1/bins/A1_WET/hardware";
   ```

4. **Select Board & Port:**
   - Tools → Board → **ESP32 Dev Module**
   - Tools → Port → **COMx** (your ESP32 port)

5. **Upload:**
   - Click the Upload button (→)
   - Wait for "Done uploading"

6. **Open Serial Monitor:**
   - Tools → Serial Monitor
   - Set baud rate: **115200**
   - You should see:
   ```
   ╔════════════════════════════════════════════════╗
   ║  Smart Waste System - ESP32 Sensor Module      ║
   ╚════════════════════════════════════════════════╝
   
   Connecting to WiFi: YourWiFiName
   ✅ Connected! IP: 192.168.1.105
   
   📊 Sensor Reading:
      Fill Level: 35.2%
      Methane: 180 ppm
   ✅ Data sent successfully!
   ```

### 5.6 Verify Hardware Connection

1. **Check Dashboard:**
   - Open http://localhost:5000
   - Look for **"🔌 HW Connected"** badge in header
   - Click on location **A1** - it should show real sensor data

2. **Test Sensors:**
   - Wave hand over ultrasonic → Fill level should change
   - Hold lighter near MQ-4 (careful!) → Methane should spike

---

## 6. Testing & Verification

### 6.1 Test Backend API

Open in browser:
```
http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "success",
  "message": "Smart Waste System API is running",
  "locations_count": 8,
  "bins_count": 16,
  "hardware_connected": true
}
```

### 6.2 Test Frontend

1. Click **"🎲 Demo Scenario"** - should create critical bins
2. Click **"⚡ Optimize Route"** - should show best route
3. Click a location → Add waste → Should update

### 6.3 Test Hardware

1. Check Serial Monitor for readings
2. Check dashboard for "HW Connected" status
3. A1_WET bin should show real-time updates

---

## 7. Troubleshooting

### Backend Issues

| Problem | Solution |
|---------|----------|
| `python: command not found` | Install Python, add to PATH |
| `ModuleNotFoundError: flask` | Run: `pip install flask flask-cors` |
| Port 5000 in use | Kill other process or change port in app.py |

### Frontend Issues

| Problem | Solution |
|---------|----------|
| "Backend Offline" | Make sure backend is running |
| Page not loading | Clear browser cache, try incognito |

### Hardware Issues

| Problem | Solution |
|---------|----------|
| ESP32 not detected | Install CP210x USB driver |
| "WiFi connection failed" | Check SSID/password spelling |
| "HTTP POST failed" | Check laptop IP address in code |
| Sensor readings stuck at 0 | Check wiring connections |
| Fill level always 0% | HC-SR04 wiring may be wrong |
| Methane always 0 | MQ-4 needs 24-48h burn-in time |

### Network Issues

| Problem | Solution |
|---------|----------|
| Can't find laptop IP | Run `ipconfig` in Command Prompt |
| ESP32 can't reach backend | Both must be on same WiFi network |
| Firewall blocking | Allow Python through Windows Firewall |

---

## 🎉 You're Ready!

Your Smart Waste Management System is now set up with:
- ✅ Backend API running
- ✅ Frontend dashboard accessible
- ✅ (Optional) Hardware sending real sensor data

**Next Steps:**
1. Explore the dashboard
2. Try the demo scenario
3. Click "Optimize Route" to see the AI in action
4. Show off at your exhibition! 🏆

---

## 📞 Quick Reference

| Component | URL/Port |
|-----------|----------|
| Backend API | http://localhost:5000 |
| Frontend Dashboard | http://localhost:5000 |
| API Health Check | http://localhost:5000/api/health |
| API Docs | See `docs/api-reference.md` |
