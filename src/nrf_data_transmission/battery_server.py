from flask import Flask, jsonify
from flask_cors import CORS
import serial
import threading
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Serial port configuration
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

battery_data = {
    'packet': {
        'location': 'Pomona',
        'battery_data': [
            {'batt_id': i, 'total_volt': 0, 'volts': [0, 0, 0, 0]} 
            for i in range(1, 9)  # Creates entries for chambers 1-8
        ]
    }
}

def read_serial_data():
    global battery_data
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        time.sleep(2)  # Allow time for Arduino to reset
        
        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                if "Voltage" in line:
                    parts = line.split(": ")
                    if len(parts) == 2:
                        cell_info = parts[0]  # e.g., "Cell 1 Voltage"
                        voltage = float(parts[1].replace(" V", ""))
                        
                        # Extract chamber ID and cell number
                        info_parts = cell_info.split()
                        chamber_id = int(info_parts[1])
                        cell_num = int(info_parts[3]) - 1  # Convert to 0-based index
                        
                        # Find the battery entry for this chamber
                        for battery in battery_data['packet']['battery_data']:
                            if battery['batt_id'] == chamber_id:
                                # Update the specific cell voltage
                                battery['volts'][cell_num] = round(voltage, 2)
                                # Update total voltage
                                battery['total_volt'] = round(sum(battery['volts']), 2)
                                break
            except Exception as e:
                print(f"Error reading serial data: {e}")
                time.sleep(1)

@app.route('/api/rgs/voltages/Pomona', methods=['GET'])
def get_battery_data():
    return jsonify(battery_data)

if __name__ == '__main__':
    # Start the serial reading thread
    threading.Thread(target=read_serial_data, daemon=True).start()
    
    # Start the Flask web server
    app.run(host='0.0.0.0', port=5000)