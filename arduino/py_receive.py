import serial
import time
import requests

# Replace 'COMX' with your Arduino's port (e.g., COM3 on Windows, /dev/ttyUSB0 or /dev/ttyACM0 on Linux/Mac)
arduino_port = '/dev/tty.usbmodem1101'  
baud_rate = 9600  # Match the Arduino's baud rate


flask_url = "http://localhost:8000"

# Initialize the serial connection
try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    print("Connected to Arduino!")
    time.sleep(2)  # Wait for Arduino to initialize
except serial.SerialException as e:
    print(f"Error: {e}")
    exit()

try:
    while True:
        if ser.in_waiting > 0:
            # Read a line from the serial port
            line = ser.readline().decode('utf-8').strip()
            # Print the data or use it in your application
            print(f"Distance: {line} cm")

            # Prepare data payload
            data = {"distance": line}

            # Send data to Flask backend
            response = requests.post(f"{flask_url}/receive_data", json=data)
            print(f"Sent to Flask, response: {response.json()}")
except KeyboardInterrupt:
    print("Exiting...")
finally:
    ser.close()