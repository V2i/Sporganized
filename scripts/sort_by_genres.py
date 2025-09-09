"""Create (or update) one Spotify playlist per broad genre cluster from
the user's liked songs.

Requirements:
    • python-dotenv
    • spotipy

Environment variables to be set in a `.env` file (handled by python‑dotenv):
    - SPOTIPY_CLIENT_ID
    - SPOTIPY_CLIENT_SECRET
    - SPOTIPY_REDIRECT_URI
"""

from __future__ import annotations
from collections import defaultdict
from typing import Dict, List
import time
import spotipy
from spotipy.exceptions import SpotifyException

# ── Constants & Functions ─────────────────────────────────────────────────
from src.fetch_from_spotify import fetch_liked_tracks
from src.authenticate_spotify import authenticate_spotify
import src.constants
from src.genre_groups import GENRE_GROUPS

def get_genres_for_artists(
    sp_client: spotipy.Spotify,
    artist_ids: list[str],
) -> Dict[str, List[str]]:
    """Fetch genres for all artists, handling rate limits and batching."""
    artist_genres: Dict[str, List[str]] = {}
    for start in range(0, len(artist_ids), 50):
        batch = artist_ids[start : start + 50]
        while True:
            try:
                artists_info = sp_client.artists(batch)["artists"]
                break
            except SpotifyException as exc:
                if exc.http_status == 429:
                    wait = int(exc.headers.get("Retry-After", 1))
                    print(f"Rate‑limited. Waiting {wait}s…")
                    time.sleep(wait)
                else:
                    raise
        for artist in artists_info:
            artist_genres[artist["id"]] = artist.get("genres", [])
        time.sleep(src.constants.RATE_DELAY)
    return artist_genres


def map_to_group(genre: str) -> str:
    """Return the broad group label for a genre, defaulting to 'Misc & Other'."""
    for group_name, subgenres in GENRE_GROUPS.items():
        if genre in subgenres:
            return group_name
    return "Misc & Other"


# ── Main function ──────────────────────────────────────────────────────────
def main() -> None:
    """Entry point: build or update one playlist per genre cluster."""
    sp_client = authenticate_spotify()
    user_id: str = sp_client.me()["id"]

    liked_tracks = fetch_liked_tracks(sp_client)
    print(f"Retrieved {len(liked_tracks)} liked track(s).")

    # Collect unique artist IDs and fetch their genres
    artist_ids = {
        artist["id"] for track in liked_tracks for artist in track["artists"]
    }
    artist_genres_map = get_genres_for_artists(sp_client, list(artist_ids))

    # Bucket tracks into genre‑groups
    grouped_tracks: Dict[str, List[str]] = defaultdict(list)
    for track in liked_tracks:
        artist_id = track["artists"][0]["id"]
        genres = artist_genres_map.get(artist_id, [])
        if genres:
            primary = genres[0]
            group_label = map_to_group(primary)
            grouped_tracks[group_label].append(track["id"])

    # Summary
    for label, tracks in grouped_tracks.items():
        print(f"{label}: {len(tracks)} track(s)")

    # Create or update playlists
    for group_label, track_ids in grouped_tracks.items():
        playlist_name = f"{src.constants.PLAYLIST_PREFIX} - {group_label}"
        description = (
            f"Sporganized generated playlist · {group_label} {src.constants.DESCRIPTION_TAG}"
        )

        # Check if playlist already exists
        playlist_id: str | None = None
        playlists_page = sp_client.current_user_playlists(limit=50)
        while playlists_page:
            for playlist in playlists_page["items"]:
                owned = playlist["owner"]["id"] == user_id
                if owned and playlist["name"].lower() == playlist_name.lower():
                    playlist_id = playlist["id"]
                    break
            if playlist_id or not playlists_page["next"]:
                break
            playlists_page = sp_client.next(playlists_page)

        if playlist_id:
            print(f"Updating playlist: {playlist_name}")
            sp_client.playlist_replace_items(playlist_id, [])
        else:
            print(f"Creating playlist: {playlist_name}")
            playlist = sp_client.user_playlist_create(
                user=user_id,
                name=playlist_name,
                public=True,
                description=description,
            )
            playlist_id = playlist["id"]

        # Add tracks in 100‑track batches
        for start in range(0, len(track_ids), 100):
            sp_client.playlist_add_items(playlist_id, track_ids[start : start + 100])
            time.sleep(src.constants.RATE_DELAY)


if __name__ == "__main__":
    main()
