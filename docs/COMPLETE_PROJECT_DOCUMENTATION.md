# 🌍 Smart City Waste Management System
## Complete Technical Documentation

---

# Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Frontend Documentation](#4-frontend-documentation)
5. [Backend Documentation](#5-backend-documentation)
6. [Hardware Documentation](#6-hardware-documentation)
7. [Algorithms & Logic](#7-algorithms--logic)
8. [Data Flow & Communication](#8-data-flow--communication)
9. [API Reference](#9-api-reference)
10. [Project Setup Guide](#10-project-setup-guide)
11. [Troubleshooting Guide](#11-troubleshooting-guide)
12. [Common Problems & Solutions](#12-common-problems--solutions)
13. [File Structure Reference](#13-file-structure-reference)

---

# 1. Project Overview

## 1.1 What is This Project?

The **Smart City Waste Management System** is an IoT + AI-based solution for monitoring and managing roadside waste bins in real-time. It uses ESP32 microcontrollers with multiple sensors to collect data from physical bins, processes this data through a Flask backend, and displays it on an interactive web dashboard.

## 1.2 Key Problem Solved

Traditional waste collection follows fixed schedules, leading to:
- **Overflowing bins** (collected too late)
- **Wasted trips** (bins collected when not full)
- **Environmental hazards** (methane emissions from decomposing organic waste)
- **Inefficient routes** (no data-driven optimization)

This system solves all these problems with real-time monitoring and intelligent route optimization.

## 1.3 Core Features

| Feature | Description |
|---------|-------------|
| **8 Smart Locations** | Each location has 2 bins (WET + DRY) = 16 total bins |
| **Real-time Monitoring** | Live dashboard with interactive SVG city map |
| **Dual Bin Types** | 💧 WET (biodegradable/organic) + 📦 DRY (recyclables/plastic) |
| **Methane Detection** | MQ-4 sensor detects dangerous methane gas from decomposing waste |
| **Environmental Priority** | Algorithm prioritizes methane (25× more potent than CO₂) |
| **Route Optimization** | Greedy Nearest Neighbor + 2-Opt algorithm for efficient collection |
| **Hardware Integration** | ESP32 + Ultrasonic + Gas sensors send real data |
| **Simulation Mode** | Full functionality without hardware for demos |

## 1.4 Environmental Focus

**Why Methane Matters:**
- Methane (CH₄) is **25 times more potent** as a greenhouse gas than CO₂
- Decomposing organic waste produces methane
- This system **prioritizes methane detection** over simple fill levels
- WET bins (organic waste) get **70% weight** in risk calculations
- DRY bins (plastic) get **30% weight** (sanitation concern, not climate emergency)

---

# 2. System Architecture

## 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SMART WASTE MANAGEMENT SYSTEM                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐  │
│  │    HARDWARE      │      │     BACKEND      │      │    FRONTEND      │  │
│  │    (ESP32)       │      │   (Flask API)    │      │   (HTML/JS)      │  │
│  │                  │      │                  │      │                  │  │
│  │  ┌────────────┐  │      │  ┌────────────┐  │      │  ┌────────────┐  │  │
│  │  │ Ultrasonic │  │      │  │ REST API   │  │      │  │ Dashboard  │  │  │
│  │  │ HC-SR04    │  │─WiFi─┼─▶│ Endpoints  │◀─┼─HTTP─┼─▶│ SVG Map    │  │  │
│  │  └────────────┘  │ POST │  └────────────┘  │ GET  │  └────────────┘  │  │
│  │                  │      │        │         │      │        │         │  │
│  │  ┌────────────┐  │      │        ▼         │      │        ▼         │  │
│  │  │ MQ-4       │  │      │  ┌────────────┐  │      │  ┌────────────┐  │  │
│  │  │ Methane    │  │      │  │ In-Memory  │  │      │  │ Real-time  │  │  │
│  │  └────────────┘  │      │  │ Database   │  │      │  │ Updates    │  │  │
│  │                  │      │  └────────────┘  │      │  └────────────┘  │  │
│  │  ┌────────────┐  │      │        │         │      │        │         │  │
│  │  │ MQ-135     │  │      │        ▼         │      │        ▼         │  │
│  │  │ Air Qual.  │  │      │  ┌────────────┐  │      │  ┌────────────┐  │  │
│  │  └────────────┘  │      │  │ Risk Calc  │  │      │  │ Route Viz  │  │  │
│  │                  │      │  │ Algorithms │  │      │  │ Animation  │  │  │
│  │  ┌────────────┐  │      │  └────────────┘  │      │  └────────────┘  │  │
│  │  │ HX711      │  │      │        │         │      │                  │  │
│  │  │ Weight     │  │      │        ▼         │      │                  │  │
│  │  └────────────┘  │      │  ┌────────────┐  │      │                  │  │
│  │                  │      │  │ Route      │  │      │                  │  │
│  │                  │      │  │ Optimizer  │  │      │                  │  │
│  └──────────────────┘      │  └────────────┘  │      └──────────────────┘  │
│                            └──────────────────┘                              │
│                                                                              │
│  Location: A1 only has     All 16 bins data    Displays all 8 locations    │
│  real hardware. Others     stored in memory    with interactive controls    │
│  are simulated.                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2.2 Component Interaction Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA FLOW DIAGRAM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│    HARDWARE                  BACKEND                    FRONTEND             │
│    ────────                  ───────                    ────────             │
│                                                                              │
│    ESP32 Sensors             Flask Server              Web Browser           │
│         │                         │                         │                │
│         │                         │                         │                │
│    ┌────▼────┐                    │                         │                │
│    │ Read    │                    │                         │                │
│    │ Sensors │                    │                         │                │
│    └────┬────┘                    │                         │                │
│         │                         │                         │                │
│         │ POST /api/locations/    │                         │                │
│         │ A1/bins/A1_WET/hardware │                         │                │
│         ├────────────────────────►│                         │                │
│         │ {fill_level, methane}   │                         │                │
│         │                    ┌────▼────┐                    │                │
│         │                    │ Update  │                    │                │
│         │                    │ A1_WET  │                    │                │
│         │                    │ Data    │                    │                │
│         │                    └────┬────┘                    │                │
│         │                         │                         │                │
│         │                         │                    ┌────▼────┐           │
│         │                         │                    │ GET     │           │
│         │                         │                    │/api/    │           │
│         │                         │◄───────────────────┤locations│           │
│         │                         │                    └────┬────┘           │
│         │                    ┌────▼────┐                    │                │
│         │                    │ Return  │                    │                │
│         │                    │ All 16  ├───────────────────►│                │
│         │                    │ Bins    │                    │                │
│         │                    └─────────┘              ┌─────▼─────┐          │
│         │                                             │ Render    │          │
│         │                                             │ Dashboard │          │
│         │                                             │ Update UI │          │
│         │                                             └───────────┘          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2.3 Location Model

```
CITY MODEL: 8 Locations × 2 Bins Each = 16 Total Bins

┌────────────────────────────────────────────────────────────────────────────┐
│                              ROUTES                                         │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ROUTE A (Blue)              ROUTE B (Green)           ROUTE C (Orange)  │
│    ─────────────────           ─────────────────         ─────────────────  │
│    Central District            Residential Zone          Market District    │
│    Distance: 8.5 km            Distance: 12.5 km         Distance: 6.0 km  │
│                                                                             │
│    ┌─────────┐                 ┌─────────┐               ┌─────────┐       │
│    │   A1    │                 │   B1    │               │   C1    │       │
│    │ Koregaon│                 │ Aundh   │               │ Deccan  │       │
│    │  Park   │                 │ IT Park │               │Gymkhana │       │
│    │ [⚡HW]  │                 └─────────┘               └─────────┘       │
│    └─────────┘                                                              │
│                                 ┌─────────┐               ┌─────────┐       │
│    ┌─────────┐                 │   B2    │               │   C2    │       │
│    │   A2    │                 │ Baner   │               │Shivaji- │       │
│    │ MG Road │                 │ Hills   │               │ nagar   │       │
│    │Junction │                 └─────────┘               └─────────┘       │
│    └─────────┘                                                              │
│                                 ┌─────────┐                                 │
│    ┌─────────┐                 │   B3    │                                 │
│    │   A3    │                 │ Pashan  │                                 │
│    │ FC Road │                 │Lake View│                                 │
│    │  Plaza  │                 └─────────┘                                 │
│    └─────────┘                                                              │
│                                                                             │
│    [⚡HW] = A1_WET is the ONLY real hardware bin                           │
│            All other 15 bins are simulated                                 │
└────────────────────────────────────────────────────────────────────────────┘

EACH LOCATION HAS:
┌───────────────────────────────────────┐
│            LOCATION X                  │
├───────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐     │
│  │  💧 WET BIN │  │  📦 DRY BIN │     │
│  ├─────────────┤  ├─────────────┤     │
│  │ fill_level  │  │ fill_level  │     │
│  │ methane     │  │ weight      │     │
│  │ decomposition│ │ waste_type  │     │
│  │ waste_comp  │  │             │     │
│  └─────────────┘  └─────────────┘     │
│                                        │
│  WET: Biodegradable (food, organic)   │
│  DRY: Recyclables (paper, plastic)    │
└───────────────────────────────────────┘
```

---

# 3. Technology Stack

## 3.1 Complete Tech Stack Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TECHNOLOGY STACK                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                           FRONTEND                                    │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  Language:     JavaScript (ES6+)                                      │   │
│  │  UI Framework: Tailwind CSS (via CDN)                                │   │
│  │  Graphics:     SVG (inline, programmatic)                            │   │
│  │  HTTP Client:  Fetch API (native browser)                            │   │
│  │  State:        JavaScript objects (in-memory)                        │   │
│  │  File:         Single index.html (1394 lines)                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                           BACKEND                                     │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  Language:     Python 3.8+                                            │   │
│  │  Framework:    Flask 3.0.0                                           │   │
│  │  CORS:         Flask-CORS 4.0.0                                      │   │
│  │  Database:     In-memory Python dictionaries                         │   │
│  │  Algorithms:   Pure Python implementation                            │   │
│  │  File:         app.py (1245 lines)                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                           HARDWARE                                    │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  Microcontroller: ESP32 DevKit V1                                    │   │
│  │  Languages:       Arduino C++ OR MicroPython                         │   │
│  │  Sensors:                                                            │   │
│  │    • HC-SR04 Ultrasonic (fill level)                                │   │
│  │    • MQ-4 Gas Sensor (methane detection)                            │   │
│  │    • MQ-135 Gas Sensor (air quality)                                │   │
│  │    • HX711 + Load Cell (weight measurement)                         │   │
│  │  Communication: WiFi (HTTP POST to Flask API)                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         COMMUNICATION                                 │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  Protocol:     HTTP/1.1 REST API                                     │   │
│  │  Data Format:  JSON                                                  │   │
│  │  CORS:         Enabled for cross-origin requests                     │   │
│  │  Ports:        Backend: 5000, Frontend: 8000 (optional)             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 3.2 Dependencies

### Backend (Python)
```
flask==3.0.0          # Web framework for REST API
flask-cors==4.0.0     # Cross-Origin Resource Sharing
python-dateutil==2.8.2 # Date/time utilities
```

### Frontend (CDN)
```html
<script src="https://cdn.tailwindcss.com"></script>  <!-- Utility CSS -->
```

### Hardware (Arduino)
```cpp
#include <WiFi.h>          // ESP32 WiFi connectivity
#include <HTTPClient.h>    // HTTP POST requests
#include <ArduinoJson.h>   // JSON serialization
```

### Hardware (MicroPython)
```python
import network           # WiFi module
import urequests         # HTTP requests
import ujson             # JSON handling
from machine import Pin, ADC  # GPIO and ADC control
```

---

# 4. Frontend Documentation

## 4.1 File Structure

```
frontend/
└── index.html    # Single-file application (HTML + CSS + JavaScript)
    ├── HTML Structure (lines 1-310)
    ├── CSS Styles (lines 7-42)
    └── JavaScript Logic (lines 312-1394)
```

## 4.2 UI Components

### 4.2.1 Header Section
```
┌─────────────────────────────────────────────────────────────────┐
│  ♻️ Smart City Waste Management                                 │
│  [🟢 Backend Online] [⚡ ESP32 Connected]                       │
│  Real-time IoT monitoring • 8 Locations × 2 Bins • ML Route    │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2.2 Statistics Bar
```
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│Locations │Total Bins│🔴 Urgent │🟡 Warning│📊 Avg Fill│⏱️ Sim Time│
│    8     │    16    │    0     │    0     │    0%    │    0h    │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

### 4.2.3 Quick Actions
```
┌──────────────────────────────────────────────────────────────────┐
│ [🎲 Demo Scenario] [🚛 Collect All Urgent] [🔄 Refresh] [🔔 Alerts] │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2.4 City Map (SVG)
```
┌─────────────────────────────────────────────────────────────────┐
│                    📍 Route A: Central District                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  🌳 Park                                                   │  │
│  │              🛒 Mall    🏥 Hospital    🏢 Office          │  │
│  │  ════════════════════════════════════════════════════     │  │
│  │       [A1]           [A2]           [A3]                  │  │
│  │        ⚡                                                  │  │
│  │  🏠 Homes        🏬 Apartments                            │  │
│  │       [B1]           [B2]           [B3]                  │  │
│  │                                                           │  │
│  │  🚛 DEPOT        🏪 Market     🛍️ Shops    🏭 DUMP       │  │
│  │  (START)            [C1]           [C2]        (END)      │  │
│  │                                                           │  │
│  │  Legend: [🟢 Safe] [🟡 Warning] [🔴 Critical]            │  │
│  └───────────────────────────────────────────────────────────┘  │
│  [🏢 Route A] [🏠 Route B] [🏪 Route C]                         │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2.5 Control Panel (Right Side)
```
┌─────────────────────────┐
│  ⏰ Simulation Time     │
│  ┌─────────────────┐    │
│  │       0h        │    │
│  │   Elapsed Time  │    │
│  └─────────────────┘    │
│  [⏱️ +1 Hour        ]   │
│  [⏱️ +6 Hours       ]   │
│  [🔄 Reset Simulation]  │
├─────────────────────────┤
│  📍 Location Details    │
│  (Click location to     │
│   view bin data)        │
├─────────────────────────┤
│  ➕ Add Waste Panel     │
│  [💧 WET] [📦 DRY]      │
│  [Waste Type: Food ▼]   │
│  [Quantity: 5kg ───]    │
│  [➕ Add Waste to Bin]  │
│  [🗑️ Empty Selected Bin]│
│  [🚛 Collect Both Bins] │
└─────────────────────────┘
```

## 4.3 JavaScript Architecture

### 4.3.1 Configuration Constants

```javascript
// API Configuration
const API_BASE = 'http://localhost:5000/api';

// Route Information
const ROUTE_INFO = {
    'A': { name: 'Route A: Central District', road: 'Main Street & Park Avenue', color: '#3B82F6' },
    'B': { name: 'Route B: Residential Zone', road: 'Oak Road & Elm Street', color: '#10B981' },
    'C': { name: 'Route C: Market District', road: 'Market Street & Central Plaza', color: '#F59E0B' }
};

// Location Positions on SVG Map (x, y coordinates)
const LOCATION_POSITIONS = {
    'A1': { x: 180, y: 120 }, 'A2': { x: 375, y: 100 }, 'A3': { x: 575, y: 130 },
    'B1': { x: 175, y: 320 }, 'B2': { x: 375, y: 350 }, 'B3': { x: 575, y: 320 },
    'C1': { x: 280, y: 520 }, 'C2': { x: 520, y: 550 }
};

// Waste Type Properties
const WASTE_TYPES = {
    food: { density: 0.8, decomposition_rate: 0.15, methane_multiplier: 2.0 },
    paper: { density: 0.3, decomposition_rate: 0.08, methane_multiplier: 0.5 },
    plastic: { density: 1.2, decomposition_rate: 0.02, methane_multiplier: 0.3 },
    organic: { density: 0.6, decomposition_rate: 0.20, methane_multiplier: 2.5 }
};
```

### 4.3.2 State Management

```javascript
// Application State (Global Variables)
let allLocations = {};           // All location data from backend
let selectedRoute = 'A';          // Currently selected route
let selectedLocation = null;      // Currently selected location
let selectedBinType = 'wet';      // Selected bin type for waste addition
let simulationTime = 0;           // Current simulation hour
let backendAvailable = false;     // Backend connection status
let hardwareConnected = false;    // ESP32 connection status
let showAlertsPanel = false;      // Alerts panel visibility
let activeRoutePath = null;       // Currently displayed route
```

### 4.3.3 Core Functions

```javascript
// Backend Health Check
async function checkBackend() {
    // Checks if backend is running
    // Updates status indicators
    // Returns: boolean
}

// Data Fetching
async function fetchLocations() {
    // Fetches all location data from backend
    // Falls back to mock data if offline
    // Updates UI after fetch
}

// Time Simulation
async function advanceTime(hours) {
    // Advances simulation by N hours
    // Triggers decomposition and methane generation
    // Updates all bin states
}

// Waste Management
async function addWaste() {
    // Adds waste to selected bin
    // Validates bin capacity
    // Checks waste type compatibility
}

// Route Optimization
async function optimizeRoute() {
    // Calls backend optimization API
    // Displays best route with explanation
    // Animates collection path
}

// Risk Calculations (Local Fallback)
function calculateBinRisk(bin) {
    // Calculates risk score for single bin
    // Returns: 0-100 score
}

function calculateLocationRisk(location) {
    // Returns MAX of WET and DRY bin risks
    // Used for urgent/warning classification
}
```

### 4.3.4 SVG Map Rendering

```javascript
function drawLocations() {
    // Creates SVG elements for each location
    // Applies risk-based coloring
    // Adds hardware indicator for A1
    // Handles click events for selection
}

function drawRoutePath(routeId, collectionOrder) {
    // Draws animated route line
    // Shows truck animation along path
    // Adds START/END labels
    // Numbers collection stops
}
```

## 4.4 CSS Animations

```css
/* Pulsing alert effect */
@keyframes pulse { 
    0%, 100% { opacity: 1; } 
    50% { opacity: 0.5; } 
}

/* Route line animation (dashed moving line) */
@keyframes dash { 
    to { stroke-dashoffset: -30; } 
}

/* Truck moving along route */
@keyframes truckMove { 
    0% { offset-distance: 0%; } 
    100% { offset-distance: 100%; } 
}

/* Hardware connection indicator pulse */
@keyframes hardwarePulse { 
    0%, 100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); } 
    50% { box-shadow: 0 0 0 8px rgba(59, 130, 246, 0); } 
}
```

---

# 5. Backend Documentation

## 5.1 File Structure

```
backend/
├── app.py              # Main Flask application (1245 lines)
└── requirements.txt    # Python dependencies
```

## 5.2 Application Structure

```python
# app.py Structure

# 1. Imports and Flask Setup (lines 1-30)
# 2. Constants & Configurations (lines 30-80)
# 3. In-Memory Database (lines 80-160)
# 4. Risk Calculation Functions (lines 160-280)
# 5. API Endpoints - Locations (lines 280-520)
# 6. API Endpoints - Hardware (lines 520-600)
# 7. API Endpoints - Routes & Optimization (lines 600-900)
# 8. API Endpoints - Simulation (lines 900-1100)
# 9. API Endpoints - Statistics & Health (lines 1100-1180)
# 10. Error Handlers & Main (lines 1180-1245)
```

## 5.3 Data Models

### 5.3.1 Location Configuration

```python
LOCATION_CONFIGS = {
    'A1': {
        'name': 'Koregaon Park Corner',
        'route': 'A',
        'address': 'Koregaon Park, Pune',
        'distance_from_depot': 2.5,
        'position': (180, 120)
    },
    # ... 7 more locations
}
```

### 5.3.2 Bin Data Structure

```python
# WET Bin (Biodegradable)
wet_bin = {
    'id': 'A1_WET',
    'type': 'wet',
    'fill_level': 30.0,           # 0-100%
    'methane': 100.0,              # PPM
    'decomposition': 20.0,         # 0-100%
    'waste_composition': {
        'food': 2,                 # kg
        'paper': 0,
        'plastic': 0,
        'organic': 1
    },
    'is_real_hardware': True,      # Only A1_WET is True
    'last_updated': '2026-02-04T...'
}

# DRY Bin (Recyclables)
dry_bin = {
    'id': 'A1_DRY',
    'type': 'dry',
    'fill_level': 50.0,           # 0-100%
    'weight': 15.0,                # kg
    'waste_composition': {
        'food': 0,
        'paper': 3,
        'plastic': 2,
        'organic': 0
    },
    'is_real_hardware': False,
    'last_updated': '2026-02-04T...'
}
```

### 5.3.3 Waste Types Configuration

```python
WASTE_TYPES = {
    'food': {
        'density': 0.8,              # kg/unit
        'decomposition_rate': 0.15,   # per hour
        'methane_multiplier': 2.0     # methane generation factor
    },
    'paper': {
        'density': 0.3,
        'decomposition_rate': 0.08,
        'methane_multiplier': 0.5
    },
    'plastic': {
        'density': 1.2,
        'decomposition_rate': 0.02,   # Very slow
        'methane_multiplier': 0.3     # Low methane
    },
    'organic': {
        'density': 0.6,
        'decomposition_rate': 0.20,   # Fastest
        'methane_multiplier': 2.5     # Highest methane
    }
}
```

## 5.4 Risk Calculation Algorithm

### 5.4.1 WET Bin Risk (Environmental Priority)

```python
def calculate_bin_risk(bin_data):
    """
    WET BIN RISK CALCULATION:
    
    Formula: risk = (methane_risk × 0.50) + (decomposition_risk × 0.30) + (fill_risk × 0.20)
    
    Methane Risk (50% weight):
    - > 800 ppm → 100 (CRITICAL HEALTH HAZARD)
    - > 500 ppm → 80  (HIGH - urgent collection)
    - > 300 ppm → 60  (MEDIUM - needs attention)
    - ≤ 300 ppm → proportional (0-40)
    
    Decomposition Risk (30% weight):
    - decomposition × 0.30
    
    Fill Risk (20% weight):
    - fill_level × 0.20
    """
    if bin_data['type'] == 'wet':
        # Methane is PRIMARY concern (50%)
        methane_ppm = bin_data['methane']
        if methane_ppm > 800:
            methane_risk = 100
        elif methane_ppm > 500:
            methane_risk = 80
        elif methane_ppm > 300:
            methane_risk = 60
        else:
            methane_risk = (methane_ppm / 300) * 40
        
        decomposition_risk = bin_data['decomposition'] * 0.30
        fill_risk = bin_data['fill_level'] * 0.20
        
        wet_risk = (methane_risk * 0.50) + decomposition_risk + fill_risk
        return min(100, wet_risk)
```

### 5.4.2 DRY Bin Risk (Sanitation Focus)

```python
def calculate_bin_risk(bin_data):
    """
    DRY BIN RISK CALCULATION:
    
    Formula: risk = (fill_risk × 0.70) + (weight_risk × 0.30)
    
    CAPPED at 75: Plastic waste doesn't cause environmental emergency
    like methane emissions from organic waste.
    
    Fill Risk (70% weight):
    - fill_level × 0.70
    
    Weight Risk (30% weight):
    - (weight / 100) × 30
    """
    else:  # DRY bin
        fill_risk = bin_data['fill_level'] * 0.70
        weight_risk = (min(bin_data['weight'], 100) / 100) * 30
        dry_risk = fill_risk + weight_risk
        return min(75, dry_risk)  # Capped at 75
```

### 5.4.3 Location Risk

```python
def calculate_location_risk(location):
    """
    LOCATION RISK CALCULATION:
    
    Uses weighted average with environmental priority:
    - WET bin: 70% weight (methane is greenhouse gas)
    - DRY bin: 30% weight (sanitation concern)
    
    OVERRIDE RULE: If methane > 500 ppm → minimum risk = 85 (URGENT)
    """
    wet_risk = calculate_bin_risk(wet_bin)
    dry_risk = calculate_bin_risk(dry_bin)
    
    # Weighted average (70% environmental, 30% sanitation)
    location_risk = (wet_risk * 0.70) + (dry_risk * 0.30)
    
    # METHANE OVERRIDE: High methane = automatic urgent
    if wet_bin['methane'] > 500:
        location_risk = max(location_risk, 85)
    
    return min(100, location_risk)
```

## 5.5 Route Optimization Algorithm

### 5.5.1 Overview

The system uses a **Greedy Nearest Neighbor + 2-Opt Improvement** algorithm.

```
ALGORITHM FLOW:

Step 1: Calculate priority score for each location
Step 2: Sort by efficiency (priority/distance)
Step 3: Critical methane locations go FIRST (safety override)
Step 4: Apply 2-Opt improvement to reduce travel distance
Step 5: Select best route based on composite score
```

### 5.5.2 Priority Score Calculation

```python
def calculate_location_priority(location):
    """
    PRIORITY SCORE FACTORS:
    
    Factor 1: Risk Score (35% weight)
    - Uses calculate_location_risk()
    
    Factor 2: Fill Level Urgency (25% weight)
    - fill_level × decomposition_multiplier
    
    Factor 3: Methane Safety (5% weight, but OVERRIDE if >800ppm)
    - >800 ppm → 100 points + CRITICAL FLAG
    - >500 ppm → 50 points
    - else → proportional
    
    Factor 4: Time Window (15% weight)
    - Based on estimated hours until full
    - <4 hours → 80 points
    - <8 hours → 50 points
    - else → 20 points
    
    Factor 5: Distance Efficiency (20% weight)
    - (10 / (1 + distance)) × 0.20 × 100
    
    EFFICIENCY = priority_score / distance
    """
    # Factor 1: Risk (35%)
    risk_factor = location_risk * 0.35
    
    # Factor 2: Fill Urgency (25%)
    fill_urgency = (fill_level / 100) * (1 + decomposition/100)
    fill_factor = fill_urgency * 100 * 0.25
    
    # Factor 3: Methane Safety (5% but can override)
    if methane > 800:
        methane_factor = 100  # CRITICAL
        methane_override = True
    elif methane > 500:
        methane_factor = 50 * 0.05
    else:
        methane_factor = (methane / 1000) * 100 * 0.05
    
    # Factor 4: Time Window (15%)
    hours_until_full = (100 - fill_level) / 5
    if hours_until_full < 4:
        time_factor = 80 * 0.15
    elif hours_until_full < 8:
        time_factor = 50 * 0.15
    else:
        time_factor = 20 * 0.15
    
    # Factor 5: Distance (20%)
    distance_factor = (10 / (1 + distance)) * 0.20 * 100
    
    priority_score = risk_factor + fill_factor + methane_factor + time_factor + distance_factor
```

### 5.5.3 2-Opt Improvement

```python
def two_opt_improve(location_priorities, max_iterations=50):
    """
    2-OPT LOCAL SEARCH:
    
    Tries to improve the route by reversing segments.
    
    For route: A → B → C → D → E
    Try swapping: A → [D → C → B] → E
    If shorter, keep the swap.
    
    Continues until no improvement or max iterations.
    """
    best_order = location_priorities[:]
    improved = True
    
    while improved and iteration < max_iterations:
        improved = False
        
        for i in range(1, len(best_order) - 1):
            for j in range(i + 1, len(best_order)):
                # Try reversing segment [i:j+1]
                new_order = best_order[:i] + best_order[i:j+1][::-1] + best_order[j+1:]
                
                # Calculate total distances
                old_dist = sum(lp['distance'] for lp in best_order)
                new_dist = sum(lp['distance'] for lp in new_order)
                
                # Keep if shorter (with priority penalty)
                if new_dist < old_dist:
                    best_order = new_order
                    improved = True
                    break
    
    return best_order
```

### 5.5.4 Route Score Formula

```python
# ROUTE SCORE = (avg_priority × 0.6 + urgent_count × 20) / (1 + total_distance × 0.02)

# Higher score = Better route
# Rewards:
#   - Higher average priority (more urgent bins)
#   - More urgent locations (×20 bonus each)
# Penalizes:
#   - Longer distances
```

## 5.6 Simulation Engine

### 5.6.1 Time Advancement Logic

```python
def advance_simulation(hours):
    """
    SIMULATION ADVANCEMENT:
    
    For each WET bin (except A1_WET if hardware connected):
    
    1. DECOMPOSITION increases by 0.5% per hour
       - Only if bin has waste (fill_level > 0)
    
    2. METHANE is GENERATED based on waste composition:
       - For each waste type in bin:
         methane += quantity × methane_multiplier × (decomposition/100)
       - Scaled by hours × 0.1
    
    DRY bins: No decomposition or methane (plastic doesn't decompose)
    """
    for bin_data in all_bins:
        # Skip A1_WET if hardware is sending real data
        if bin_data['id'] == 'A1_WET' and hardware_connected:
            continue
        
        if bin_data['type'] == 'wet' and bin_data['fill_level'] > 0:
            # Decomposition
            bin_data['decomposition'] += 0.5 * hours
            
            # Methane generation
            decomp_factor = bin_data['decomposition'] / 100
            for waste_type, qty in bin_data['waste_composition'].items():
                methane_gen = qty * WASTE_TYPES[waste_type]['methane_multiplier'] * decomp_factor
                bin_data['methane'] += methane_gen * 0.1 * hours
```

---

# 6. Hardware Documentation

## 6.1 Supported Hardware Configurations

### Option 1: Arduino IDE (C++)
- File: `hardware/esp32_sensor.ino`
- Config: `hardware/sensor_config.h`

### Option 2: MicroPython (Thonny IDE)
- Offline: `hardware/micropython/main.py`
- WiFi: `hardware/micropython/main_wifi.py`

## 6.2 Sensor Specifications

### 6.2.1 HC-SR04 Ultrasonic Sensor (Fill Level)

```
SPECIFICATIONS:
- Working Voltage: 5V (use level shifter) or 3.3V
- Working Current: 15mA
- Range: 2cm - 400cm
- Accuracy: ±3mm
- Trigger Pulse: 10µs minimum

WIRING:
ESP32 GPIO4  → TRIG (Trigger pulse)
ESP32 GPIO5  → ECHO (Echo return)
ESP32 3.3V   → VCC
ESP32 GND    → GND

ALGORITHM:
1. Send 10µs HIGH pulse on TRIG
2. Measure time until ECHO goes HIGH
3. Distance (cm) = duration (µs) / 58
4. Fill Level (%) = ((BIN_HEIGHT - distance) / BIN_HEIGHT) × 100
```

### 6.2.2 MQ-4 Methane Gas Sensor

```
SPECIFICATIONS:
- Detection: Methane (CH4), Natural Gas
- Range: 200 - 10000 ppm
- Operating Voltage: 5V
- Heater Consumption: ≤ 800mW
- Warm-up Time: 20+ seconds

WIRING:
ESP32 GPIO34 → AO (Analog Output)
ESP32 3.3V   → VCC
ESP32 GND    → GND

ALGORITHM:
1. Read ADC value (0-4095 on ESP32)
2. Calculate ratio to clean air baseline
3. Convert to PPM using logarithmic curve
4. MQ-4 responds to methane concentration exponentially

CALIBRATION:
- MQ4_CLEAN_AIR = ADC reading in fresh air (typically 200-1000)
- Calibrate after 24-48 hours of burn-in
```

### 6.2.3 MQ-135 Air Quality Sensor

```
SPECIFICATIONS:
- Detection: CO2, Ammonia, Benzene, Alcohol, Smoke
- Operating Voltage: 5V
- Warm-up Time: 20+ seconds

WIRING:
ESP32 GPIO35 → AO (Analog Output)
ESP32 3.3V   → VCC (or 5V via level shifter)
ESP32 GND    → GND

ALGORITHM:
- Similar to MQ-4
- Used for general air quality index (0-100)
- Higher reading = worse air quality
```

### 6.2.4 HX711 + Load Cell (Weight Sensor)

```
SPECIFICATIONS:
- Precision: 24-bit ADC
- Gain Options: 128, 64, 32
- Load Cell: Typically 5-50kg capacity

WIRING:
ESP32 GPIO22 → DT (Data)
ESP32 GPIO23 → SCK (Clock)
ESP32 3.3V   → VCC
ESP32 GND    → GND

Load Cell to HX711:
Red    → E+ (Excitation+)
Black  → E- (Excitation-)
White  → A- (Amplifier-)
Green  → A+ (Amplifier+)

ALGORITHM:
1. Wait for DT to go LOW (ready signal)
2. Pulse SCK 24 times, read DT on each pulse
3. Add 1 more pulse to set gain
4. Subtract tare offset
5. Divide by scale factor to get grams

CALIBRATION:
1. Empty scale → record TARE_OFFSET
2. Place known weight → calculate SCALE_FACTOR
```

## 6.3 Wiring Diagram

```
                    ┌─────────────────────────────────────┐
                    │          ESP32 DevKit V1            │
                    │                                     │
                    │  3.3V ○─────┬────────┬────────┐    │
                    │             │        │        │    │
                    │        ┌────┴────┐ ┌─┴──┐ ┌──┴──┐ │
                    │        │ HC-SR04 │ │MQ-4│ │MQ135│ │
                    │        │   VCC   │ │VCC │ │ VCC │ │
                    │        └────┬────┘ └─┬──┘ └──┬──┘ │
                    │             │        │        │    │
    GPIO4 ○─────────┼─────────────┤TRIG    │        │    │
    GPIO5 ○─────────┼─────────────┤ECHO    │        │    │
   GPIO34 ○─────────┼─────────────┼────────┤AO      │    │
   GPIO35 ○─────────┼─────────────┼────────┼────────┤AO  │
                    │             │        │        │    │
                    │  GND ○──────┴────────┴────────┴────┘
                    │                                     │
                    │  GPIO22 ○────────── HX711 DT        │
                    │  GPIO23 ○────────── HX711 SCK       │
                    │  3.3V ○───────────── HX711 VCC      │
                    │  GND ○────────────── HX711 GND      │
                    │                                     │
                    └─────────────────────────────────────┘

CONNECTIONS SUMMARY:
┌──────────────┬──────────────┬─────────────────────────┐
│  ESP32 Pin   │    Sensor    │       Function          │
├──────────────┼──────────────┼─────────────────────────┤
│    3.3V      │  HC-SR04     │  Power                  │
│    GPIO4     │  HC-SR04     │  Trigger pulse          │
│    GPIO5     │  HC-SR04     │  Echo return            │
│    GND       │  HC-SR04     │  Ground                 │
├──────────────┼──────────────┼─────────────────────────┤
│    3.3V      │  MQ-4        │  Power                  │
│    GPIO34    │  MQ-4        │  Analog out (methane)   │
│    GND       │  MQ-4        │  Ground                 │
├──────────────┼──────────────┼─────────────────────────┤
│    3.3V      │  MQ-135      │  Power                  │
│    GPIO35    │  MQ-135      │  Analog out (air qual)  │
│    GND       │  MQ-135      │  Ground                 │
├──────────────┼──────────────┼─────────────────────────┤
│    3.3V      │  HX711       │  Power                  │
│    GPIO22    │  HX711       │  Data (DT)              │
│    GPIO23    │  HX711       │  Clock (SCK)            │
│    GND       │  HX711       │  Ground                 │
└──────────────┴──────────────┴─────────────────────────┘
```

## 6.4 MicroPython Code Flow

```python
# main.py Flow (Offline Mode)

def main():
    # 1. Initialize hardware
    setup_pins()
    
    # 2. Warm up gas sensors (20 seconds)
    warmup_sensors()
    
    # 3. Tare weight sensor
    hx711_tare()
    
    # 4. Main loop
    while True:
        # Read all sensors
        data = read_all_sensors()
        
        # Print formatted output
        print_sensor_data(data)
        
        # Wait 5 seconds
        time.sleep(5)

# main_wifi.py Flow (WiFi Mode)

def main():
    # 1. Connect to WiFi
    connect_wifi()
    
    # 2. Initialize sensors
    warmup_sensors()
    hx711_tare()
    
    # 3. Main loop
    while True:
        # Read sensors
        data = read_all_sensors()
        
        # Print locally
        print_sensor_data(data)
        
        # Send to backend (if WiFi connected)
        if is_wifi_connected():
            send_to_backend({
                'fill_level': data['fill_level'],
                'methane': data['methane']
            })
        
        # Wait SEND_INTERVAL seconds
        time.sleep(SEND_INTERVAL)
```

## 6.5 Backend Integration

```
ESP32 → POST /api/locations/A1/bins/A1_WET/hardware
        Content-Type: application/json
        Body: {"fill_level": 45.3, "methane": 250.5}

Backend Response:
{
    "status": "success",
    "message": "A1_WET updated from ESP32 hardware",
    "hardware_connected": true,
    "bin": {...},
    "location_risk": 52.3
}

IMPORTANT:
- Only A1_WET accepts hardware data
- When hardware sends data, simulation is SKIPPED for A1_WET
- Real data OVERRIDES simulated values
- Hardware connection times out after 30 seconds of no data
```

---

# 7. Algorithms & Logic

## 7.1 Risk Status Thresholds

```
RISK SCORE → STATUS MAPPING:

┌────────────────┬──────────────┬──────────────────────────────┐
│  Risk Score    │    Status    │         Action Required      │
├────────────────┼──────────────┼──────────────────────────────┤
│    0 - 40      │   🟢 Normal  │  Routine collection          │
│   40 - 70      │   🟡 Warning │  Schedule within 24 hours    │
│   70 - 100     │   🔴 Urgent  │  Collect within 2 hours      │
└────────────────┴──────────────┴──────────────────────────────┘

SPECIAL OVERRIDE:
- Methane > 500 ppm → Location automatically becomes URGENT
- Methane > 800 ppm → CRITICAL HEALTH HAZARD (emergency)
```

## 7.2 Fill Level Calculation

```
ULTRASONIC → FILL LEVEL:

BIN_HEIGHT = 50 cm (configurable)
SENSOR_OFFSET = 2 cm (distance from sensor to bin top)

1. Read distance from ultrasonic sensor
2. Calculate empty space:
   empty_space = distance - SENSOR_OFFSET

3. Calculate fill level:
   fill_level = ((BIN_HEIGHT - empty_space) / BIN_HEIGHT) × 100

4. Clamp to 0-100%:
   fill_level = max(0, min(100, fill_level))

EXAMPLE:
- Distance = 20 cm
- Empty space = 20 - 2 = 18 cm
- Fill level = ((50 - 18) / 50) × 100 = 64%
```

## 7.3 Methane PPM Calculation

```
MQ-4 ADC → METHANE PPM:

1. Read ADC value (0-4095 on ESP32)
2. Calculate ratio to clean air baseline:
   ratio = raw_value / MQ4_CLEAN_AIR

3. Convert to PPM (simplified):
   if ratio <= 1:
       ppm = ratio × 200  # Low concentration
   else:
       ppm = 200 + (ratio - 1) × 500  # Higher concentration

4. Cap at 10000 ppm:
   ppm = min(ppm, 10000)

NOTE: This is a simplified conversion.
For accurate readings, use manufacturer's calibration curve.
```

## 7.4 Methane Generation (Simulation)

```
DECOMPOSITION MODEL:

Time-based methane generation for simulated bins:

1. Decomposition increases 0.5% per hour (if bin has waste)
2. Methane is generated based on waste composition:

   For each waste type in bin:
       methane_gen += quantity × methane_multiplier × (decomposition/100)
   
   Total methane += methane_gen × 0.1 × hours

WASTE TYPE METHANE MULTIPLIERS:
- Food:    2.0 (high methane)
- Organic: 2.5 (highest methane)
- Paper:   0.5 (low methane)
- Plastic: 0.3 (very low methane)

EXAMPLE:
Bin has: 5kg food, 2kg organic
Decomposition: 50%

Methane per hour:
= (5 × 2.0 + 2 × 2.5) × 0.5 × 0.1
= (10 + 5) × 0.5 × 0.1
= 0.75 ppm/hour
```

## 7.5 Edge Case Handling

```
BIN FULL PREVENTION:

Before adding waste:
1. Check if fill_level >= 100
   → Error: "Bin is FULL!"

2. Check if fill_level >= 95
   → Error: "Bin is almost full!"

3. Calculate projected fill:
   projected = fill_level + (quantity × 8)
   
   If projected > 100:
   → Error: "Adding this would overflow!"
   → Suggest max quantity

WASTE TYPE VALIDATION:

DRY bins ONLY accept:
- Paper
- Plastic

If trying to add food/organic to DRY bin:
→ Error: "DRY bins cannot accept [waste_type]"
```

---

# 8. Data Flow & Communication

## 8.1 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COMPLETE DATA FLOW                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│    HARDWARE FLOW (Real Sensors)                                             │
│    ────────────────────────────                                             │
│                                                                              │
│    Ultrasonic ─┐                                                            │
│    MQ-4 ───────┼─→ ESP32 ─── WiFi ───→ POST /api/.../hardware ───→ Backend │
│    MQ-135 ─────┤        (JSON)           (every 10s)                        │
│    HX711 ──────┘                                                            │
│                                                                              │
│    SIMULATION FLOW (Simulated Bins)                                         │
│    ────────────────────────────────                                         │
│                                                                              │
│    User clicks "Advance Time" ───→ POST /api/simulation/advance             │
│                                            │                                 │
│                                            ▼                                 │
│                                    Backend calculates:                       │
│                                    - Decomposition increase                  │
│                                    - Methane generation                      │
│                                            │                                 │
│                                            ▼                                 │
│                                    Returns updated locations                 │
│                                                                              │
│    UI FLOW (Dashboard Updates)                                              │
│    ────────────────────────────                                             │
│                                                                              │
│    Page Load ───→ GET /api/locations ───→ Render map + bins                 │
│         │                                                                    │
│         ▼                                                                    │
│    setInterval (10s) ───→ GET /api/locations ───→ Update UI                 │
│         │                                                                    │
│         ▼                                                                    │
│    User clicks "Optimize" ───→ GET /api/routes/optimize ───→ Show result   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 8.2 API Request/Response Examples

### 8.2.1 Get All Locations

```http
GET /api/locations
```

Response:
```json
{
    "status": "success",
    "time": 6,
    "hardware_connected": true,
    "locations": {
        "A1": {
            "id": "A1",
            "name": "Koregaon Park Corner",
            "route": "A",
            "location_risk": 45.3,
            "status": "warning",
            "bins": {
                "A1_WET": {
                    "id": "A1_WET",
                    "type": "wet",
                    "fill_level": 65.2,
                    "methane": 280.5,
                    "decomposition": 42.0,
                    "risk_score": 52.3,
                    "status": "warning",
                    "is_real_hardware": true
                },
                "A1_DRY": {
                    "id": "A1_DRY",
                    "type": "dry",
                    "fill_level": 50.0,
                    "weight": 15.0,
                    "risk_score": 39.5,
                    "status": "normal"
                }
            }
        }
        // ... 7 more locations
    }
}
```

### 8.2.2 Add Waste

```http
POST /api/locations/A1/bins/A1_WET/add-waste
Content-Type: application/json

{"type": "food", "quantity": 5}
```

Response:
```json
{
    "status": "success",
    "message": "Added 5kg of food to A1_WET",
    "changes": {
        "fill_level": {"old": 30.0, "new": 70.0},
        "bin_risk": {"old": 25.3, "new": 48.7},
        "location_risk": {"old": 32.1, "new": 55.4}
    },
    "bin": {...},
    "location_risk": 55.4,
    "location_status": "warning"
}
```

### 8.2.3 Route Optimization

```http
GET /api/routes/optimize
```

Response:
```json
{
    "status": "success",
    "optimization": {
        "best_route": "A",
        "best_route_name": "Route A: Central District",
        "reason": "Route A selected with highest optimization score (12.5). Has 2 urgent + 1 warning locations...",
        "collection_order": ["A1", "A3", "A2"],
        "algorithm": "Greedy Nearest Neighbor + 2-Opt Improvement",
        "formula": {
            "priority": "(risk × 0.35) + (fill_urgency × 0.25) + (methane × 0.05) + (time_window × 0.15) + (distance_efficiency × 0.20)",
            "route_score": "(avg_priority × 0.6 + urgent_count × 20) / (1 + total_distance × 0.02)"
        },
        "comparison": [
            "Route A: score=12.5, urgent=2, avg_priority=68.3, distance=8.5km → BEST",
            "Route B: score=8.2, urgent=1, avg_priority=45.2, distance=12.5km",
            "Route C: score=5.1, urgent=0, avg_priority=32.1, distance=6.0km"
        ],
        "all_routes": {...}
    }
}
```

---

# 9. API Reference

## 9.1 Complete Endpoint List

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/locations` | Get all 8 locations with bin data |
| GET | `/api/locations/<id>` | Get single location details |
| POST | `/api/locations/<id>/bins/<bin_id>/add-waste` | Add waste to bin |
| POST | `/api/locations/<id>/bins/<bin_id>/empty` | Empty a bin |
| POST | `/api/locations/<id>/collect` | Collect both bins at location |
| POST | `/api/locations/A1/bins/A1_WET/hardware` | ESP32 sensor data endpoint |
| GET | `/api/hardware/status` | Check hardware connection |
| GET | `/api/routes` | Get all routes with locations |
| GET | `/api/routes/optimize` | Get optimal route recommendation |
| POST | `/api/simulation/advance` | Advance time by N hours |
| POST | `/api/simulation/reset` | Reset to initial state |
| POST | `/api/simulation/demo` | Create demo scenario |
| GET | `/api/statistics` | Get system-wide stats |
| GET | `/api/health` | Health check endpoint |
| GET | `/` | Serve frontend dashboard |

## 9.2 Endpoint Details

### Locations Endpoints

```
GET /api/locations
Returns: All locations with calculated risks and alerts

GET /api/locations/<location_id>
Parameters: location_id (A1, A2, A3, B1, B2, B3, C1, C2)
Returns: Single location with full details

POST /api/locations/<location_id>/bins/<bin_id>/add-waste
Body: {"type": "food|paper|plastic|organic", "quantity": 1-20}
Returns: Updated bin and location risk

POST /api/locations/<location_id>/bins/<bin_id>/empty
Returns: Emptied bin data

POST /api/locations/<location_id>/collect
Returns: Both bins emptied
```

### Hardware Endpoints

```
POST /api/locations/A1/bins/A1_WET/hardware
Body: {"fill_level": 0-100, "methane": 0-1000}
Note: ONLY for A1_WET bin

GET /api/hardware/status
Returns: {
    "hardware_connected": boolean,
    "last_update": timestamp,
    "timeout_seconds": 30
}
```

### Simulation Endpoints

```
POST /api/simulation/advance
Body: {"hours": 1-24}
Returns: All locations with decomposition/methane updates

POST /api/simulation/reset
Returns: Initial state restored

POST /api/simulation/demo
Returns: A1, B2 critical; A3 warning
```

---

# 10. Project Setup Guide

## 10.1 Prerequisites

```
REQUIRED SOFTWARE:
┌────────────────────────────────────────────────────────────────┐
│  Software              │  Version    │  Download Link          │
├────────────────────────┼─────────────┼─────────────────────────┤
│  Python                │  3.8+       │  python.org/downloads   │
│  Web Browser           │  Any modern │  Chrome/Firefox/Edge    │
│  Git (optional)        │  Latest     │  git-scm.com            │
└────────────────────────┴─────────────┴─────────────────────────┘

FOR HARDWARE (Optional):
┌────────────────────────────────────────────────────────────────┐
│  Arduino IDE           │  1.8+       │  arduino.cc             │
│  OR Thonny             │  4.0+       │  thonny.org             │
│  USB Driver            │  CH340/CP210x│  Manufacturer site     │
└────────────────────────────────────────────────────────────────┘
```

## 10.2 Installation Steps

### Step 1: Get the Code

```powershell
# Clone or download the project
cd C:\Users\YourName\Documents\VSCode
# Place "Smart Bin 2" folder here
```

### Step 2: Install Python Dependencies

```powershell
# Open terminal in project folder
cd "Smart Bin 2\backend"

# Install dependencies
pip install -r requirements.txt

# Or manually:
pip install flask flask-cors python-dateutil
```

### Step 3: Start the System

**Option A: One-Click (Recommended)**
```
Double-click: start_system.bat
```

**Option B: Manual Start**

```powershell
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend (optional, backend serves frontend)
cd frontend
python -m http.server 8000
```

### Step 4: Open Dashboard

```
🌐 Open browser: http://localhost:5000
```

## 10.3 Hardware Setup (Optional)

### Step 1: Wire the Sensors

Follow wiring diagram in Section 6.3

### Step 2: Flash Code to ESP32

**Using Arduino IDE:**
```
1. Install ESP32 board support
2. Open hardware/esp32_sensor.ino
3. Update WiFi credentials (lines 34-35)
4. Update backend IP (line 40)
5. Select: Tools → Board → ESP32 DevKit V1
6. Select: Tools → Port → COM3 (or your port)
7. Click Upload
```

**Using Thonny (MicroPython):**
```
1. Flash MicroPython firmware to ESP32
2. Open hardware/micropython/main_wifi.py
3. Update WiFi credentials
4. Update backend IP
5. Save to device as main.py
```

### Step 3: Find Your Computer's IP

```powershell
ipconfig
# Look for "IPv4 Address" under WiFi adapter
# Example: 192.168.1.50
```

### Step 4: Verify Connection

```
1. Start backend (python app.py)
2. Power on ESP32
3. Watch backend terminal for POST requests
4. Dashboard should show "⚡ ESP32 Connected"
```

---

# 11. Troubleshooting Guide

## 11.1 Backend Issues

### Backend won't start

```
ERROR: ModuleNotFoundError: No module named 'flask'

SOLUTION:
pip install flask flask-cors

ERROR: Address already in use (port 5000)

SOLUTION:
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <process_id> /F

# Or use different port
python app.py --port 5001
```

### CORS errors in browser

```
ERROR: Access-Control-Allow-Origin

SOLUTION:
1. Ensure flask-cors is installed
2. Check app.py has: CORS(app)
3. Clear browser cache
4. Restart backend
```

## 11.2 Frontend Issues

### Dashboard not loading

```
PROBLEM: Blank page or errors

SOLUTIONS:
1. Check backend is running (http://localhost:5000/api/health)
2. Check browser console for errors (F12)
3. Verify API_BASE in index.html matches backend URL
4. Try hard refresh (Ctrl+Shift+R)
```

### Map not showing locations

```
PROBLEM: SVG map empty

SOLUTIONS:
1. Check if /api/locations returns data
2. Check browser console for JavaScript errors
3. Verify LOCATION_POSITIONS matches backend location IDs
```

## 11.3 Hardware Issues

### ESP32 won't connect to WiFi

```
PROBLEM: WiFi connection fails

SOLUTIONS:
1. Verify SSID and password (case-sensitive!)
2. Ensure 2.4GHz network (ESP32 doesn't support 5GHz)
3. Check WiFi signal strength
4. Try closer to router
5. Check if WIFI_ENABLED = True
```

### Sensor readings incorrect

```
PROBLEM: Ultrasonic shows wrong distance

SOLUTIONS:
1. Check wiring (TRIG/ECHO correct?)
2. Measure actual bin height
3. Adjust BIN_HEIGHT_CM constant
4. Check for obstructions

PROBLEM: MQ-4 always shows high methane

SOLUTIONS:
1. Let sensor warm up (20+ seconds)
2. Calibrate in fresh air
3. Adjust MQ4_CLEAN_AIR baseline
4. Check sensor is not damaged
```

### Data not reaching backend

```
PROBLEM: ESP32 sends but backend doesn't receive

SOLUTIONS:
1. Check both devices on same network
2. Verify backend IP is correct
3. Check firewall allows port 5000
4. Try: curl http://YOUR_IP:5000/api/health
5. Check backend terminal for errors
```

## 11.4 Simulation Issues

### Time advance doesn't change methane

```
PROBLEM: Clicking +1h doesn't increase methane

SOLUTIONS:
1. Ensure bin has waste (add waste first)
2. Methane is generated, not instant
3. Advance more hours (+6h)
4. Check waste_composition is not empty
```

### Route optimization always picks same route

```
PROBLEM: Always recommends Route A

SOLUTIONS:
1. Add more waste to other routes
2. Click "Demo Scenario" for varied data
3. Check if all routes have similar risk levels
4. Algorithm picks highest score route
```

---

# 12. Common Problems & Solutions

## 12.1 Quick Reference Table

| Problem | Cause | Solution |
|---------|-------|----------|
| "Backend Offline" | Backend not running | Run `python app.py` |
| Blank dashboard | JavaScript error | Check console (F12) |
| "No Hardware" | ESP32 not sending | Check WiFi + IP |
| Can't add waste | Bin is full (>=95%) | Empty bin first |
| Methane stays at 0 | No organic waste | Add food/organic |
| Wrong port | 5000 in use | Kill process or change port |
| CORS error | Flask-CORS missing | `pip install flask-cors` |
| ESP32 timeout | Bad connection | Check wiring |
| Map colors wrong | Risk calculation | Check thresholds |

## 12.2 Emergency Reset

```powershell
# If everything is broken:

# 1. Stop all processes
taskkill /IM python.exe /F

# 2. Clear browser cache
# Chrome: Ctrl+Shift+Delete

# 3. Restart backend
cd backend
python app.py

# 4. Reset simulation
# In browser: Click "Reset Simulation"

# 5. Open fresh browser tab
# Navigate to http://localhost:5000
```

---

# 13. File Structure Reference

## 13.1 Complete Project Tree

```
Smart Bin 2/
│
├── 📄 README.md                    # Project overview
├── 📄 HARDWARE_CONNECTION_GUIDE.md # Hardware setup guide
├── 📄 start_backend.bat            # Start backend (Windows)
├── 📄 start_frontend.bat           # Start frontend (Windows)
├── 📄 start_system.bat             # Start everything (Windows)
│
├── 📁 backend/
│   ├── 📄 app.py                   # Flask API server (1245 lines)
│   │   ├── Imports & Setup
│   │   ├── Constants & Configuration
│   │   ├── In-Memory Database
│   │   ├── Risk Calculation Functions
│   │   ├── API Endpoints - Locations
│   │   ├── API Endpoints - Hardware
│   │   ├── API Endpoints - Routes
│   │   ├── API Endpoints - Simulation
│   │   └── Main Entry Point
│   │
│   └── 📄 requirements.txt         # Python dependencies
│
├── 📁 frontend/
│   └── 📄 index.html               # Dashboard (1394 lines)
│       ├── HTML Structure
│       ├── Tailwind CSS Styles
│       ├── SVG City Map
│       └── JavaScript Application
│
├── 📁 hardware/
│   ├── 📄 esp32_sensor.ino         # Arduino C++ code
│   ├── 📄 sensor_config.h          # Hardware configuration
│   │
│   └── 📁 micropython/
│       ├── 📄 main.py              # Offline sensor reading
│       ├── 📄 main_wifi.py         # WiFi + backend integration
│       ├── 📄 test_sensors.py      # Individual sensor tests
│       ├── 📄 test_weight.py       # Weight sensor calibration
│       ├── 📄 monitor_all_sensors.py # Live monitoring
│       ├── 📄 monitor_weight.py    # Weight calibration
│       ├── 📄 send_raw_data.py     # Raw data to backend
│       └── 📄 README.py            # Setup instructions
│
└── 📁 docs/
    ├── 📄 setup-guide.md           # Detailed setup
    ├── 📄 api-reference.md         # API documentation
    └── 📄 COMPLETE_PROJECT_DOCUMENTATION.md  # This file
```

## 13.2 Key File Descriptions

| File | Lines | Purpose |
|------|-------|---------|
| `backend/app.py` | 1245 | Main Flask API with all algorithms |
| `frontend/index.html` | 1394 | Complete dashboard with map |
| `hardware/esp32_sensor.ino` | ~250 | Arduino code for ESP32 |
| `hardware/micropython/main_wifi.py` | 335 | MicroPython with WiFi |
| `hardware/micropython/main.py` | 393 | MicroPython offline |

---

# Appendix A: Quick Commands Reference

```powershell
# Start Backend
cd backend && python app.py

# Start Frontend (standalone)
cd frontend && python -m http.server 8000

# Install Dependencies
pip install flask flask-cors

# Check Backend Health
curl http://localhost:5000/api/health

# Find Your IP
ipconfig

# Kill Port 5000
netstat -ano | findstr :5000
taskkill /PID <pid> /F
```

---

# Appendix B: Environment Variables (Optional)

```python
# Can be set in app.py or environment

FLASK_ENV=development    # Enable debug mode
FLASK_DEBUG=1            # Auto-reload on changes
HOST=0.0.0.0             # Listen on all interfaces
PORT=5000                # API port
```

---

# Appendix C: Cost Estimate

| Component | Quantity | Cost (INR) |
|-----------|----------|------------|
| ESP32 DevKit V1 | 1 | ₹400-500 |
| HC-SR04 Ultrasonic | 1 | ₹50-80 |
| MQ-4 Methane Sensor | 1 | ₹150-200 |
| MQ-135 Air Quality | 1 | ₹150-200 |
| HX711 + Load Cell | 1 | ₹200-300 |
| Breadboard | 1 | ₹80-100 |
| Jumper Wires | 1 set | ₹50-80 |
| USB Cable | 1 | ₹50-100 |
| **TOTAL** | | **₹1130-1560** |

---

# Appendix D: Future Enhancements

1. **Database Integration** - Replace in-memory with PostgreSQL/MongoDB
2. **User Authentication** - Admin login for route management
3. **Mobile App** - React Native companion app
4. **Multiple Hardware Bins** - Support all 16 bins with hardware
5. **Machine Learning** - Predictive fill level forecasting
6. **SMS/Email Alerts** - Automatic notifications for urgent bins
7. **GPS Integration** - Real truck tracking
8. **Analytics Dashboard** - Historical data and trends

---

**Document Version:** 1.0  
**Last Updated:** February 4, 2026  
**Author:** Smart Waste System Documentation

---

*End of Complete Project Documentation*
