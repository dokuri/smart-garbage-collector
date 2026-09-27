# 📚 Smart Waste System - API Reference

Base URL: `http://localhost:5000/api`

---

## System Overview

- **8 Locations** across 3 routes
- **Each location has 2 bins**: WET (💧) + DRY (📦)
- **Total: 16 bins**
- **Real hardware**: A1_WET accepts ESP32 data

---

## Health Check

### GET /health
Check if the API is running.

**Response:**
```json
{
  "status": "success",
  "message": "Smart Waste System API is running",
  "locations_count": 8,
  "bins_count": 16,
  "routes_count": 3
}
```

---

## Locations

### GET /locations
Get all locations with current status.

**Response:**
```json
{
  "status": "success",
  "time": 0,
  "locations": {
    "A1": {
      "id": "A1",
      "name": "Koregaon Park Corner",
      "route": "A",
      "address": "Koregaon Park, Pune",
      "distance_from_depot": 2.5,
      "position": [180, 120],
      "location_risk": 45.2,
      "status": "warning",
      "bins": {
        "A1_WET": {
          "id": "A1_WET",
          "type": "wet",
          "fill_level": 32.5,
          "methane": 125.0,
          "decomposition": 22.5,
          "waste_composition": {"food": 0, "paper": 0, "plastic": 0, "organic": 0},
          "is_real_hardware": true,
          "risk_score": 38.2,
          "status": "normal"
        },
        "A1_DRY": {
          "id": "A1_DRY",
          "type": "dry",
          "fill_level": 45.0,
          "weight": 18.5,
          "waste_composition": {"food": 0, "paper": 0, "plastic": 0, "organic": 0},
          "is_real_hardware": false,
          "risk_score": 52.2,
          "status": "warning"
        }
      }
    }
  }
}
```

### GET /locations/{location_id}
Get specific location details.

**Example:** `GET /locations/A1`

---

### POST /locations/{location_id}/bins/{bin_id}/add-waste
Add waste to a specific bin within a location.

**Example:** `POST /locations/A1/bins/A1_WET/add-waste`

**Request Body:**
```json
{
  "type": "food",
  "quantity": 5
}
```

**Waste Types:**
| Type | Density | Decomp Rate | Methane Multiplier |
|------|---------|-------------|-------------------|
| food | 0.8 | 0.15 | 2.0 |
| paper | 0.3 | 0.08 | 0.5 |
| plastic | 1.2 | 0.02 | 0.3 |
| organic | 0.6 | 0.20 | 2.5 |

**Response:**
```json
{
  "status": "success",
  "message": "Added 5kg of food waste to A1_WET",
  "changes": {
    "fill_level": {"old": 30.0, "new": 70.0},
    "bin_risk": {"old": 35.5, "new": 58.2},
    "location_risk": {"old": 42.0, "new": 55.3}
  },
  "bin": {
    "id": "A1_WET",
    "type": "wet",
    "fill_level": 70.0,
    "methane": 125.0,
    "decomposition": 23.25,
    "risk_score": 58.2,
    "status": "warning"
  },
  "location_risk": 55.3,
  "location_status": "warning"
}
```

---

### POST /locations/{location_id}/bins/{bin_id}/hardware
Update bin data from real hardware (ESP32).

**Note:** Only works for `A1_WET` (the hardware bin).

**Example:** `POST /locations/A1/bins/A1_WET/hardware`

**Request Body:**
```json
{
  "fill_level": 75.5,
  "methane": 350.0
}
```

---

## Routes

### GET /routes
Get all routes with their locations.

**Response:**
```json
{
  "status": "success",
  "routes": {
    "A": {
      "id": "A",
      "name": "Route A: Central District",
      "road": "Main Street & Park Avenue",
      "distance": 8.5,
      "locations": { ... }
    },
    "B": { ... },
    "C": { ... }
  }
}
```

---

### GET /routes/optimize
Find the best route to collect based on advanced multi-factor optimization.

**Algorithm: Greedy Nearest Neighbor + 2-Opt Improvement**

This endpoint uses a sophisticated optimization algorithm that considers multiple weighted factors to determine the optimal collection route and order.

**Optimization Factors (Weighted):**
| Factor | Weight | Description |
|--------|--------|-------------|
| Risk Score | 35% | Max of WET/DRY bin risk scores |
| Fill Level Urgency | 25% | Fill level × decomposition factor |
| Distance Efficiency | 20% | Priority/distance ratio |
| Time Window | 15% | Hours until overflow |
| Methane Safety | 5% | With OVERRIDE if >800ppm |

**Priority Formula:**
```
priority = (risk × 0.35) + (fill_urgency × 0.25) + (methane × 0.05) + (time_window × 0.15) + (distance_efficiency × 0.20)
```

**Route Score Formula:**
```
route_score = (avg_priority × 0.6 + urgent_count × 20) / (1 + total_distance × 0.02)
```

**Safety Override:**
- If methane > 800 ppm at any location → That location is collected FIRST regardless of distance

**Response:**
```json
{
  "status": "success",
  "optimization": {
    "best_route": "A",
    "best_route_name": "Route A: Central District",
    "reason": "Route A selected with highest optimization score (18.5). Has 2 urgent + 1 warning locations. Average priority: 65.2, Max risk: 78.5. Total distance: 8.5km. Recommended collection: A1 → A3 → A2 → Depot",
    "explanation": "Route A is OPTIMAL:\n📍 Collection Order: A1 → A3 → A2 → Depot\n...",
    "collection_order": ["A1", "A3", "A2"],
    "urgent_locations": [
      {
        "id": "A1",
        "name": "Koregaon Park Corner",
        "priority": 78.5,
        "risk": 72.5,
        "efficiency": 28.6,
        "distance": 2.5,
        "methane": 450.0,
        "fill_urgency": 85.0,
        "is_critical": false,
        "reason": "🔴 URGENT: 85.0% full + methane 450ppm",
        "status": "urgent"
      }
    ],
    "algorithm": "Greedy Nearest Neighbor + 2-Opt Improvement",
    "formula": {
      "priority": "(risk × 0.35) + (fill_urgency × 0.25) + (methane × 0.05) + (time_window × 0.15) + (distance_efficiency × 0.20)",
      "route_score": "(avg_priority × 0.6 + urgent_count × 20) / (1 + total_distance × 0.02)"
    },
    "factors": {
      "risk_weight": "35%",
      "fill_urgency_weight": "25%",
      "distance_efficiency_weight": "20%",
      "time_window_weight": "15%",
      "methane_safety_weight": "5% (with OVERRIDE if >800ppm)"
    },
    "comparison": [
      "Route A: score=18.5, urgent=2, avg_priority=65.2, distance=8.5km → BEST",
      "Route B: score=12.3, urgent=1, avg_priority=45.8, distance=12.5km",
      "Route C: score=10.1, urgent=0, avg_priority=35.2, distance=6.0km"
    ],
    "all_routes": {
      "A": {
        "route_id": "A",
        "name": "Route A: Central District",
        "road": "Main Street & Park Avenue",
        "score": 18.5,
        "avg_priority": 65.2,
        "max_risk": 78.5,
        "urgent_locations": 2,
        "warning_locations": 1,
        "locations_count": 3,
        "total_distance": 8.5,
        "collection_order": ["A1", "A3", "A2"],
        "location_details": [
          {
            "id": "A1",
            "name": "Koregaon Park Corner",
            "priority": 78.5,
            "risk": 72.5,
            "efficiency": 28.6,
            "distance": 2.5,
            "methane": 450.0,
            "fill_urgency": 85.0,
            "is_critical": false,
            "reason": "🔴 URGENT: 85.0% full + methane 450ppm",
            "status": "urgent"
          }
        ]
      },
      "B": { ... },
      "C": { ... }
    }
  }
}
```

**Algorithm Details:**
1. **Phase 1 - Greedy Selection:** Calculate efficiency (priority/distance) for each location
2. **Phase 2 - Safety Override:** Move critical methane locations (>800ppm) to front
3. **Phase 3 - 2-Opt Improvement:** Swap adjacent locations to reduce total travel distance

---

## Simulation

### POST /simulation/advance
Advance simulation time by N hours.

**Request Body:**
```json
{
  "hours": 6
}
```

**Effects per hour (WET bins only):**
- Decomposition: +0.5%
- Methane: Generated based on waste composition
- Fill level: Slight increase from gas expansion

**Response:**
```json
{
  "status": "success",
  "message": "Simulation advanced by 6 hour(s)",
  "current_time": 6,
  "changes": [
    {
      "bin": "A1_WET",
      "location": "A1",
      "decomposition": {"old": 22.5, "new": 25.5},
      "methane": {"old": 125.0, "new": 180.0}
    }
  ],
  "locations": { ... }
}
```

---

### POST /simulation/reset
Reset simulation to initial state.

**Response:**
```json
{
  "status": "success",
  "message": "Simulation reset to initial state",
  "current_time": 0
}
```

---

## Statistics

### GET /statistics
Get system-wide statistics.

**Response:**
```json
{
  "status": "success",
  "statistics": {
    "total_locations": 8,
    "total_bins": 16,
    "wet_bins": 8,
    "dry_bins": 8,
    "urgent_locations": 2,
    "warning_locations": 3,
    "average_fill_level": 38.5,
    "average_methane_level": 145.2,
    "total_weight": 125.5,
    "simulation_time_hours": 6
  }
}
```

---

## Risk Calculations (Environmentally-Correct)

### 🌱 Why This Algorithm Matters

This system prioritizes **environmental impact** over simple fill levels:
- **Methane (CH₄)** is 25× more potent greenhouse gas than CO₂
- Contributes to climate change and ozone layer damage
- Health hazard (explosive, toxic in high concentrations)
- Attracts pests and spreads disease

**Result:** Biodegradable waste (food/organic) gets priority over plastic overflow.

---

### Bin Risk Formulas

**WET Bin (Biodegradable/Organic):**

Prioritizes methane emissions (environmental emergency):

```python
# METHANE RISK (50% weight - greenhouse gas hazard)
if methane > 800 ppm:
    methane_risk = 100  # CRITICAL HEALTH HAZARD
elif methane > 500 ppm:
    methane_risk = 80   # HIGH - urgent collection
elif methane > 300 ppm:
    methane_risk = 60   # MEDIUM
else:
    methane_risk = (methane / 300) × 40

# TOTAL WET RISK
wet_risk = (methane_risk × 0.50) + (decomposition × 0.30) + (fill_level × 0.20)
```

| Factor | Weight | Reason |
|--------|--------|--------|
| Methane Level | **50%** | Greenhouse gas, health hazard |
| Decomposition | **30%** | Speed of methane generation |
| Fill Level | **20%** | Secondary concern |

**DRY Bin (Plastic/Recyclables):**

Capped at 75 max (sanitation concern, not environmental emergency):

```python
dry_risk = min(75, (fill_level × 0.70) + (weight × 0.30))
```

| Factor | Weight | Reason |
|--------|--------|--------|
| Fill Level | **70%** | Overflow/litter prevention |
| Weight | **30%** | Structural integrity |
| **Max Score** | **75** | Less urgent than methane |

---

### Location Risk

**Weighted by Environmental Impact:**

```python
location_risk = (wet_risk × 0.70) + (dry_risk × 0.30)

# METHANE OVERRIDE
if wet_bin.methane > 500 ppm:
    location_risk = max(location_risk, 85)  # Force urgent status
```

| Component | Weight | Reason |
|-----------|--------|--------|
| WET (biodegradable) | **70%** | Environmental/climate priority |
| DRY (plastic) | **30%** | Sanitation concern |

**Override Rule:** If methane > 500 ppm → Location automatically becomes URGENT (risk = 85)

---

### Risk Thresholds
| Score | Status | Color | Action |
|-------|--------|-------|--------|
| > 70 | Urgent | 🔴 Red | Collect within 2 hours |
| 40-70 | Warning | 🟡 Yellow | Collect within 24 hours |
| < 40 | Normal | 🟢 Green | Routine schedule |

**Special:** Methane > 800 ppm = EMERGENCY (immediate collection)

---

### Real-World Impact

| Waste Type | Environmental Impact | Collection Priority |
|-----------|---------------------|-------------------|
| **Food/Organic (WET)** | Methane → Climate change, ozone harm | 🔴 **CRITICAL** |
| **Plastic (DRY)** | Pollution, microplastics, but not greenhouse | 🟡 **MEDIUM** |
| **Paper** | Recyclable, minimal environmental harm | 🟢 **LOW** |

**This algorithm demonstrates:**
- ✅ Environmental awareness (not just operational efficiency)
- ✅ Climate action (prioritize methane prevention)
- ✅ Real-world best practices (aligned with global sustainability goals)
- ✅ Innovation (most waste systems ignore greenhouse gas impact)

---

## Location Structure

| Route | Locations | Distance |
|-------|-----------|----------|
| A | A1, A2, A3 | 8.5 km |
| B | B1, B2, B3 | 12.5 km |
| C | C1, C2 | 6.0 km |

**Each location has:**
- 1 WET bin (💧): Organic waste, methane/decomposition tracking
- 1 DRY bin (📦): Recyclables, weight tracking

---

## Legacy Endpoints

### GET /bins
Returns all bins in flat format (backward compatibility).

```json
{
  "status": "success",
  "time": 0,
  "bins": {
    "A1_WET": { ... },
    "A1_DRY": { ... },
    ...
  }
}
```
