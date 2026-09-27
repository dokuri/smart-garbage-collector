"""
Smart Waste Bin - MicroPython Setup Guide
==========================================

HOW TO USE THIS WITH THONNY IDE:

STEP 1: Install Thonny
----------------------
Download from: https://thonny.org/
Install with default settings

STEP 2: Flash MicroPython to ESP32 (First Time Only)
-----------------------------------------------------
1. Open Thonny
2. Go to: Tools → Options → Interpreter
3. Select: "MicroPython (ESP32)"
4. Click: "Install or update MicroPython"
5. Select your COM port
6. Click "Install"
7. Wait for flashing to complete

STEP 3: Connect ESP32
---------------------
1. Plug ESP32 into laptop via USB
2. In Thonny: Tools → Options → Interpreter
3. Select: "MicroPython (ESP32)"
4. Select Port: COM3 or COM4 (whichever shows up)
5. Click OK

STEP 4: Upload the Code
-----------------------
1. Open "main.py" in Thonny
2. Click: File → Save as
3. Select: "MicroPython device"
4. Save as: "main.py"
5. The code will run automatically on boot!

STEP 5: Run Manually (for testing)
----------------------------------
1. Open main.py from device
2. Click the green "Run" button
3. See output in Shell window below


WIRING DIAGRAM:
===============

ESP32 Pin    Sensor          Pin
---------    ------          ---
D18          HC-SR04         TRIG
D5           HC-SR04         ECHO
3.3V         HC-SR04         VCC
GND          HC-SR04         GND

D26          MQ-4            AO (Analog Out)
3.3V         MQ-4            VCC
GND          MQ-4            GND

D27          MQ-135          AO (Analog Out)
3.3V         MQ-135          VCC
GND          MQ-135          GND

D22          HX711           DT
D23          HX711           SCK
3.3V         HX711           VCC
GND          HX711           GND


EXPECTED OUTPUT:
================

╔════════════════════════════════════════════════════╗
║  🗑️  Smart Waste Bin - MicroPython                 ║
║  ESP32 Sensor Module                               ║
╚════════════════════════════════════════════════════╝

══════════════════════════════════════════════════
📊 SMART BIN SENSOR READINGS
══════════════════════════════════════════════════
📦 Fill Level:   45.2% [████░░░░░░] 🟢 OK
📏 Distance:     27.4 cm
💨 Methane:       180 ppm 🟢 OK
   (MQ-4 raw:    1250)
🌬️ Air Quality:  35.0/100 🟢 GOOD
   (MQ-135 raw:  920)
⚖️ Weight:        2.50 kg (2500 g)
══════════════════════════════════════════════════

📝 LOG: fill=45.2%, methane=180ppm, weight=2.50kg


TROUBLESHOOTING:
================

Problem: "Could not connect to ESP32"
Solution: 
- Check USB cable (use data cable, not charging-only)
- Install CP210x driver from Silicon Labs website
- Try different USB port

Problem: "Ultrasonic always shows 0 or -1"
Solution:
- Check TRIG and ECHO wires
- Make sure ECHO is on D5, TRIG is on D18
- VCC should be 3.3V (not 5V on some ESP32)

Problem: "MQ sensors show very high values"
Solution:
- MQ sensors need 24-48 hours of "burn-in" first use
- Let them warm up for at least 2-5 minutes
- Calibrate MQ4_CLEAN_AIR and MQ135_CLEAN_AIR values

Problem: "HX711 weight always 0"
Solution:
- Check DT and SCK wiring
- Make sure HX711 has stable 3.3V power
- Run hx711_tare() with no weight on scale
- Adjust HX711_SCALE_FACTOR for your load cell

"""
