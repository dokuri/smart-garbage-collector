"""Standalone Flask backend to receive continuous pings from ESP32."""

import json
from datetime import datetime
from flask import Flask, jsonify, request

# Create Flask app instance
app = Flask(__name__)


@app.route('/api/health', methods=['GET', 'POST'])
def health_endpoint():
    """Health endpoint that receives pings from ESP32 and logs them."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.environ.get('REMOTE_ADDR'))
    
    # Print ping information to terminal
    print(f"[{timestamp}] ESP32 PING received from {client_ip}")
    print(f"  Method: {request.method}")
    print(f"  User-Agent: {request.headers.get('User-Agent', 'Unknown')}")
    
    # Log any additional data if sent via POST
    if request.method == 'POST':
        try:
            data = request.get_json()
            if data:
                print(f"  Data: {json.dumps(data, indent=2)}")
        except:
            pass
    
    print("-" * 50)
    
    # Return success response
    response_data = {
        "status": "success",
        "message": "Ping received successfully",
        "timestamp": timestamp,
        "server": "ESP32 Ping Receiver"
    }
    
    return jsonify(response_data), 200


@app.route('/api/data', methods=['POST'])
def receive_data():
    """Endpoint to receive sensor data from ESP32."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.environ.get('REMOTE_ADDR'))
    
    print(f"[{timestamp}] ESP32 DATA received from {client_ip}")
    
    try:
        data = request.get_json()
        if data:
            print(f"  Sensor Data: {json.dumps(data, indent=2)}")
        else:
            print("  No JSON data received")
    except Exception as e:
        print(f"  Error parsing JSON: {e}")
    
    print("-" * 50)
    
    return jsonify({
        "status": "success",
        "message": "Data received successfully",
        "timestamp": timestamp
    }), 200


if __name__ == '__main__':
    print("=" * 60)
    print("ESP32 Ping Receiver Backend Server")
    print("=" * 60)
    print("Waiting for ESP32 pings...")
    print("Available endpoints:")
    print("  GET/POST /api/health - Health check endpoint")
    print("  POST /api/data - Sensor data endpoint")
    print("=" * 60)
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=5000,
        debug=True
    )
