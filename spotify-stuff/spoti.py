from flask import Flask, jsonify, request, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from scipy.ndimage import gaussian_filter1d
import numpy as np

from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__,  static_url_path='')
buffer = np.array([])
N = 10
N_local = 3
THRESHOLD = 10
distance = 0
# 0: no action, 1: next, 2: previous, 3: pause, 4: play, 5: volume up, 6: volume down
actions = {0: "No action", 1: "Next", 2: "Previous", 3: "Pause", 4: "Play", 5: "Volume up", 6: "Volume down"}
last_action =  {"action": actions[0], "time": datetime.now()}

action_time_threshold = timedelta(seconds=1)

prev_distance_time = datetime.now()

distance_time_threshold = timedelta(seconds=1)

# Spotify credentials from .env
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = 'http://localhost:8080/callback'

# Spotify API scope
scope = "user-modify-playback-state user-read-playback-state"

# Initialize Spotipy client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=scope
))

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/last_action', methods=['GET'])
def get_last_action():
    """Endpoint to return the last known action."""
    playback = sp.current_playback()
    if playback:
        current_volume = playback['device']['volume_percent']
    return jsonify({"last_action": last_action["action"], "volume": current_volume})


@app.route('/current_song', methods=['GET'])
def current_song():
    try:
        playback = sp.current_playback()
        if playback and playback['item']:
            artist_name = ", ".join([artist['name'] for artist in playback['item']['artists']])
            song_name = playback['item']['name']
            album = playback['item']['album']['name']
            album_img = playback['item']['album']['images'][0]['url']
            return jsonify({'artist': artist_name, 'song': song_name, 'album': album, 'album_img': album_img})
        return jsonify({'error': 'No active playback found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/play_pause', methods=['POST'])
def play_pause():
    global last_action
    try:
        playback = sp.current_playback()
        if playback and playback['is_playing']:
            sp.pause_playback()
            last_action["action"] = actions[3]
            return jsonify({'status': f'{last_action["action"]}'})
        sp.start_playback()
        last_action["action"] = actions[4]
        return jsonify({'status': f'{last_action["action"]}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/skip_song', methods=['POST'])
def skip_song():
    global last_action
    try:
        sp.next_track()
        last_action["action"] = actions[1]
        return jsonify({'status': f'{last_action["action"]}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/previous_song', methods=['POST'])
def previous_song():
    global last_action
    try:
        sp.previous_track()
        last_action["action"] = actions[2]
        return jsonify({'status': f'{last_action["action"]}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/volume_up', methods=['POST'])
def volume_up():
    global last_action
    try:
        playback = sp.current_playback()
        if playback:
            current_volume = playback['device']['volume_percent']
            new_volume = min(current_volume + 10, 100)

            sp.volume(new_volume)
            last_action["action"] = actions[5]
            return jsonify({'status': f'{last_action["action"]}'})
        return jsonify({'error': 'No active playback found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/volume_down', methods=['POST'])
def volume_down():
    global last_action
    try:
        playback = sp.current_playback()
        if playback:
            current_volume = playback['device']['volume_percent']
            new_volume = max(current_volume - 10, 0)
            sp.volume(new_volume)
            last_action["action"] = actions[6]
            return jsonify({'status': f'{last_action["action"]}'})
        return jsonify({'error': 'No active playback found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/receive_data', methods=['POST'])
def receive_data():

    print(f"Received data, {request.json['distance']}")
    return jsonify({'status': "no action"})
    # global last_action
    # global buffer
    # global prev_distance_time
    # global distance_time_threshold

    # current_time = datetime.now()

    # data = request.json  # Get the JSON data sent from the Python script
    # if len(buffer) < N:
    #     np.append(buffer, data)
    # else:
    #     # buffer.pop(0)
    #     buffer = buffer[1:]
    #     np.append(buffer, data)

    # if (current_time - prev_distance_time <= distance_time_threshold):
    #     return jsonify({'status': "no action"})
    
    # prev_distance_time = current_time

    # smoothed = gaussian_filter1d(buffer, sigma=2)

    # local = smoothed[-N_local:]
    # local_avg = np.mean(local)
    # abs_avg = np.mean(smoothed)

    # diff = local_avg - abs_avg
    # deriv = np.mean(np.diff(local))

    # print("{last_action} diff: {diff}")

    # predicted_action = ""

    # if diff > THRESHOLD and deriv > 0:
    #     predicted_action = actions[1]
    # elif diff < -THRESHOLD and deriv < 0:
    #     predicted_action = actions[2]
    # elif -THRESHOLD < diff and diff < THRESHOLD:
    #     predicted_action = actions[3]
    # else:
    #     predicted_action = actions[0]
    
    # # no action
    # if predicted_action == last_action["action"] and current_time - last_action["time"] <= action_time_threshold:
    #     last_action["time"] = current_time
    #     return jsonify({'status': f'{last_action["action"]}'})

    # last_action["action"] = predicted_action
    # last_action["time"] = current_time

    # match last_action["action"]:
    #     case "No action":
    #         return jsonify({'status': f'{last_action["action"]}'})
    #     case "Next":
    #         sp.next_track()
    #         return jsonify({'status': f'{last_action["action"]}'})
        
    #     case "Previous":
    #         sp.previous_track()
    #         return jsonify({'status': f'{last_action["action"]}'})
    #     case "Pause":
    #         sp.pause_playback()
    #         return jsonify({'status': f'{last_action["action"]}'})
    #     case _:
    #          return jsonify({'status': f'{last_action["action"]}'})


if __name__ == "__main__":
    app.run(debug=True, port=8000)
