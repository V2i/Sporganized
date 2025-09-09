"""
spotify_fetch.py

Helper for fetching saved (liked) tracks from Spotify using Spotipy.
Can return either full track objects or simplified tracks with cleaned ISRCs.
"""

import re
from typing import Dict, List, Any, Union
from spotipy import Spotify

def fetch_liked_tracks(
    sp_client: Spotify, simplified: bool = False
) -> List[Union[Dict[str, Any], Dict[str, str]]]:
    """
    Fetch all saved (liked) tracks for the current user.

    Parameters
    ----------
    sp_client : Spotify
        Authenticated Spotipy client.
    simplified : bool, default False
        If True, return a simplified dictionary for each track containing:
        'id', 'name', and cleaned 'isrc'. If False, return full track objects.

    Returns
    -------
    List[dict]
        List of tracks, either full Spotify track objects or simplified dictionaries.
    """
    tracks: List[Union[Dict[str, Any], Dict[str, str]]] = []
    results = sp_client.current_user_saved_tracks(limit=50)

    while results:
        for item in results["items"]:
            t = item["track"]
            if simplified:
                isrc = t.get("external_ids", {}).get("isrc")
                if isrc:
                    cleaned_isrc = re.sub(r"[^A-Za-z0-9]", "", str(isrc)).upper()
                    tracks.append({"id": t["id"], "name": t["name"], "isrc": cleaned_isrc})
            else:
                tracks.append(t)
        results = sp_client.next(results) if results["next"] else None

    return tracks
