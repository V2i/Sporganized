"""
Constants for Sporganized.

Spotify Credentials:
- CLIENT_ID
- CLIENT_SECRET
- REDIRECT_URI
- SCOPE

LastFM Credentials:
- LASTFM_API_KEY

API URLs:
- DISCOG_API_URL: Discogs database search
- LASTFM_API_URL: Last.fm API

Settings:
- RATE_DELAY: delay between API requests (seconds)
- N_CLUSTERS: number of K-means clusters
- DESCRIPTION_TAG: marker for auto-generated playlists
- PLAYLIST_PREFIX: prefix to sort playlists

Mood labels for categorizing tracks: ("Chill", "Feel‑Good", "Dance", "Workout", "Mellow")
"""
import os
from dotenv import load_dotenv
load_dotenv()

# Spotify credentials
CLIENT_ID: str | None = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET: str | None = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI: str | None = os.getenv("SPOTIPY_REDIRECT_URI")
SCOPE = (
    "user-library-read playlist-modify-public playlist-modify-private "
    "ugc-image-upload"
)

# LastFM API key
LASTFM_API_KEY: str | None = os.getenv("LASTFM_API_KEY")

# URLs
DISCOG_API_URL="https://api.discogs.com/database/search"
LASTFM_API_URL="http://ws.audioscrobbler.com/2.0"

# Settings
RATE_DELAY = 0.3                        # polite delay between API writes (seconds)
N_CLUSTERS = 5                          # number of clusters for the K-means
DESCRIPTION_TAG = "[AUTO]"              # marker to identify auto‑generated lists
PLAYLIST_PREFIX = "Playlist"            # helps the playlists sort together

# Moods labels used to sort liked tracks based on metadata
MOOD_LABELS = ("Chill", "Feel‑Good", "Dance", "Workout", "Mellow")
