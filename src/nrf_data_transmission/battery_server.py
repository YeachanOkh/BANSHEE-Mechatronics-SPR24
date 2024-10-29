from flask import Flask, jsonify
from flask_cors import CORS
import serial
import threading
import time
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Serial port configuration - adjust COM port as needed
SERIAL_PORT = 'COM3'  # Change this to match your system
BAUD_RATE = 9600

# Global variable to store battery data
battery_data = {
    'packet': {
        'location': 'Pomona',
        'last_complete_update': None,
        'battery_data': [
            {
                'batt_id': 1,  # Using single battery ID since we have one Arduino
                'total_volt': 0,
                'volts': [0, 0, 0, 0],
                'cells_reported': set()
            }
        ]
    }
}

def read_serial_data():
    global battery_data
    while True:
        try:
            # Try to open the serial port
            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
                print(f"Successfully connected to {SERIAL_PORT}")
                time.sleep(2)  # Allow Arduino to reset
                
                while True:
                    try:
                        line = ser.readline().decode('utf-8').strip()
                        if line:  # Check if line is not empty
                            print(f"Raw data received: {line}")  # Debugging output
                            
                            # Parse the JSON data
                            json_data = json.loads(line)  # This assumes the Arduino sends valid JSON

                            # Assuming the structure is like: {"battery_data":[{"batt_id":1, "total_volt":...}]}
                            battery_info = json_data.get("battery_data", [{}])[0]
                            battery = battery_data['packet']['battery_data'][0]

                            # Update battery data from the parsed JSON
                            battery['batt_id'] = battery_info.get("batt_id", battery['batt_id'])
                            battery['total_volt'] = round(battery_info.get("total_volt", 0), 2)
                            battery['volts'] = [round(v, 2) for v in battery_info.get("volts", [0]*4)]
                            battery['cells_reported'] = set(range(1, 5))  # Set all cells as reported for this example

                            print(f"Updated battery data: {battery}")
                        
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                    except Exception as e:
                        print(f"Error reading line: {e}")
                        continue
                        
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
            continue

@app.route('/api/rgs/voltages/Pomona', methods=['GET'])
def get_battery_data():
    try:
        print("Fetching battery data...")
        print("Current battery_data state:", battery_data)  # Add this debug line
        # Prepare the battery data for JSON response
        response_data = {
            'packet': {
                'location': 'Pomona',
                'battery_data': [
                    {
                        'batt_id': battery_data['packet']['battery_data'][0]['batt_id'],
                        'total_volt': battery_data['packet']['battery_data'][0]['total_volt'],
                        'volts': battery_data['packet']['battery_data'][0]['volts']
                    }
                ]
            }
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error in /api/rgs/voltages/Pomona: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/rgs/status', methods=['GET'])
def get_status():
    battery = battery_data['packet']['battery_data'][0]
    status = {
        'complete_data_available': len(battery['cells_reported']) == 4,
        'last_complete_update': battery_data['packet']['last_complete_update'],
        'chambers_status': [
            {
                'chamber_id': battery['batt_id'],
                'cells_reported': len(battery['cells_reported']),
                'is_complete': len(battery['cells_reported']) == 4
            }
        ]
    }
    return jsonify(status)

if __name__ == '__main__':
    # Start the serial reading thread
    threading.Thread(target=read_serial_data, daemon=True).start()
    
    # Start the Flask web server
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000)
