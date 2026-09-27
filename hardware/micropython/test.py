"""
HX711 Weight Sensor Calibration Test
=====================================

This script helps calibrate the tare value and scale factor for the HX711 load cell.

Steps:
1. Run with empty scale to get TARE_VALUE
2. Place a known weight to calculate SCALE_FACTOR
3. Verify calibration with the known weight

Wiring: HX711 DT=D22, SCK=D23
"""

from machine import Pin
import time

# ============================================================
# PIN CONFIGURATION (same as send_raw_data.py)
# ============================================================

HX711_DT_PIN = 22
HX711_SCK_PIN = 23

# Initialize pins
dt_pin = Pin(HX711_DT_PIN, Pin.IN)
sck_pin = Pin(HX711_SCK_PIN, Pin.OUT)
sck_pin.value(0)

# Current calibration values (update after calibration)
TARE_VALUE = -7691
SCALE_FACTOR = 473.48

# ============================================================
# HX711 FUNCTIONS
# ============================================================

def read_hx711_raw():
    """Read raw value from HX711 (24-bit signed)."""
    try:
        # Wait for data ready
        timeout = 50
        while dt_pin.value() == 1:
            time.sleep_ms(5)
            timeout -= 1
            if timeout <= 0:
                print("  ERROR: HX711 timeout - check wiring!")
                return None
        
        # Read 24 bits
        value = 0
        for i in range(24):
            sck_pin.value(1)
            time.sleep_us(1)
            value = (value << 1) | dt_pin.value()
            sck_pin.value(0)
            time.sleep_us(1)
        
        # 25th pulse for gain 128 (channel A)
        sck_pin.value(1)
        time.sleep_us(1)
        sck_pin.value(0)
        
        # Convert to signed
        if value & 0x800000:
            value -= 0x1000000
        
        return value
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def read_averaged_raw(samples=10, delay_ms=100):
    """Read multiple samples and return average."""
    readings = []
    for i in range(samples):
        raw = read_hx711_raw()
        if raw is not None:
            readings.append(raw)
            print(f"  Sample {i+1}: {raw}")
        time.sleep_ms(delay_ms)
    
    if not readings:
        return None
    
    avg = sum(readings) / len(readings)
    return avg


def read_weight_grams(tare=TARE_VALUE, scale=SCALE_FACTOR):
    """Convert raw reading to grams using tare and scale factor."""
    raw = read_hx711_raw()
    if raw is None:
        return None, None
    weight = (raw - tare) / scale
    return raw, round(max(0, weight), 2)


# ============================================================
# CALIBRATION TESTS
# ============================================================

def test_tare():
    """
    TEST 1: Find the TARE_VALUE
    Run this with EMPTY scale (no weight on it).
    """
    print("\n" + "="*50)
    print("TEST 1: TARE VALUE CALIBRATION")
    print("="*50)
    print("\nMake sure the scale is EMPTY (no weight on it).")
    print("Taking 20 samples...")
    time.sleep(2)
    
    avg = read_averaged_raw(samples=20, delay_ms=200)
    
    if avg is not None:
        print(f"\n>>> TARE_VALUE = {int(avg)}")
        print(f"    (Average of readings: {avg:.2f})")
        print("\nUpdate TARE_VALUE in send_raw_data.py with this value.")
        return int(avg)
    else:
        print("\nERROR: Could not read from HX711. Check wiring!")
        return None


def test_scale_factor(known_weight_grams, tare=None):
    """
    TEST 2: Calculate the SCALE_FACTOR
    Place a known weight on the scale.
    
    Args:
        known_weight_grams: Weight of the calibration object in grams
        tare: Tare value (uses current TARE_VALUE if not provided)
    """
    if tare is None:
        tare = TARE_VALUE
    
    print("\n" + "="*50)
    print("TEST 2: SCALE FACTOR CALIBRATION")
    print("="*50)
    print(f"\nUsing TARE_VALUE = {tare}")
    print(f"Place a {known_weight_grams}g weight on the scale.")
    print("Taking 20 samples...")
    time.sleep(3)
    
    avg = read_averaged_raw(samples=20, delay_ms=200)
    
    if avg is not None:
        scale_factor = (avg - tare) / known_weight_grams
        print(f"\n>>> SCALE_FACTOR = {scale_factor:.2f}")
        print(f"    Raw reading: {avg:.2f}")
        print(f"    Tare value: {tare}")
        print(f"    Known weight: {known_weight_grams}g")
        print(f"    Formula: ({avg:.2f} - {tare}) / {known_weight_grams} = {scale_factor:.2f}")
        print("\nUpdate SCALE_FACTOR in send_raw_data.py with this value.")
        return scale_factor
    else:
        print("\nERROR: Could not read from HX711. Check wiring!")
        return None


def test_verification(tare=None, scale=None):
    """
    TEST 3: Verify the calibration
    Tests current calibration by showing weight readings.
    """
    if tare is None:
        tare = TARE_VALUE
    if scale is None:
        scale = SCALE_FACTOR
    
    print("\n" + "="*50)
    print("TEST 3: CALIBRATION VERIFICATION")
    print("="*50)
    print(f"Using TARE_VALUE = {tare}")
    print(f"Using SCALE_FACTOR = {scale:.2f}")
    print("\nReading weight continuously. Press Ctrl+C to stop.")
    print("-"*50)
    
    try:
        while True:
            raw, weight = read_weight_grams(tare, scale)
            if raw is not None:
                print(f"Raw: {raw:>10}  |  Weight: {weight:>8.2f} g")
            else:
                print("ERROR: Could not read sensor")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped verification test.")


def test_raw_readings():
    """
    TEST 4: Show raw HX711 readings
    Useful for debugging connection issues.
    """
    print("\n" + "="*50)
    print("TEST 4: RAW HX711 READINGS")
    print("="*50)
    print("Reading raw values continuously. Press Ctrl+C to stop.")
    print("-"*50)
    
    try:
        while True:
            raw = read_hx711_raw()
            if raw is not None:
                print(f"Raw value: {raw}")
            else:
                print("ERROR: Could not read - check wiring!")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopped raw readings test.")


def full_calibration(known_weight_grams):
    """
    Run complete calibration sequence.
    
    Args:
        known_weight_grams: Weight of calibration object in grams
    """
    print("\n" + "="*50)
    print("FULL CALIBRATION SEQUENCE")
    print("="*50)
    
    # Step 1: Tare
    input_prompt = "Press Enter when scale is EMPTY..."
    print(f"\nStep 1: {input_prompt}")
    time.sleep(3)
    tare = test_tare()
    
    if tare is None:
        print("Calibration failed at tare step!")
        return
    
    # Step 2: Scale Factor
    print(f"\nStep 2: Place the {known_weight_grams}g weight on the scale...")
    time.sleep(5)
    scale = test_scale_factor(known_weight_grams, tare)
    
    if scale is None:
        print("Calibration failed at scale factor step!")
        return
    
    # Summary
    print("\n" + "="*50)
    print("CALIBRATION COMPLETE")
    print("="*50)
    print(f"\nUpdate these values in send_raw_data.py:")
    print(f"  TARE_VALUE = {tare}")
    print(f"  SCALE_FACTOR = {scale:.2f}")
    print("\nStarting verification in 3 seconds...")
    time.sleep(3)
    
    test_verification(tare, scale)


# ============================================================
# MAIN - AUTO RUN ON EXECUTION
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*50)
    print("HX711 WEIGHT SENSOR CALIBRATION")
    print("="*50)
    
    # STEP 1: TARE CALIBRATION
    print("\n[STEP 1] TARE VALUE CALIBRATION")
    print("Make sure the scale is EMPTY!")
    print("Reading in 3 seconds...")
    time.sleep(3)
    
    print("\nTaking 20 samples for tare value:")
    tare_avg = read_averaged_raw(samples=20, delay_ms=200)
    
    if tare_avg is None:
        print("ERROR: Cannot read HX711. Check wiring!")
    else:
        new_tare = int(tare_avg)
        print("\n" + "-"*50)
        print(f">>> NEW TARE_VALUE = {new_tare}")
        print("-"*50)
        
        # STEP 2: SCALE FACTOR
        print("\n[STEP 2] SCALE FACTOR CALIBRATION")
        print("Place a KNOWN WEIGHT on the scale.")
        print("Waiting 10 seconds for you to place the weight...")
        time.sleep(10)
        
        print("\nTaking 20 samples with weight:")
        weight_avg = read_averaged_raw(samples=20, delay_ms=200)
        
        if weight_avg is not None:
            print("\n" + "-"*50)
            print(f"Raw reading with weight: {weight_avg:.2f}")
            print(f"Tare value: {new_tare}")
            print("-"*50)
            
            print("\n*** CALCULATE YOUR SCALE_FACTOR ***")
            print(f"Formula: (raw - tare) / known_weight_grams")
            print(f"         ({weight_avg:.2f} - {new_tare}) / YOUR_WEIGHT_GRAMS")
            print(f"\nExample calculations:")
            for w in [50, 100, 200, 500, 1000]:
                sf = (weight_avg - new_tare) / w
                print(f"  If weight = {w:4}g  -->  SCALE_FACTOR = {sf:.2f}")
            
            print("\n" + "="*50)
            print("FINAL VALUES TO UPDATE IN send_raw_data.py:")
            print("="*50)
            print(f"TARE_VALUE = {new_tare}")
            print(f"SCALE_FACTOR = <choose from above based on your weight>")
            
            # STEP 3: Continuous reading
            print("\n" + "="*50)
            print("[STEP 3] CONTINUOUS READINGS")
            print("="*50)
            print("Showing raw values. Press Ctrl+C to stop.\n")
            
            try:
                while True:
                    raw = read_hx711_raw()
                    if raw is not None:
                        # Show with current calibration
                        weight_current = (raw - TARE_VALUE) / SCALE_FACTOR
                        weight_new = (raw - new_tare) / SCALE_FACTOR
                        print(f"Raw: {raw:>10} | Old cal: {weight_current:>8.2f}g | New tare: {weight_new:>8.2f}g")
                    time.sleep(0.5)
            except KeyboardInterrupt:
                print("\nStopped.")
