"""
Smart Waste Management System - Backend API
Location-based model: 8 locations × 2 bins each (WET + DRY)
Handles real hardware integration, ML predictions, and route optimization

CRITICAL FEATURES:
- A1 Location = Real hardware bin (accepts ESP32 POST data for both bins)
  - A1_WET: fill_level (ultrasonic), methane (MQ-4 + MQ-135)
  - A1_DRY: weight (HX711)
- All other 14 bins = pure simulation
- ENVIRONMENTALLY-CORRECT risk model: Prioritizes methane (greenhouse gas)
- Methane is GENERATED over time (not immediate)

ENVIRONMENTAL PRIORITY:
- WET bins (biodegradable): 70% weight - methane is 25× more potent than CO2
- DRY bins (plastic): 30% weight - sanitation concern, not climate emergency
- Methane > 500 ppm = URGENT override (health + environmental hazard)
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta    
import random
import os

app = Flask(__name__)
CORS(app)

# Path to frontend folder
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')

# ============================================================
# CONSTANTS & CONFIGURATIONS
# ============================================================

WASTE_TYPES = {
    'food': {'density': 0.8, 'decomposition_rate': 0.15, 'methane_multiplier': 2.0},
    'paper': {'density': 0.3, 'decomposition_rate': 0.08, 'methane_multiplier': 0.5},
    'plastic': {'density': 1.2, 'decomposition_rate': 0.02, 'methane_multiplier': 0.3},
    'organic': {'density': 0.6, 'decomposition_rate': 0.20, 'methane_multiplier': 2.5}
}

ROUTE_INFO = {
    'A': {'name': 'Route A: Central District', 'road': 'Main Street & Park Avenue', 'distance': 8.5},
    'B': {'name': 'Route B: Residential Zone', 'road': 'Oak Road & Elm Street', 'distance': 12.5},
    'C': {'name': 'Route C: Market District', 'road': 'Market Street & Central Plaza', 'distance': 6.0}
}

LOCATION_CONFIGS = {
    'A1': {'name': 'Koregaon Park Corner', 'route': 'A', 'address': 'Koregaon Park, Pune', 'distance_from_depot': 2.5, 'position': (180, 120)},
    'A2': {'name': 'MG Road Junction', 'route': 'A', 'address': 'MG Road, Pune', 'distance_from_depot': 4.0, 'position': (350, 100)},
    'A3': {'name': 'FC Road Plaza', 'route': 'A', 'address': 'FC Road, Pune', 'distance_from_depot': 6.5, 'position': (520, 130)},
    'B1': {'name': 'Aundh IT Park', 'route': 'B', 'address': 'Aundh, Pune', 'distance_from_depot': 3.0, 'position': (200, 320)},
    'B2': {'name': 'Baner Hills', 'route': 'B', 'address': 'Baner, Pune', 'distance_from_depot': 5.5, 'position': (400, 350)},
    'B3': {'name': 'Pashan Lake View', 'route': 'B', 'address': 'Pashan, Pune', 'distance_from_depot': 8.0, 'position': (620, 320)},
    'C1': {'name': 'Deccan Gymkhana', 'route': 'C', 'address': 'Deccan, Pune', 'distance_from_depot': 2.0, 'position': (300, 520)},
    'C2': {'name': 'Shivajinagar Market', 'route': 'C', 'address': 'Shivajinagar, Pune', 'distance_from_depot': 4.5, 'position': (550, 550)}
}

# ============================================================
# IN-MEMORY DATABASE & HARDWARE STATE
# ============================================================

locations_db = {}
simulation_time = 0

# CRITICAL: Hardware connection tracking for A1_WET
hardware_connected = False
last_hardware_update = None
HARDWARE_TIMEOUT_SECONDS = 30  # If no data for 30s, consider disconnected


def is_hardware_active():
    """Check if hardware is currently active (received data recently)"""
    global hardware_connected, last_hardware_update
    if not hardware_connected or last_hardware_update is None:
        return False
    # Check if last update was within timeout
    elapsed = (datetime.now() - last_hardware_update).total_seconds()
    if elapsed > HARDWARE_TIMEOUT_SECONDS:
        hardware_connected = False
        return False
    return True


def create_bin(bin_id, bin_type, is_hardware=False):
    """Create a bin with demo-ready initial values"""
    loc_id = bin_id.split('_')[0]
    
    # A1 specific values for demo flow - both bins connected to hardware
    if loc_id == 'A1':
        if bin_type == 'wet':
            return {
                'id': bin_id,
                'type': 'wet',
                'fill_level': 30.0,
                'methane': 100.0,
                'decomposition': 20.0,
                'waste_composition': {'food': 2, 'paper': 0, 'plastic': 0, 'organic': 1},
                'is_real_hardware': True,  # A1_WET: ultrasonic + MQ-4 + MQ-135
                'last_updated': datetime.now().isoformat()
            }
        else:
            return {
                'id': bin_id,
                'type': 'dry',
                'fill_level': 50.0,
                'weight': 1500.0,  # Weight in GRAMS
                'waste_composition': {'food': 0, 'paper': 3, 'plastic': 2, 'organic': 0},
                'is_real_hardware': True,  # A1_DRY: HX711 weight sensor
                'last_updated': datetime.now().isoformat()
            }
    
    # Other locations - random initial values
    if bin_type == 'wet':
        return {
            'id': bin_id,
            'type': 'wet',
            'fill_level': random.uniform(20, 45),
            'methane': random.uniform(60, 150),
            'decomposition': random.uniform(15, 35),
            'waste_composition': {'food': random.randint(1, 3), 'paper': 0, 'plastic': 0, 'organic': random.randint(0, 2)},
            'is_real_hardware': False,
            'last_updated': datetime.now().isoformat()
        }
    else:
        return {
            'id': bin_id,
            'type': 'dry',
            'fill_level': random.uniform(25, 50),
            'weight': random.uniform(1000, 3000),  # Weight in GRAMS
            'waste_composition': {'food': 0, 'paper': random.randint(1, 3), 'plastic': random.randint(1, 2), 'organic': 0},
            'is_real_hardware': False,
            'last_updated': datetime.now().isoformat()
        }


def initialize_locations():
    """Initialize 8 locations, each with 2 bins (WET + DRY)"""
    global locations_db, hardware_connected, last_hardware_update
    locations_db = {}
    hardware_connected = False
    last_hardware_update = None
    
    for loc_id, config in LOCATION_CONFIGS.items():
        is_hardware_wet = (loc_id == 'A1')  # ONLY A1_WET is hardware
        
        locations_db[loc_id] = {
            'id': loc_id,
            'name': config['name'],
            'route': config['route'],
            'address': config['address'],
            'distance_from_depot': config['distance_from_depot'],
            'position': config['position'],
            'bins': {
                f'{loc_id}_WET': create_bin(f'{loc_id}_WET', 'wet', is_hardware_wet),
                f'{loc_id}_DRY': create_bin(f'{loc_id}_DRY', 'dry', False)
            },
            'last_updated': datetime.now().isoformat()
        }


initialize_locations()

# ============================================================
# RISK CALCULATION FUNCTIONS (ENVIRONMENTALLY-CORRECT)
# ============================================================

def calculate_bin_risk(bin_data):
    """
    Calculate risk score for a single bin (0-100 scale)
    
    ENVIRONMENTALLY-CORRECT ALGORITHM:
    - Prioritizes METHANE (greenhouse gas 25× more potent than CO2)
    - Plastic/dry waste is important but less urgent (doesn't harm climate)
    
    WET (Biodegradable): methane × 0.50 + decomposition × 0.30 + fill × 0.20
    DRY (Recyclables): Capped at 75 max (less urgent than methane hazard)
    """
    if bin_data['type'] == 'wet':
        # FACTOR 1: METHANE is PRIMARY (50% weight - greenhouse gas hazard)
        methane_ppm = bin_data['methane']
        if methane_ppm > 800:
            methane_risk = 100  # CRITICAL HEALTH HAZARD
        elif methane_ppm > 500:
            methane_risk = 80   # HIGH - urgent collection needed
        elif methane_ppm > 300:
            methane_risk = 60   # MEDIUM - needs attention
        else:
            methane_risk = (methane_ppm / 300) * 40  # LOW - proportional
        
        # FACTOR 2: DECOMPOSITION SPEED (30% weight - how fast it's generating methane)
        decomposition_risk = bin_data['decomposition'] * 0.30
        
        # FACTOR 3: FILL LEVEL (20% weight - secondary concern)
        fill_risk = bin_data['fill_level'] * 0.20
        
        # WET BIN TOTAL RISK (Environmental priority)
        wet_risk = (methane_risk * 0.50) + decomposition_risk + fill_risk
        return min(100, wet_risk)
    
    else:
        # DRY BIN (Plastic/Recyclables)
        # FACTOR 1: FILL LEVEL (70% weight - main concern is overflow/sanitation)
        fill_risk = bin_data['fill_level'] * 0.70
        
        # FACTOR 2: WEIGHT (30% weight - structural risk) - weight in grams, max 10kg
        weight_risk = (min(bin_data['weight'], 10000) / 10000) * 30
        
        # DRY BIN TOTAL RISK (Capped at 75 - plastic doesn't harm environment as urgently)
        dry_risk = fill_risk + weight_risk
        return min(75, dry_risk)  # Cap at 75: sanitation concern, not environmental emergency


def calculate_location_risk(location):
    """
    CRITICAL: Location risk prioritizes ENVIRONMENTAL IMPACT
    
    WET (biodegradable) waste = 70% weight (methane is greenhouse gas)
    DRY (plastic) waste = 30% weight (sanitation concern, not climate emergency)
    
    OVERRIDE RULE: If methane > 500 ppm → location_risk = 85 (URGENT)
    """
    wet_bin = location['bins'].get(f"{location['id']}_WET")
    dry_bin = location['bins'].get(f"{location['id']}_DRY")
    
    wet_risk = calculate_bin_risk(wet_bin) if wet_bin else 0
    dry_risk = calculate_bin_risk(dry_bin) if dry_bin else 0
    
    # Calculate weighted risk (70% environmental, 30% sanitation)
    location_risk = (wet_risk * 0.70) + (dry_risk * 0.30)
    
    # METHANE OVERRIDE: If methane > 500 ppm, treat as urgent regardless
    if wet_bin and wet_bin['methane'] > 500:
        location_risk = max(location_risk, 85)  # Force urgent status
    
    return min(100, location_risk)


def get_risk_status(risk_score):
    """Get risk status based on score"""
    if risk_score > 70:
        return 'urgent'
    elif risk_score > 40:
        return 'warning'
    return 'normal'


def generate_bin_alerts(bin_data):
    """Generate alerts for a bin"""
    alerts = []
    
    if bin_data['fill_level'] > 85:
        alerts.append({'type': 'fill_critical', 'message': f"Fill level {bin_data['fill_level']:.1f}% - URGENT", 'severity': 'critical'})
    elif bin_data['fill_level'] > 70:
        alerts.append({'type': 'fill_warning', 'message': f"Fill level {bin_data['fill_level']:.1f}% - HIGH", 'severity': 'warning'})
    
    if bin_data['type'] == 'wet':
        if bin_data['methane'] > 500:
            alerts.append({'type': 'methane_critical', 'message': f"Methane {bin_data['methane']:.1f} ppm - HAZARD", 'severity': 'critical'})
        elif bin_data['methane'] > 300:
            alerts.append({'type': 'methane_warning', 'message': f"Methane {bin_data['methane']:.1f} ppm - ELEVATED", 'severity': 'warning'})
        if bin_data['decomposition'] > 80:
            alerts.append({'type': 'decomp_high', 'message': "Advanced decomposition - odor risk", 'severity': 'warning'})
    
    return alerts


# ============================================================
# API ENDPOINTS - LOCATIONS
# ============================================================

@app.route('/api/locations', methods=['GET'])
def get_all_locations():
    """Get all locations with current status"""
    response_locations = {}
    
    for loc_id, location in locations_db.items():
        for bin_id, bin_data in location['bins'].items():
            bin_data['risk_score'] = round(calculate_bin_risk(bin_data), 1)
            bin_data['alerts'] = generate_bin_alerts(bin_data)
            bin_data['status'] = get_risk_status(bin_data['risk_score'])
        
        location_risk = calculate_location_risk(location)
        
        response_locations[loc_id] = {
            **location,
            'location_risk': round(location_risk, 1),
            'status': get_risk_status(location_risk)
        }
    
    return jsonify({
        'status': 'success',
        'time': simulation_time,
        'hardware_connected': is_hardware_active(),
        'locations': response_locations
    })


@app.route('/api/locations/<location_id>', methods=['GET'])
def get_location(location_id):
    """Get specific location details"""
    if location_id not in locations_db:
        return jsonify({'status': 'error', 'message': 'Location not found'}), 404
    
    location = locations_db[location_id]
    
    for bin_id, bin_data in location['bins'].items():
        bin_data['risk_score'] = round(calculate_bin_risk(bin_data), 1)
        bin_data['alerts'] = generate_bin_alerts(bin_data)
        bin_data['status'] = get_risk_status(bin_data['risk_score'])
    
    location_risk = calculate_location_risk(location)
    
    return jsonify({
        'status': 'success',
        'hardware_connected': is_hardware_active(),
        'location': {
            **location,
            'location_risk': round(location_risk, 1),
            'status': get_risk_status(location_risk)
        }
    })


@app.route('/api/locations/<location_id>/bins/<bin_id>/add-waste', methods=['POST'])
def add_waste_to_bin(location_id, bin_id):
    """
    Add waste to a specific bin
    CRITICAL: Methane is NOT increased immediately - only through time advancement
    DRY bins: Only accept paper/plastic
    EDGE CASE: Cannot add waste if bin is already full (>=95%)
    """
    if location_id not in locations_db:
        return jsonify({'status': 'error', 'message': 'Location not found'}), 404
    
    location = locations_db[location_id]
    
    if bin_id not in location['bins']:
        return jsonify({'status': 'error', 'message': 'Bin not found'}), 404
    
    data = request.json
    waste_type = data.get('type', 'food')
    quantity = data.get('quantity', 2)
    
    if waste_type not in WASTE_TYPES:
        return jsonify({'status': 'error', 'message': 'Invalid waste type'}), 400
    
    if quantity < 1 or quantity > 20:
        return jsonify({'status': 'error', 'message': 'Quantity must be 1-20 kg'}), 400
    
    bin_data = location['bins'][bin_id]
    waste_config = WASTE_TYPES[waste_type]
    
    # ===== EDGE CASE: BIN ALREADY FULL =====
    if bin_data['fill_level'] >= 100:
        return jsonify({
            'status': 'error',
            'message': f'🚫 Bin {bin_id} is FULL (100%)! Cannot add more waste. Please empty the bin first.',
            'bin_id': bin_id,
            'current_fill': bin_data['fill_level'],
            'alert_type': 'bin_full'
        }), 400
    
    # ===== EDGE CASE: BIN NEARLY FULL - Check if waste will overflow =====
    fill_increase = quantity * 8  # Each kg adds ~8% fill
    projected_fill = bin_data['fill_level'] + fill_increase
    
    if bin_data['fill_level'] >= 95:
        return jsonify({
            'status': 'error',
            'message': f'⚠️ Bin {bin_id} is almost full ({bin_data["fill_level"]:.1f}%)! Cannot add {quantity}kg. Please empty the bin first.',
            'bin_id': bin_id,
            'current_fill': bin_data['fill_level'],
            'requested_quantity': quantity,
            'alert_type': 'bin_nearly_full'
        }), 400
    
    # ===== EDGE CASE: Adding this much would overflow =====
    if projected_fill > 100:
        max_quantity = int((100 - bin_data['fill_level']) / 8)
        if max_quantity <= 0:
            return jsonify({
                'status': 'error',
                'message': f'🚫 Bin {bin_id} is too full ({bin_data["fill_level"]:.1f}%)! Cannot add more waste.',
                'bin_id': bin_id,
                'current_fill': bin_data['fill_level'],
                'alert_type': 'bin_overflow_prevented'
            }), 400
        return jsonify({
            'status': 'error',
            'message': f'⚠️ Adding {quantity}kg would overflow bin {bin_id}! Current: {bin_data["fill_level"]:.1f}%, Max you can add: {max_quantity}kg',
            'bin_id': bin_id,
            'current_fill': bin_data['fill_level'],
            'requested_quantity': quantity,
            'max_allowed_quantity': max_quantity,
            'projected_fill': projected_fill,
            'alert_type': 'overflow_warning'
        }), 400
    
    # Store old values
    old_fill = bin_data['fill_level']
    old_risk = calculate_bin_risk(bin_data)
    old_location_risk = calculate_location_risk(location)
    
    if bin_data['type'] == 'dry':
        # DRY BIN: Only accept paper and plastic
        if waste_type not in ['paper', 'plastic']:
            return jsonify({
                'status': 'error', 
                'message': f'DRY bins cannot accept {waste_type}. Only paper and plastic allowed.'
            }), 400
        
        # Update fill and weight
        bin_data['fill_level'] = min(100, bin_data['fill_level'] + quantity * 8)
        bin_data['weight'] = min(100, bin_data['weight'] + quantity * waste_config['density'])
        bin_data['waste_composition'][waste_type] += quantity
    
    else:
        # WET BIN: Accept all waste types
        bin_data['fill_level'] = min(100, bin_data['fill_level'] + quantity * 8)
        bin_data['waste_composition'][waste_type] += quantity
        
        # Decomposition starts immediately (based on waste type)
        decomp_increase = quantity * waste_config['decomposition_rate']
        bin_data['decomposition'] = min(100, bin_data['decomposition'] + decomp_increase)
        
        # CRITICAL: Methane is NOT set immediately
        # It will be generated during time advancement based on waste_composition
    
    bin_data['last_updated'] = datetime.now().isoformat()
    location['last_updated'] = datetime.now().isoformat()
    
    # Calculate new risks
    new_risk = calculate_bin_risk(bin_data)
    new_location_risk = calculate_location_risk(location)
    
    return jsonify({
        'status': 'success',
        'message': f'Added {quantity}kg of {waste_type} to {bin_id}',
        'changes': {
            'fill_level': {'old': round(old_fill, 1), 'new': round(bin_data['fill_level'], 1)},
            'bin_risk': {'old': round(old_risk, 1), 'new': round(new_risk, 1)},
            'location_risk': {'old': round(old_location_risk, 1), 'new': round(new_location_risk, 1)}
        },
        'bin': {
            **bin_data,
            'risk_score': round(new_risk, 1),
            'status': get_risk_status(new_risk)
        },
        'location_risk': round(new_location_risk, 1),
        'location_status': get_risk_status(new_location_risk)
    })


@app.route('/api/locations/<location_id>/bins/<bin_id>/empty', methods=['POST'])
def empty_bin(location_id, bin_id):
    """Empty a specific bin (simulate collection)"""
    if location_id not in locations_db:
        return jsonify({'status': 'error', 'message': 'Location not found'}), 404
    
    location = locations_db[location_id]
    
    if bin_id not in location['bins']:
        return jsonify({'status': 'error', 'message': 'Bin not found'}), 404
    
    bin_data = location['bins'][bin_id]
    old_fill = bin_data['fill_level']
    old_risk = calculate_bin_risk(bin_data)
    
    # Empty the bin
    bin_data['fill_level'] = 0
    bin_data['waste_composition'] = {'food': 0, 'paper': 0, 'plastic': 0, 'organic': 0}
    
    if bin_data['type'] == 'wet':
        bin_data['methane'] = max(0, bin_data['methane'] * 0.1)  # Residual
        bin_data['decomposition'] = 0
    else:
        bin_data['weight'] = 0
    
    bin_data['last_updated'] = datetime.now().isoformat()
    new_risk = calculate_bin_risk(bin_data)
    
    return jsonify({
        'status': 'success',
        'message': f'Bin {bin_id} emptied',
        'changes': {
            'fill_level': {'old': round(old_fill, 1), 'new': 0},
            'risk': {'old': round(old_risk, 1), 'new': round(new_risk, 1)}
        },
        'bin': {**bin_data, 'risk_score': round(new_risk, 1), 'status': get_risk_status(new_risk)},
        'location_risk': round(calculate_location_risk(location), 1)
    })


@app.route('/api/locations/<location_id>/collect', methods=['POST'])
def collect_location(location_id):
    """Collect both bins at a location (full truck stop)"""
    if location_id not in locations_db:
        return jsonify({'status': 'error', 'message': 'Location not found'}), 404
    
    location = locations_db[location_id]
    old_risk = calculate_location_risk(location)
    collected_data = {}
    
    for bin_id, bin_data in location['bins'].items():
        old_fill = bin_data['fill_level']
        
        bin_data['fill_level'] = 0
        bin_data['waste_composition'] = {'food': 0, 'paper': 0, 'plastic': 0, 'organic': 0}
        
        if bin_data['type'] == 'wet':
            bin_data['methane'] = max(0, bin_data['methane'] * 0.1)
            bin_data['decomposition'] = 0
        else:
            bin_data['weight'] = 0
        
        bin_data['last_updated'] = datetime.now().isoformat()
        collected_data[bin_id] = {'old_fill': round(old_fill, 1), 'type': bin_data['type']}
    
    location['last_updated'] = datetime.now().isoformat()
    new_risk = calculate_location_risk(location)
    
    return jsonify({
        'status': 'success',
        'message': f'Location {location_id} fully collected',
        'collected': collected_data,
        'risk_change': {'old': round(old_risk, 1), 'new': round(new_risk, 1)}
    })


# ============================================================
# API ENDPOINTS - HARDWARE (ESP32)
# ============================================================

@app.route('/api/locations/A1/hardware', methods=['POST'])
def update_a1_from_hardware():
    """
    Accept real ESP32 sensor data for A1 location
    Updates both A1_WET and A1_DRY bins from sensor readings:
    - A1_WET: methane (MQ-4 + MQ-135)
    - A1_DRY: fill_level (ultrasonic), weight (HX711)
    Expected JSON: {"fill_level": 45.3, "methane": 250, "weight": 1500}
    Note: weight is sent in GRAMS from ESP32, converted to KG here
    """
    global hardware_connected, last_hardware_update
    
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'No data received'}), 400
    
    wet_bin = locations_db['A1']['bins']['A1_WET']
    dry_bin = locations_db['A1']['bins']['A1_DRY']
    
    # Update A1_WET: methane from MQ-4 + MQ-135
    if 'methane' in data:
        wet_bin['methane'] = min(1000, max(0, float(data['methane'])))
    
    # Update A1_DRY: fill_level from ultrasonic, weight from HX711 (grams to kg)
    if 'fill_level' in data:
        dry_bin['fill_level'] = min(100, max(0, float(data['fill_level'])))
    
    # Only update weight if valid reading received (not 0 or missing)
    if 'weight' in data:
        weight_grams = float(data['weight'])
        if weight_grams > 0:  # Ignore 0 readings (sensor failure)
            dry_bin['weight'] = round(weight_grams, 1)  # Store in GRAMS for precision
    
    # Mark hardware as connected
    hardware_connected = True
    last_hardware_update = datetime.now()
    wet_bin['last_updated'] = datetime.now().isoformat()
    dry_bin['last_updated'] = datetime.now().isoformat()
    
    # Log received data for debugging
    print(f"[HARDWARE] A1_DRY: fill={data.get('fill_level')}%, weight={data.get('weight')}g -> stored {dry_bin['weight']}g | A1_WET: methane={data.get('methane')}ppm")
    
    return jsonify({
        'status': 'success',
        'message': 'A1 bins updated from ESP32 hardware',
        'hardware_connected': True,
        'wet_bin': wet_bin,
        'dry_bin': dry_bin,
        'location_risk': round(calculate_location_risk(locations_db['A1']), 1)
    })


@app.route('/api/hardware/status', methods=['GET'])
def get_hardware_status():
    """Check if hardware is connected and active"""
    return jsonify({
        'status': 'success',
        'hardware_connected': is_hardware_active(),
        'last_update': last_hardware_update.isoformat() if last_hardware_update else None,
        'timeout_seconds': HARDWARE_TIMEOUT_SECONDS
    })


# ============================================================
# API ENDPOINTS - ROUTES & OPTIMIZATION
# ============================================================

@app.route('/api/routes', methods=['GET'])
def get_routes():
    """Get all routes with their locations"""
    routes_response = {}
    
    for route_id, route_info in ROUTE_INFO.items():
        route_locations = {k: v for k, v in locations_db.items() if v['route'] == route_id}
        
        for loc_id, location in route_locations.items():
            for bin_id, bin_data in location['bins'].items():
                bin_data['risk_score'] = round(calculate_bin_risk(bin_data), 1)
            location['location_risk'] = round(calculate_location_risk(location), 1)
            location['status'] = get_risk_status(location['location_risk'])
        
        routes_response[route_id] = {
            'id': route_id,
            'name': route_info['name'],
            'road': route_info['road'],
            'distance': route_info['distance'],
            'locations': route_locations
        }
    
    return jsonify({'status': 'success', 'routes': routes_response})


# ============================================================
# ADVANCED ROUTE OPTIMIZATION - GREEDY NEAREST NEIGHBOR + 2-OPT
# ============================================================

def explain_priority(location_detail):
    """Generate human-readable explanation for why a location has its priority"""
    loc = location_detail['location']
    priority = location_detail['priority_score']
    
    wet_bin = loc['bins'].get(f"{loc['id']}_WET")
    dry_bin = loc['bins'].get(f"{loc['id']}_DRY")
    
    reasons = []
    
    if wet_bin and wet_bin['methane'] > 800:
        reasons.append(f"🚨 CRITICAL METHANE: {wet_bin['methane']:.0f} ppm (HAZARD)")
    elif wet_bin and wet_bin['fill_level'] > 85:
        reasons.append(f"🔴 URGENT: {wet_bin['fill_level']:.1f}% full + methane {wet_bin['methane']:.0f}ppm")
    elif dry_bin and dry_bin['fill_level'] > 85:
        reasons.append(f"🔴 DRY URGENT: {dry_bin['fill_level']:.1f}% full, {dry_bin['weight']:.1f}kg")
    elif priority > 60:
        reasons.append(f"🟡 WARNING: Risk {priority:.1f}")
    else:
        reasons.append(f"🟢 OK: Risk {priority:.1f}")
    
    return " | ".join(reasons) if reasons else f"Priority: {priority:.1f}"


def generate_route_explanation(best_route_detail):
    """Generate detailed explanation of why this route is optimal"""
    explanation = f"""
Route {best_route_detail['route_id']} is OPTIMAL:

📍 Collection Order: {' → '.join(best_route_detail['collection_order'])} → Depot

Key Factors:
✅ Average Priority Score: {best_route_detail['avg_priority']:.1f}/100
✅ Urgent Locations: {best_route_detail['urgent_locations']} (must collect)
✅ Total Distance: {best_route_detail['total_distance']:.1f} km
✅ Efficiency Score: {best_route_detail['score']:.2f}

Why each location is in this order:
"""
    for detail in best_route_detail['location_details']:
        explanation += f"\n  {detail['id']}: {detail['reason']}"
    
    return explanation


def calculate_route_distance(route_locations, depot_distance_first, depot_distance_last):
    """
    Calculate total route distance for a given order of locations
    Depot → first location → ... → last location → Depot
    """
    if not route_locations:
        return 0
    
    total = depot_distance_first  # Depot to first
    
    # Between consecutive locations (simplified: use average of their depot distances as approximation)
    for i in range(len(route_locations) - 1):
        # Approximate inter-location distance
        dist_i = route_locations[i]['distance_from_depot']
        dist_j = route_locations[i + 1]['distance_from_depot']
        inter_distance = abs(dist_j - dist_i) * 0.8  # 80% of difference as approximation
        total += inter_distance
    
    total += depot_distance_last  # Last to depot
    return total


def two_opt_improve(location_priorities, max_iterations=50):
    """
    2-Opt local search improvement
    Try swapping segments to reduce total travel distance
    """
    if len(location_priorities) <= 2:
        return location_priorities
    
    best_order = location_priorities[:]
    improved = True
    iteration = 0
    
    while improved and iteration < max_iterations:
        improved = False
        
        for i in range(1, len(best_order) - 1):
            for j in range(i + 1, len(best_order)):
                # Try reversing segment [i:j+1]
                new_order = best_order[:i] + best_order[i:j+1][::-1] + best_order[j+1:]
                
                # Calculate distances for comparison
                old_dist = sum(lp['distance'] for lp in best_order)
                new_dist = sum(lp['distance'] for lp in new_order)
                
                # Keep if shorter (with priority consideration)
                old_priority_penalty = sum(1 for idx, lp in enumerate(best_order) if lp['is_critical_methane'] and idx > 0) * 10
                new_priority_penalty = sum(1 for idx, lp in enumerate(new_order) if lp['is_critical_methane'] and idx > 0) * 10
                
                if (new_dist + new_priority_penalty) < (old_dist + old_priority_penalty):
                    best_order = new_order
                    improved = True
                    break
            
            if improved:
                break
        
        iteration += 1
    
    return best_order


@app.route('/api/routes/optimize', methods=['GET'])
def optimize_routes():
    """
    ADVANCED Route Optimization using Greedy Nearest Neighbor + 2-Opt
    
    FACTORS (weighted):
    - Risk Score: 35% (max of WET/DRY risk)
    - Fill Level Urgency: 25% (fill × decomposition factor)
    - Distance Efficiency: 20% (priority/distance ratio)
    - Time Window: 15% (current urgency vs deadline)
    - Methane Safety: 5% (with OVERRIDE if >800 ppm)
    
    ALGORITHM:
    1. Calculate priority score for each location
    2. Sort by efficiency (priority/distance)
    3. Critical methane locations FIRST (safety override)
    4. Apply 2-Opt improvement to reduce travel distance
    5. Select best route based on composite score
    """
    route_scores = {}
    current_hour = (simulation_time % 24) if simulation_time else 9  # Default 9am
    
    for route_id in ['A', 'B', 'C']:
        locations = [loc for loc in locations_db.values() if loc['route'] == route_id]
        
        if not locations:
            continue
        
        # ===== CALCULATE LOCATION PRIORITIES =====
        location_priorities = []
        
        for location in locations:
            wet_bin = location['bins'].get(f"{location['id']}_WET")
            dry_bin = location['bins'].get(f"{location['id']}_DRY")
            
            # FACTOR 1: Risk Score (35%)
            location_risk = calculate_location_risk(location)
            risk_factor = location_risk * 0.35
            
            # FACTOR 2: Fill Level Urgency (25%)
            wet_fill_urgency = 0
            dry_fill_urgency = 0
            
            if wet_bin:
                decomposition_multiplier = 1 + (wet_bin['decomposition'] / 100)
                wet_fill_urgency = (wet_bin['fill_level'] / 100) * decomposition_multiplier
            
            if dry_bin:
                dry_fill_urgency = dry_bin['fill_level'] / 100
            
            fill_urgency_factor = max(wet_fill_urgency, dry_fill_urgency) * 100 * 0.25
            
            # FACTOR 3: Methane Safety (5% but OVERRIDE if critical)
            methane_factor = 0
            methane_override = False
            
            if wet_bin:
                if wet_bin['methane'] > 800:
                    methane_factor = 100  # CRITICAL - becomes top priority
                    methane_override = True
                elif wet_bin['methane'] > 500:
                    methane_factor = 50 * 0.05
                else:
                    methane_factor = (wet_bin['methane'] / 1000) * 100 * 0.05
            
            # FACTOR 4: Time Window (15%)
            # Simulate urgency based on fill level and decomposition
            time_urgency = 0
            if wet_bin and wet_bin['fill_level'] > 70:
                hours_until_full = max(1, (100 - wet_bin['fill_level']) / 5)  # ~5% per hour
                if hours_until_full < 4:
                    time_urgency = 80
                elif hours_until_full < 8:
                    time_urgency = 50
                else:
                    time_urgency = 20
            
            if dry_bin and dry_bin['fill_level'] > 75:
                time_urgency = max(time_urgency, 60)
            
            time_factor = time_urgency * 0.15
            
            # FACTOR 5: Distance (20%) - used for efficiency calculation
            distance_to_location = location['distance_from_depot']
            
            # PRIORITY SCORE = Risk + Fill + Methane + Time
            priority_score = risk_factor + fill_urgency_factor + methane_factor + time_factor
            
            # EFFICIENCY = Priority / Distance (want high priority, low distance)
            if distance_to_location > 0:
                efficiency = priority_score / distance_to_location
            else:
                efficiency = priority_score
            
            # Distance factor for route score (20%)
            distance_factor = (10 / (1 + distance_to_location)) * 0.20 * 100
            priority_score += distance_factor
            
            location_priorities.append({
                'location': location,
                'priority_score': priority_score,
                'risk_score': location_risk,
                'fill_urgency': max(wet_fill_urgency, dry_fill_urgency) * 100,
                'methane_level': wet_bin['methane'] if wet_bin else 0,
                'distance': distance_to_location,
                'efficiency': efficiency,
                'is_critical_methane': methane_override,
                'time_urgency': time_urgency
            })
        
        # ===== SORT BY EFFICIENCY (greedy nearest neighbor) =====
        # Critical methane locations FIRST (safety override)
        critical = [l for l in location_priorities if l['is_critical_methane']]
        normal = [l for l in location_priorities if not l['is_critical_methane']]
        
        critical.sort(key=lambda x: x['efficiency'], reverse=True)
        normal.sort(key=lambda x: x['efficiency'], reverse=True)
        
        sorted_locations = critical + normal
        
        # ===== APPLY 2-OPT IMPROVEMENT =====
        sorted_locations = two_opt_improve(sorted_locations)
        
        # ===== CALCULATE ROUTE QUALITY SCORE =====
        avg_priority = sum(l['priority_score'] for l in sorted_locations) / len(sorted_locations)
        urgent_count = sum(1 for l in sorted_locations if l['priority_score'] > 60 or l['is_critical_methane'])
        warning_count = sum(1 for l in sorted_locations if 40 < l['priority_score'] <= 60 and not l['is_critical_methane'])
        total_distance = sum(l['distance'] for l in sorted_locations)
        max_risk = max(l['risk_score'] for l in sorted_locations)
        
        # ROUTE SCORE = (avg_priority × 0.6 + urgent_count × 20) / (1 + total_distance × 0.02)
        route_score = (avg_priority * 0.6 + urgent_count * 20) / (1 + total_distance * 0.02)
        
        # Build collection order and details
        collection_order = [l['location']['id'] for l in sorted_locations]
        location_details = [
            {
                'id': l['location']['id'],
                'name': l['location']['name'],
                'priority': round(l['priority_score'], 1),
                'risk': round(l['risk_score'], 1),
                'efficiency': round(l['efficiency'], 2),
                'distance': l['distance'],
                'methane': round(l['methane_level'], 1),
                'fill_urgency': round(l['fill_urgency'], 1),
                'is_critical': l['is_critical_methane'],
                'reason': explain_priority(l),
                'status': get_risk_status(l['risk_score'])
            }
            for l in sorted_locations
        ]
        
        route_scores[route_id] = {
            'route_id': route_id,
            'name': ROUTE_INFO[route_id]['name'],
            'road': ROUTE_INFO[route_id]['road'],
            'score': round(route_score, 2),
            'avg_priority': round(avg_priority, 1),
            'max_risk': round(max_risk, 1),
            'urgent_locations': urgent_count,
            'warning_locations': warning_count,
            'locations_count': len(sorted_locations),
            'total_distance': round(total_distance, 1),
            'collection_order': collection_order,
            'location_details': location_details,
            # Legacy fields for compatibility
            'avg_risk': round(avg_priority, 1),
            'urgent_count': urgent_count,
            'warning_count': warning_count,
            'distance_km': round(total_distance, 1),
            'optimization_score': round(route_score, 2),
            'locations': location_details
        }
    
    # ===== SELECT BEST ROUTE =====
    best_route = max(route_scores.items(), key=lambda x: x[1]['score'])
    best_id = best_route[0]
    best_data = best_route[1]
    
    # Generate detailed comparison
    comparison_parts = []
    for rid, rdata in route_scores.items():
        marker = "→ BEST" if rid == best_id else ""
        comparison_parts.append(
            f"Route {rid}: score={rdata['score']}, urgent={rdata['urgent_locations']}, "
            f"avg_priority={rdata['avg_priority']}, distance={rdata['total_distance']}km {marker}"
        )
    
    # Collection order string
    if best_data['collection_order']:
        order_str = " → ".join(best_data['collection_order'])
        collection_msg = f"Recommended collection: {order_str} → Depot"
    else:
        collection_msg = "No collections needed"
    
    # Build reason with factor breakdown
    critical_locs = [d for d in best_data['location_details'] if d['is_critical']]
    critical_msg = ""
    if critical_locs:
        critical_names = ", ".join([f"{d['id']} ({d['methane']:.0f}ppm)" for d in critical_locs])
        critical_msg = f" CRITICAL METHANE at {critical_names}!"
    
    reason = (
        f"Route {best_id} selected with highest optimization score ({best_data['score']}).{critical_msg} "
        f"Has {best_data['urgent_locations']} urgent + {best_data['warning_locations']} warning locations. "
        f"Average priority: {best_data['avg_priority']}, Max risk: {best_data['max_risk']}. "
        f"Total distance: {best_data['total_distance']}km. {collection_msg}"
    )
    
    # Generate full explanation
    explanation = generate_route_explanation(best_data)
    
    return jsonify({
        'status': 'success',
        'optimization': {
            'best_route': best_id,
            'best_route_name': best_data['name'],
            'reason': reason,
            'explanation': explanation,
            'collection_order': best_data['collection_order'],
            'urgent_locations': [d for d in best_data['location_details'] if d['priority'] > 60 or d['is_critical']],
            'algorithm': 'Greedy Nearest Neighbor + 2-Opt Improvement',
            'formula': {
                'priority': '(risk × 0.35) + (fill_urgency × 0.25) + (methane × 0.05) + (time_window × 0.15) + (distance_efficiency × 0.20)',
                'route_score': '(avg_priority × 0.6 + urgent_count × 20) / (1 + total_distance × 0.02)'
            },
            'factors': {
                'risk_weight': '35%',
                'fill_urgency_weight': '25%',
                'distance_efficiency_weight': '20%',
                'time_window_weight': '15%',
                'methane_safety_weight': '5% (with OVERRIDE if >800ppm)'
            },
            'comparison': comparison_parts,
            'all_routes': route_scores
        }
    })


# ============================================================
# API ENDPOINTS - SIMULATION
# ============================================================

@app.route('/api/simulation/advance', methods=['POST'])
def advance_simulation():
    """
    Advance simulation by N hours
    CRITICAL: 
    - Skip A1_WET if hardware is connected (use real data)
    - Decomposition increases 0.5 per hour
    - Methane GENERATED based on waste_composition (not immediate)
    """
    global simulation_time
    
    data = request.json
    hours = data.get('hours', 1)
    simulation_time += hours
    
    changes = []
    hw_active = is_hardware_active()
    
    for loc_id, location in locations_db.items():
        for bin_id, bin_data in location['bins'].items():
            
            # CRITICAL: Skip A1_WET if hardware connected
            if bin_id == 'A1_WET' and hw_active:
                changes.append({
                    'bin': bin_id,
                    'location': loc_id,
                    'skipped': True,
                    'reason': 'Hardware connected - using real sensor data'
                })
                continue
            
            if bin_data['type'] == 'wet':
                old_decomp = bin_data['decomposition']
                old_methane = bin_data['methane']
                
                # Decomposition increases 0.5% per hour (only if bin has waste)
                if bin_data['fill_level'] > 0:
                    bin_data['decomposition'] = min(100, bin_data['decomposition'] + 0.5 * hours)
                
                # Methane GENERATED based on waste_composition
                decomp_factor = bin_data['decomposition'] / 100
                total_waste = sum(bin_data['waste_composition'].values())
                
                if total_waste > 0:
                    methane_generated = 0
                    for waste_type, qty in bin_data['waste_composition'].items():
                        if qty > 0:
                            methane_generated += qty * WASTE_TYPES[waste_type]['methane_multiplier'] * decomp_factor
                    
                    # Add generated methane (scaled by hours and 0.1 factor)
                    bin_data['methane'] = min(1000, bin_data['methane'] + methane_generated * 0.1 * hours)
                
                if old_decomp != bin_data['decomposition'] or old_methane != bin_data['methane']:
                    changes.append({
                        'bin': bin_id,
                        'location': loc_id,
                        'decomposition': {'old': round(old_decomp, 1), 'new': round(bin_data['decomposition'], 1)},
                        'methane': {'old': round(old_methane, 1), 'new': round(bin_data['methane'], 1)}
                    })
            
            bin_data['last_updated'] = datetime.now().isoformat()
        location['last_updated'] = datetime.now().isoformat()
    
    # Build response with updated locations
    response_locations = {}
    for loc_id, location in locations_db.items():
        for bin_id, bin_data in location['bins'].items():
            bin_data['risk_score'] = round(calculate_bin_risk(bin_data), 1)
            bin_data['status'] = get_risk_status(bin_data['risk_score'])
        
        location_risk = calculate_location_risk(location)
        response_locations[loc_id] = {
            **location,
            'location_risk': round(location_risk, 1),
            'status': get_risk_status(location_risk)
        }
    
    return jsonify({
        'status': 'success',
        'message': f'Simulation advanced by {hours} hour(s)',
        'current_time': simulation_time,
        'hardware_connected': hw_active,
        'changes': changes,
        'locations': response_locations
    })


@app.route('/api/simulation/reset', methods=['POST'])
def reset_simulation():
    """Reset simulation to initial state"""
    global simulation_time
    simulation_time = 0
    initialize_locations()
    
    return jsonify({
        'status': 'success',
        'message': 'Simulation reset to initial state',
        'current_time': simulation_time,
        'hardware_connected': False
    })


@app.route('/api/simulation/demo', methods=['POST'])
def generate_demo():
    """Generate demo scenario with critical locations"""
    global simulation_time
    
    simulation_time = 0
    initialize_locations()
    
    # Make A1 and B2 critical
    for loc_id in ['A1', 'B2']:
        location = locations_db[loc_id]
        wet_bin = location['bins'].get(f'{loc_id}_WET')
        dry_bin = location['bins'].get(f'{loc_id}_DRY')
        
        if wet_bin:
            wet_bin['fill_level'] = random.uniform(75, 90)
            wet_bin['methane'] = random.uniform(350, 500)
            wet_bin['decomposition'] = random.uniform(50, 70)
            wet_bin['waste_composition'] = {'food': 12, 'paper': 2, 'plastic': 1, 'organic': 8}
        
        if dry_bin:
            dry_bin['fill_level'] = random.uniform(70, 85)
            dry_bin['weight'] = random.uniform(50, 70)
    
    # Make A3 warning level
    location = locations_db['A3']
    wet_bin = location['bins']['A3_WET']
    wet_bin['fill_level'] = random.uniform(50, 65)
    wet_bin['methane'] = random.uniform(200, 300)
    wet_bin['decomposition'] = random.uniform(35, 50)
    
    simulation_time = 6
    
    response_locations = {}
    for loc_id, location in locations_db.items():
        for bin_id, bin_data in location['bins'].items():
            bin_data['risk_score'] = round(calculate_bin_risk(bin_data), 1)
            bin_data['status'] = get_risk_status(bin_data['risk_score'])
        
        location_risk = calculate_location_risk(location)
        response_locations[loc_id] = {
            **location,
            'location_risk': round(location_risk, 1),
            'status': get_risk_status(location_risk)
        }
    
    return jsonify({
        'status': 'success',
        'message': 'Demo scenario: A1, B2 critical. A3 warning.',
        'current_time': simulation_time,
        'locations': response_locations
    })


# ============================================================
# API ENDPOINTS - STATISTICS & HEALTH
# ============================================================

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get system-wide statistics"""
    all_location_risks = [calculate_location_risk(loc) for loc in locations_db.values()]
    urgent_locations = sum(1 for risk in all_location_risks if risk > 60)
    warning_locations = sum(1 for risk in all_location_risks if 40 < risk <= 60)
    
    all_bins = []
    for loc in locations_db.values():
        all_bins.extend(loc['bins'].values())
    
    wet_bins = [b for b in all_bins if b['type'] == 'wet']
    dry_bins = [b for b in all_bins if b['type'] == 'dry']
    
    avg_fill = sum(b['fill_level'] for b in all_bins) / len(all_bins)
    avg_methane = sum(b['methane'] for b in wet_bins) / len(wet_bins) if wet_bins else 0
    total_weight = sum(b['weight'] for b in dry_bins)
    
    return jsonify({
        'status': 'success',
        'statistics': {
            'total_locations': len(locations_db),
            'total_bins': len(all_bins),
            'wet_bins': len(wet_bins),
            'dry_bins': len(dry_bins),
            'urgent_locations': urgent_locations,
            'warning_locations': warning_locations,
            'average_fill_level': round(avg_fill, 1),
            'average_methane_level': round(avg_methane, 1),
            'total_weight': round(total_weight, 1),
            'simulation_time_hours': simulation_time,
            'hardware_connected': is_hardware_active()
        }
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Smart Waste System API is running',
        'locations_count': len(locations_db),
        'bins_count': sum(len(loc['bins']) for loc in locations_db.values()),
        'routes_count': 3,
        'hardware_connected': is_hardware_active()
    })


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


# ============================================================
# SERVE FRONTEND
# ============================================================

@app.route('/')
def serve_frontend():
    """Serve the main frontend HTML file"""
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from frontend directory"""
    return send_from_directory(FRONTEND_DIR, filename)


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   🌍 Smart City Waste Management System - Backend API         ║
    ║   Location-based Model: 8 Locations × 2 Bins Each             ║
    ║   Running on http://localhost:5000                            ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║   HARDWARE: A1 = Real ESP32 (WET+DRY), others simulated       ║
    ║   ENVIRONMENTAL: WET 70% | DRY 30% (methane priority)         ║
    ║   METHANE: >500ppm = URGENT | >800ppm = EMERGENCY             ║
    ║   CLIMATE: Prioritizes CH₄ (25× more potent than CO₂)         ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    print("\n🌐 Frontend: http://localhost:5000")
    print("\n📍 Locations API:")
    print("   GET  /api/locations                              - All locations")
    print("   GET  /api/locations/<id>                         - Single location")
    print("   POST /api/locations/<id>/bins/<bin_id>/add-waste - Add waste")
    print("   POST /api/locations/<id>/bins/<bin_id>/empty     - Empty bin")
    print("   POST /api/locations/<id>/collect                 - Collect both bins")
    print("\n⚡ Hardware API (A1 Location):")
    print("   POST /api/locations/A1/hardware                  - ESP32 data (all sensors)")
    print("   GET  /api/hardware/status                        - Check connection")
    print("\n🚛 Routes API:")
    print("   GET  /api/routes                                 - All routes")
    print("   GET  /api/routes/optimize                        - Best route (all factors)")
    print("\n⏱️ Simulation API:")
    print("   POST /api/simulation/advance                     - Advance time")
    print("   POST /api/simulation/reset                       - Reset")
    print("   POST /api/simulation/demo                        - Demo scenario")
    print("\n📊 Other:")
    print("   GET  /api/statistics                             - System stats")
    print("   GET  /api/health                                 - Health check")
    print("\n🌱 ENVIRONMENTAL PRIORITY:")
    print("   ✅ Methane (CH₄) = 25× more potent greenhouse gas than CO₂")
    print("   ✅ WET waste (biodegradable) = Climate emergency priority")
    print("   ✅ DRY waste (plastic) = Sanitation concern, not rushed")
    print("\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
