import serial
import time
import requests
import numpy as np
from datetime import datetime, timedelta

from scipy.ndimage import gaussian_filter1d

# Replace 'COMX' with your Arduino's port (e.g., COM3 on Windows, /dev/ttyUSB0 or /dev/ttyACM0 on Linux/Mac)
# arduino_port = '/dev/tty.usbmodem1101'  
arduino_port = 'COM3'
baud_rate = 9600  # Match the Arduino's baud rate


flask_url = "http://localhost:8000"

buffer = []
hand_flag = False
N = 10
THRESHOLD = 5
SMALL = 40
PAUSE_SMALL =  4
# 0: no action, 1: next, 2: previous, 3: pause, 4: play, 5: volume up, 6: volume down
actions = {0: "No action", 1: "Next", 2: "Previous", 3: "Pause", 4: "Play", 5: "Volume up", 6: "Volume down"}
last_action =  {"action": actions[0], "time": datetime.now()}

action_time_threshold = timedelta(seconds=2)

prev_distance_time = datetime.now()

distance_time_threshold = timedelta(seconds=1)

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
            try:
                line = float(ser.readline().decode('utf-8').strip())
                if line > SMALL:
                    continue
            except ValueError:
                continue
            # Print the data or use it in your application
            # print(f"Distance: {line} cm")

            # Prepare data payload
            # data = {"distance": line}

            # Send data to Flask backend
            # response = requests.post(f"{flask_url}/receive_data", json=data)
            # print(f"Sent to Flask, response: {response.json()}")
            
            current_time = datetime.now()
            if len(buffer) < N:
                buffer.append(line)
            else:
                buffer.pop(0)
                # buffer = buffer[1:]
                buffer.append(line)

                # np.append(buffer, data)

            if (current_time - prev_distance_time <= distance_time_threshold):
                continue

            buffer_np = np.array(buffer)
            
            prev_distance_time = current_time

            smoothed = gaussian_filter1d(buffer_np, sigma=2)

            # local = smoothed[-N_local:]
            # local_avg = np.mean(local)
            # abs_avg = np.mean(smoothed)

            avg = np.mean(smoothed)


            # diff = local_avg - abs_avg
            deriv = smoothed[N//2:] - smoothed[:-N//2]
            deriv = np.mean(deriv)
            # if avg < SMALL:
            #     hand_flag = True
            # else:
            #     hand_flag = False

            print(f'{buffer_np}')
            print(f'{smoothed}')
            print(f"{last_action['action']}, deriv: {round(deriv,2)}, abs_avg: {round(avg, 2)}")

            # print(smoothed)

            predicted_action = ""

            if avg < PAUSE_SMALL: # pause
                predicted_action = actions[3]
            elif deriv > THRESHOLD: # up -> next
                predicted_action = actions[1]
            elif deriv < -THRESHOLD: # down -> previous
                predicted_action = actions[2]
            else:
                predicted_action = actions[0]

                # # no action
            if predicted_action == last_action["action"] and current_time - last_action["time"] <= action_time_threshold:
                last_action["time"] = current_time
                continue

            last_action["action"] = predicted_action
            last_action["time"] = current_time

            data = {'status': f'{last_action["action"]}'}
            # print("data: ", data)
            # response = requests.post(f"{flask_url}/receive_data", json=data)

            match last_action["action"]:
                case "Next": 
                    print("next")
                    response = requests.post(f"{flask_url}/skip_song")
                case "Previous":
                    print("previous")
                    response = requests.post(f"{flask_url}/previous_song")
                # case "Pause":
                #     print("pause")
                #     response = requests.post(f"{flask_url}/play_pause")
                case _:
                     continue



except KeyboardInterrupt:
    print("Exiting...")
finally:
    ser.close()