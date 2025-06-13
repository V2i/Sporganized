import os
import time
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# --- Load environment variables from .env ---
load_dotenv()

client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

# --- Spotify authentication ---
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="playlist-modify-public playlist-modify-private"
))

user_id = sp.me()['id']
deleted_total = 0

while True:
    deleted_this_round = 0
    playlists = sp.current_user_playlists(limit=50)

    while playlists:
        for playlist in playlists['items']:
            name = playlist['name']
            description = playlist.get('description', '')
            owner_id = playlist['owner']['id']

            if owner_id == user_id and "[AUTO]" in description:
                print(f"Deleting playlist: {name}")
                sp.current_user_unfollow_playlist(playlist['id'])
                deleted_total += 1
                deleted_this_round += 1
                time.sleep(0.2)
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            break

    if deleted_this_round == 0:
        break  # No more to delete, stop the loop

print(f"\n✅ Finished. Deleted {deleted_total} playlists with '[AUTO]' in the description.")
