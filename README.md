# 🌍 Smart City Waste Management System

An **IoT + AI-based Smart Waste Management System** that monitors roadside bins in real-time using ESP32 sensors, predicts fill levels, detects methane gas emissions, and optimizes collection routes using an environmentally-conscious algorithm.

> **🏆 Project Focus:** Prioritizes **methane detection** (greenhouse gas 25× more potent than CO₂) over simple fill levels, making this an **environmentally-aware** waste management solution.

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **8 Smart Locations** | Each with 2 bins (WET + DRY) = 16 total bins |
| **Real-time Monitoring** | Live dashboard with interactive city map |
| **Two Bin Types** | 💧 WET (biodegradable) + 📦 DRY (recyclables) |
| **Methane Priority** | Environmental algorithm prioritizes greenhouse gas |
| **Route Optimization** | Greedy Nearest Neighbor + 2-Opt algorithm |
| **Hardware Integration** | ESP32 + Ultrasonic + MQ-4 (methane) sensors |
| **Simulation Mode** | Full demo without hardware |

---

## 📁 Project Structure

```
Smart Bin 2/
├── backend/
│   ├── app.py              # Flask API server (main backend)
│   └── requirements.txt    # Python dependencies
├── frontend/
│   └── index.html          # Dashboard (Tailwind CSS)
├── hardware/
│   ├── esp32_sensor.ino    # Arduino code for ESP32
│   └── sensor_config.h     # Hardware configuration
├── docs/
│   ├── setup-guide.md      # Detailed setup instructions
│   └── api-reference.md    # Complete API documentation
├── start_backend.bat       # One-click backend start
├── start_frontend.bat      # One-click frontend start
├── start_system.bat        # Start everything
└── README.md               # This file
```

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- ✅ Python 3.8+ installed ([Download](https://python.org/downloads))
- ✅ Web browser (Chrome/Firefox/Edge)

### Step 1: Install Dependencies (First Time Only)

```bash
cd backend
pip install flask flask-cors
```

### Step 2: Start the System

**Option A: One-Click (Windows)**
```
Double-click: start_system.bat
```

**Option B: Manual Start**

Terminal 1 (Backend):
```bash
cd backend
python app.py
```

Terminal 2 (Frontend):
```bash
cd frontend
python -m http.server 8000
```

### Step 3: Open Dashboard

🌐 **Open in browser:** http://localhost:5000

*(Or http://localhost:8000 if using separate frontend server)*

---

## 🎮 How to Use the Dashboard

### Basic Controls

| Button | Action |
|--------|--------|
| 🎲 **Demo Scenario** | Creates critical bins for testing |
| 🚛 **Collect All Urgent** | Empties all urgent bins |
| 🔄 **Refresh** | Reload data from backend |
| ⚡ **Optimize Route** | Find best collection route |

### Using the System

1. **Click a location** on the map to select it
2. **Choose WET or DRY bin** using the toggle
3. **Add waste** using the panel (select type + quantity)
4. **Advance time** (+1h or +6h) to see decomposition
5. **Click Optimize Route** to find the best path

### Understanding Colors

| Color | Status | Risk Score | Action |
|-------|--------|------------|--------|
| 🟢 Green | Normal | 0-40 | Routine collection |
| 🟡 Yellow | Warning | 40-70 | Collect within 24h |
| 🔴 Red | Urgent | 70-100 | Collect within 2h |

---

## 🔧 Hardware Setup (Optional)

### Required Components

| Component | Purpose | Approx. Cost |
|-----------|---------|--------------|
| ESP32 DevKit V1 | Microcontroller | ₹400-500 |
| HC-SR04 | Ultrasonic (fill level) | ₹50-80 |
| MQ-4 | Methane gas sensor | ₹150-200 |
| MQ-135 | Air quality sensor | ₹150-200 |
| Jumper wires | Connections | ₹50 |
| Breadboard | Prototyping | ₹80 |

**Total: ~₹900-1100**

### Wiring Diagram

```
ESP32 DevKit V1
┌─────────────────────────────────────┐
│                                     │
│  3.3V ──────┬───────┬───────┐      │
│             │       │       │      │
│         ┌───┴───┐ ┌─┴──┐ ┌──┴──┐   │
│         │HC-SR04│ │MQ-4│ │MQ135│   │
│         │  VCC  │ │VCC │ │ VCC │   │
│         │  Trig │ │ AO │ │ AO  │   │
│         │  Echo │ │GND │ │ GND │   │
│         │  GND  │ └────┘ └─────┘   │
│         └───────┘                   │
│                                     │
│  GPIO4 ────── Trig (HC-SR04)       │
│  GPIO5 ────── Echo (HC-SR04)       │
│  GPIO34 ───── AO (MQ-4 Methane)    │
│  GPIO35 ───── AO (MQ-135 Air)      │
│  GND ────────┴───────┴───────┘     │
│                                     │
└─────────────────────────────────────┘
```

### Connections Table

| ESP32 Pin | Sensor | Pin |
|-----------|--------|-----|
| 3.3V | HC-SR04 | VCC |
| GPIO4 | HC-SR04 | Trig |
| GPIO5 | HC-SR04 | Echo |
| GND | HC-SR04 | GND |
| 3.3V | MQ-4 | VCC |
| GPIO34 | MQ-4 | AO (Analog Out) |
| GND | MQ-4 | GND |
| 3.3V | MQ-135 | VCC |
| GPIO35 | MQ-135 | AO (Analog Out) |
| GND | MQ-135 | GND |

### Upload Code to ESP32

1. **Install Arduino IDE** from [arduino.cc](https://arduino.cc/en/software)

2. **Add ESP32 Board Support:**
   - Go to: File → Preferences
   - Add to "Additional Board URLs":
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
   - Go to: Tools → Board → Boards Manager
   - Search "ESP32" and install

3. **Open the code:**
   - File → Open → `hardware/esp32_sensor.ino`

4. **Configure WiFi (IMPORTANT):**
   - Edit lines 34-35 in `esp32_sensor.ino`:
     ```cpp
     const char* WIFI_SSID = "YOUR_WIFI_NAME";
     const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
     ```

5. **Find your laptop's IP address:**
   - Open Command Prompt
   - Type: `ipconfig`
   - Look for "IPv4 Address" (e.g., `192.168.1.50`)

6. **Update Backend URL (line 40):**
   ```cpp
   const char* BACKEND_URL = "http://192.168.1.50:5000/api/locations/A1/bins/A1_WET/hardware";
   ```

7. **Upload:**
   - Select Board: Tools → Board → ESP32 Dev Module
   - Select Port: Tools → Port → COMx
   - Click Upload (→)

8. **Verify:**
   - Open Serial Monitor (115200 baud)
   - Should see sensor readings being sent

---

## 🌱 Environmental Algorithm Explained

### Why Methane Matters

| Gas | Global Warming Potential | In This System |
|-----|-------------------------|----------------|
| CO₂ | 1× (baseline) | Not measured |
| **CH₄ (Methane)** | **25× more potent** | **Primary focus** |

**Food waste in landfills generates methane → Climate change**

### Risk Calculation

**WET Bins (Biodegradable):**
```
Risk = (Methane × 50%) + (Decomposition × 30%) + (Fill × 20%)
```

**DRY Bins (Plastic/Paper):**
```
Risk = min(75, Fill × 70% + Weight × 30%)
       ↑ Capped at 75 (plastic doesn't harm climate like methane)
```

**Location Risk:**
```
Location = (WET × 70%) + (DRY × 30%)
           ↑ Environmental priority
```

### Route Optimization

Uses **Greedy Nearest Neighbor + 2-Opt** algorithm:

1. Calculate priority for each location
2. Sort by efficiency (priority ÷ distance)
3. Critical methane (>800ppm) locations FIRST
4. Apply 2-Opt swaps to reduce travel distance

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Check if API is running |
| `/api/locations` | GET | Get all 8 locations |
| `/api/locations/{id}` | GET | Get specific location |
| `/api/locations/{id}/bins/{bin}/add-waste` | POST | Add waste to bin |
| `/api/locations/{id}/bins/{bin}/empty` | POST | Empty a bin |
| `/api/locations/{id}/collect` | POST | Collect both bins |
| `/api/routes/optimize` | GET | Get optimized route |
| `/api/simulation/advance` | POST | Advance time by hours |
| `/api/simulation/reset` | POST | Reset simulation |
| `/api/simulation/demo` | POST | Generate demo scenario |

See [docs/api-reference.md](docs/api-reference.md) for complete documentation.

---

## 🎤 Exhibition Explanation Script

### 30-Second Pitch
> "This is a **Smart Waste Management System** that uses IoT sensors to monitor bins in real-time. What makes it unique is that it **prioritizes methane detection** - a greenhouse gas 25 times more potent than CO₂. When food waste decomposes, it releases methane. Our system detects this and **prioritizes collection of biodegradable waste** to reduce climate impact. The AI optimizes truck routes to minimize fuel consumption while ensuring critical bins are collected first."

### Key Points to Highlight

1. **Environmental Focus:**
   - "We detect methane, which is 25× worse for climate than CO₂"
   - "Food waste is prioritized over plastic because it causes more environmental harm"

2. **Real Hardware:**
   - "This ESP32 has an ultrasonic sensor for fill level and MQ-4 for methane"
   - "The sensor sends data every 10 seconds to our backend"

3. **AI Optimization:**
   - "Our algorithm considers 5 factors: risk, fill, methane, distance, and time"
   - "It uses Greedy Nearest Neighbor with 2-Opt improvement"

4. **Real-World Impact:**
   - "Cities like Pune could reduce emissions by prioritizing wet waste"
   - "Route optimization saves fuel and reduces truck emissions"

### Demo Flow (2 Minutes)

1. **Show dashboard** - "Here's our city map with 8 locations"
2. **Click Demo Scenario** - "This simulates critical bins"
3. **Point to colors** - "Red means urgent, especially for methane"
4. **Click Optimize Route** - "Watch how it prioritizes high-methane locations"
5. **Show hardware** - "This sensor sends real data to the system"
6. **Explain impact** - "This helps cities fight climate change"

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend won't start | Check Python is installed: `python --version` |
| "Module not found" | Run: `pip install flask flask-cors` |
| Frontend shows "Backend Offline" | Make sure backend is running on port 5000 |
| ESP32 not connecting | Check WiFi credentials and IP address |
| Sensor readings stuck | Check wiring connections |

---

## 👨‍💻 Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python Flask |
| Frontend | HTML + Tailwind CSS + JavaScript |
| Hardware | ESP32 + Arduino |
| Sensors | HC-SR04, MQ-4, MQ-135 |
| Algorithm | Greedy Nearest Neighbor + 2-Opt |

---

## 📄 License

This project is created for educational purposes.

---

## 🙏 Acknowledgments

- Smart City Mission India
- Environmental sustainability goals
- Open-source community

---

**Made with ❤️ for a cleaner, greener future 🌱**
