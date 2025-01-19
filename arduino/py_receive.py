import serial
import time
import requests
import numpy as np
from datetime import datetime, timedelta

from scipy.ndimage import gaussian_filter1d

arduino_port = 'COM3'
baud_rate = 9600  # Match the Arduino's baud rate


flask_url = "http://localhost:8000"

buffer = []
N = 8
THRESHOLD = 4
SMALL = 100
PAUSE_SMALL =  6
do_nothing_count = 0
# 0: no action, 1: next, 2: previous, 3: pause, 4: play, 5: volume up, 6: volume down
actions = {0: "No action", 1: "Next", 2: "Previous", 3: "Pause", 4: "Play", 5: "Volume up", 6: "Volume down"}
last_action =  {"action": actions[0], "time": datetime.now()}

# action_time_threshold = timedelta(seconds=2)

# prev_distance_time = datetime.now()

# distance_time_threshold = timedelta(seconds=1)

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


            # print(line)
            # current_time = datetime.now()
            if len(buffer) <= N:
                buffer.append(line)
            else:
                buffer.pop(0)
                buffer.append(line)


            # if (current_time - prev_distance_time <= distance_time_threshold):
            #     continue

            buffer_np = np.array(buffer)
            
            # prev_distance_time = current_time

            # smoothed = gaussian_filter1d(buffer_np, sigma=2)
            smoothed = buffer_np

            avg = np.mean(smoothed)

            old = np.median(smoothed[:N//2])
            new = np.median(smoothed[N//2:])

            deriv = new - old

            # print(buffer)

            

            if old > SMALL or new > SMALL or len(buffer) < N:
                last_action["action"] = actions[0]
                # print("small")
                continue

            predicted_action = ""
            
            if avg < PAUSE_SMALL: # pause
                predicted_action = actions[3]
            elif deriv > THRESHOLD: # up -> previous
                predicted_action = actions[2]
            elif deriv < -THRESHOLD: # down -> next
                predicted_action = actions[1]
            else:
                predicted_action = actions[0]

                # # no action
            # if predicted_action == last_action["action"] and current_time - last_action["time"] <= action_time_threshold:
            #     last_action["time"] = current_time
            #     # print("old jews")
            #     continue

            if (predicted_action == last_action["action"] and do_nothing_count <= 8 and predicted_action != actions[0]):
                do_nothing_count += 1
                # print("no action (if)")
            else:
                do_nothing_count = 0
                last_action["action"] = predicted_action
                data = {'status': f'{last_action["action"]}'}

                match last_action["action"]:
                    case "Next": 
                        print("next")
                        previous_flag = False
                        response = requests.post(f"{flask_url}/skip_song")
                    # case "Previous":
                    #     print("previous")
                    #     response = requests.post(f"{flask_url}/previous_song")
                    case "Pause":
                        print("pause")
                        previous_flag = False
                        response = requests.post(f"{flask_url}/play_pause")
                    case _:
                        continue



            # last_action["action"] = predicted_action
            # last_action["time"] = current_time

            # data = {'status': f'{last_action["action"]}'}

            # # print(f"{avg}")

            # match last_action["action"]:
            #     case "Next": 
            #         print("next")
            #         print(current_time - last_action["time"])
            #         response = requests.post(f"{flask_url}/skip_song")
            #     case "Previous":
            #         print("previous")
            #         print(current_time - last_action["time"])
            #         response = requests.post(f"{flask_url}/previous_song")
            #     case "Pause":
            #         print("pause")
            #         print(current_time - last_action["time"])
            #         response = requests.post(f"{flask_url}/play_pause")
            #     case _:
            #         continue



except KeyboardInterrupt:
    print("Exiting...")
finally:
    ser.close()