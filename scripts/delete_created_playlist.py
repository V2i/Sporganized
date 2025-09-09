"""Delete all Spotify playlists owned by the user that contain “[AUTO]” in
their description.

Environment variables to be set in a `.env` file (handled by python‑dotenv):
    - SPOTIPY_CLIENT_ID
    - SPOTIPY_CLIENT_SECRET
    - SPOTIPY_REDIRECT_URI
"""

from __future__ import annotations
from typing import Any
import time
import spotipy

# ── Constants & Functions ────────────────────────────────────────────────────────────────
from src.authenticate_spotify import authenticate_spotify
import src.constants

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
                    time.sleep(src.constants.RATE_DELAY)

            playlists = sp_client.next(playlists) if playlists["next"] else None

        if deleted_this_round == 0:
            break  # no more matches, exit outer loop

    return deleted_total


def main() -> None:
    """Script entry point."""
    sp_client = authenticate_spotify()
    total_deleted = delete_auto_playlists(sp_client, src.constants.DESCRIPTION_TAG)
    print(f"\n✅ Finished. Deleted {total_deleted} playlist(s) with '{src.constants.DESCRIPTION_TAG}' in the description.")


if __name__ == "__main__":
    main()
