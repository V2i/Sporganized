"""Fetch genres for Spotify artists with batching and rate-limit handling."""

import time
from typing import Dict, List
import spotipy
from spotipy.exceptions import SpotifyException
from src.constants import RATE_DELAY

def get_artists_genre(
    sp_client: spotipy.Spotify,
    artist_ids: List[str],
) -> Dict[str, List[str]]:
    """Fetch genres for all artists, handling rate limits and batching.

    Args:
        sp_client: Authenticated Spotipy client.
        artist_ids: List of Spotify artist IDs.

    Returns:
        Mapping from artist ID to a list of genres.
    """
    artist_genres: Dict[str, List[str]] = {}

    for start in range(0, len(artist_ids), 50):
        batch = artist_ids[start:start + 50]

        while True:
            try:
                artists_info = sp_client.artists(batch)["artists"]
                break
            except SpotifyException as exc:
                if exc.http_status == 429:
                    wait_time = int(exc.headers.get("Retry-After", 1))
                    print(f"Rate-limited. Waiting {wait_time}s…")
                    time.sleep(wait_time)
                else:
                    raise

        for artist in artists_info:
            artist_genres[artist["id"]] = artist.get("genres", [])

        time.sleep(RATE_DELAY)

    return artist_genres
