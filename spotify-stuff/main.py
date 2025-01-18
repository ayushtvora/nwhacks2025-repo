import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

# Replace with your Spotify app credentials
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = 'http://localhost:8080/callback'

# Set up Spotipy with user authorization
scope = "user-modify-playback-state user-read-playback-state"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=scope
))

def play_pause():
    playback = sp.current_playback()
    if playback is None:
        print("No active playback found.")
        return

    if playback['is_playing']:
        sp.pause_playback()
        print("Paused playback.")
    else:
        sp.start_playback()
        print("Resumed playback.")


def skip_song():
    sp.next_track()
    print("Skipped song.")

def previous_song():
    sp.previous_track()
    print("Previous song.")

def volume_up():
    playback = sp.current_playback()
    if playback is None:
        print("No active playback found.")
        return

    volume = playback['device']['volume_percent']
    new_volume = min(volume + 10, 100)
    sp.volume(new_volume)
    print(f"Volume increased to {new_volume}%.")

def volume_down():
    playback = sp.current_playback()
    if playback is None:
        print("No active playback found.")
        return

    volume = playback['device']['volume_percent']
    new_volume = max(volume - 10, 0)
    sp.volume(new_volume)
    print(f"Volume decreased to {new_volume}%.")


if __name__ == "__main__":
    # play_pause()
    skip_song()
    # previous_song()
    # volume_up()
    # volume_down()
