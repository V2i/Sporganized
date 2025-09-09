"""
authenticate_spotify.py

Handles authentication with the Spotify API using Spotipy and environment variables.

- Loads client credentials from a `.env` file.
- Defines Spotify OAuth scopes.
- Provides a function to return an authenticated Spotipy client.
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from src.constants import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE 

def authenticate_spotify() -> spotipy.Spotify:
    """
    Authenticate with Spotify and return a Spotipy client.

    Reads client ID, client secret, and redirect URI from environment variables,
    and uses the SpotifyOAuth flow with the predefined scope.

    Returns
    -------
    spotipy.Spotify
        Authenticated Spotipy client ready for API requests.
    """
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
    )
    return spotipy.Spotify(auth_manager=auth_manager)
