"""Delete all Spotify playlists owned by the user that contain “[AUTO]” in
their description.

Requires:
    - SPOTIPY_CLIENT_ID
    - SPOTIPY_CLIENT_SECRET
    - SPOTIPY_REDIRECT_URI
to be set in a `.env` file (handled by python‑dotenv).
"""

from __future__ import annotations

import os
import time
from typing import Any

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ── Load environment variables ──────────────────────────────────────────────
load_dotenv()

CLIENT_ID: str | None = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET: str | None = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI: str | None = os.getenv("SPOTIPY_REDIRECT_URI")

SCOPE = "playlist-modify-public playlist-modify-private"
AUTO_TAG = "[AUTO]"        # text to look for in the playlist description
BATCH_DELAY = 0.2          # seconds to wait after each delete (rate‑limit safety)


def authenticate_spotify() -> spotipy.Spotify:
    """Return an authenticated Spotipy client."""
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def delete_auto_playlists(sp_client: spotipy.Spotify, description_tag: str) -> int:
    """Delete every playlist *owned by the user* that contains `description_tag`.

    Args:
        sp_client: Authenticated Spotipy client.
        description_tag: The marker text to search for in playlist descriptions.

    Returns:
        The total number of playlists deleted.
    """
    user_id: str = sp_client.me()["id"]
    deleted_total = 0

    while True:
        deleted_this_round = 0
        playlists: dict[str, Any] = sp_client.current_user_playlists(limit=50)

        while playlists:
            for playlist in playlists["items"]:
                is_owner = playlist["owner"]["id"] == user_id
                has_tag = description_tag in (playlist.get("description") or "")

                if is_owner and has_tag:
                    name = playlist["name"]
                    print(f"Deleting playlist: {name}")
                    sp_client.current_user_unfollow_playlist(playlist["id"])
                    deleted_total += 1
                    deleted_this_round += 1
                    time.sleep(BATCH_DELAY)

            playlists = sp_client.next(playlists) if playlists["next"] else None

        if deleted_this_round == 0:
            break  # no more matches, exit outer loop

    return deleted_total


def main() -> None:
    """Script entry point."""
    sp_client = authenticate_spotify()
    total_deleted = delete_auto_playlists(sp_client, AUTO_TAG)
    print(f"\n✅ Finished. Deleted {total_deleted} playlist(s) with '{AUTO_TAG}' in the description.")


if __name__ == "__main__":
    main()
