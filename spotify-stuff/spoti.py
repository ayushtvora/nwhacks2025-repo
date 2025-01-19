from flask import Flask, jsonify, request, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__,  static_url_path='')

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


@app.route('/current_song', methods=['GET'])
def current_song():
    try:
        playback = sp.current_playback()
        if playback and playback['item']:
            artist_name = ", ".join([artist['name'] for artist in playback['item']['artists']])
            song_name = playback['item']['name']
            return jsonify({'artist': artist_name, 'song': song_name})
        return jsonify({'error': 'No active playback found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/play_pause', methods=['POST'])
def play_pause():
    try:
        playback = sp.current_playback()
        if playback and playback['is_playing']:
            sp.pause_playback()
            return jsonify({'status': 'Paused playback.'})
        sp.start_playback()
        return jsonify({'status': 'Resumed playback.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/skip_song', methods=['POST'])
def skip_song():
    try:
        sp.next_track()
        return jsonify({'status': 'Skipped to the next song.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/previous_song', methods=['POST'])
def previous_song():
    try:
        sp.previous_track()
        return jsonify({'status': 'Skipped to the previous song.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/volume_up', methods=['POST'])
def volume_up():
    try:
        playback = sp.current_playback()
        if playback:
            current_volume = playback['device']['volume_percent']
            new_volume = min(current_volume + 10, 100)
            sp.volume(new_volume)
            return jsonify({'status': f'Volume increased to {new_volume}%.'})
        return jsonify({'error': 'No active playback found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/volume_down', methods=['POST'])
def volume_down():
    try:
        playback = sp.current_playback()
        if playback:
            current_volume = playback['device']['volume_percent']
            new_volume = max(current_volume - 10, 0)
            sp.volume(new_volume)
            return jsonify({'status': f'Volume decreased to {new_volume}%.'})
        return jsonify({'error': 'No active playback found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8000)
