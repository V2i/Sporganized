from typing import Dict, List, Any
from spotipy import Spotify

# ── Data fetch helpers ───────────────────────────────────────────────────────
def fetch_spotify_likes(sp: Spotify) -> List[dict]:
    tracks, results = [], sp.current_user_saved_tracks(limit=50)
    while results:
        for item in results['items']:
            t = item['track']
            isrc = t['external_ids'].get('isrc')
            if isrc:
                # Ensure it's a string, remove special characters, and make uppercase
                cleaned_isrc = re.sub(r'[^A-Za-z0-9]', '', str(isrc)).upper()
                tracks.append({
                    'id': t['id'],
                    'name': t['name'],
                    'isrc': cleaned_isrc
                })
        results = sp.next(results) if results['next'] else None
    return tracks

def fetch_liked_tracks(sp_client: Spotify) -> List[Dict[str, Any]]:
    """Return the full list of saved (liked) tracks for the current user."""
    tracks: List[Dict[str, Any]] = []
    results = sp_client.current_user_saved_tracks(limit=50)
    while results:
        tracks.extend(item["track"] for item in results["items"])
        results = sp_client.next(results) if results["next"] else None
    return tracks
