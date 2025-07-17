import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ── Load environment variables ──────────────────────────────────────────────
load_dotenv()

CLIENT_ID: str | None = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET: str | None = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI: str | None = os.getenv("SPOTIPY_REDIRECT_URI")

# ── Constants ────────────────────────────────────────────────────────────────
SCOPE = (
    "user-library-read playlist-modify-public playlist-modify-private "
    "ugc-image-upload"
)

def authenticate_spotify() -> spotipy.Spotify:
    """Return an authenticated Spotipy client."""
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
    )
    return spotipy.Spotify(auth_manager=auth_manager)