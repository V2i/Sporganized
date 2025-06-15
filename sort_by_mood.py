"""Sort Spotify liked tracks into mood/energy playlists (patched for batch size)."""

from __future__ import annotations

import os
import time
from collections import defaultdict
from typing import Dict, List

from dotenv import load_dotenv
import spotipy
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

# ── Constants ────────────────────────────────────────────────────────────────
SCOPE = (
    "user-library-read playlist-modify-public playlist-modify-private "
    "ugc-image-upload"
)
PLAYLIST_PREFIX = "Mood"
DESCRIPTION_TAG = "[AUTO]"
RATE_DELAY = 0.2
BATCH_SIZE_AUDIO = 90  # <= 100 per Spotify docs; keep a safety margin

# Thresholds for mood buckets
ENERGY_HIGH = 0.7
ENERGY_LOW = 0.4
DANCE_HIGH = 0.7
DANCE_LOW = 0.6
VALENCE_HIGH = 0.7
TEMPO_WORKOUT = 120.0
ACOUSTIC_HIGH = 0.6
MOOD_BUCKETS = ("Chill", "Feel‑Good", "Dance", "Workout", "Mellow", "Misc & Other")


# ── Auth helpers ─────────────────────────────────────────────────────────────
def authenticate_spotify() -> spotipy.Spotify:
    """Return an authenticated Spotipy client."""
    load_dotenv()
    auth_manager = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope=SCOPE,
    )
    return spotipy.Spotify(auth_manager=auth_manager)


# ── Data fetch helpers ───────────────────────────────────────────────────────
def fetch_liked_track_ids(sp_client: spotipy.Spotify) -> List[str]:
    """Return all liked‑track IDs for the current user."""
    track_ids: List[str] = []
    results = sp_client.current_user_saved_tracks(limit=50)
    while results:
        track_ids.extend(item["track"]["id"] for item in results["items"])
        results = sp_client.next(results) if results["next"] else None
    return track_ids


def fetch_audio_features(
    sp_client: spotipy.Spotify, track_ids: List[str]
) -> Dict[str, dict]:
    """Fetch audio features, batching safely under Spotify's limit using the new API call."""
    features_map: Dict[str, dict] = {}

    for start in range(0, len(track_ids), BATCH_SIZE_AUDIO):
        batch_ids = track_ids[start : start + BATCH_SIZE_AUDIO]

        while True:
            try:
                # TODO: Fix audio_feature call error 403
                # Directly call the new API endpoint to avoid deprecation warning
                features_batch = sp_client.audio_features(batch_ids)
                #ids_param = ",".join(batch_ids)
                #response = sp_client._get(f"audio-features?ids={ids_param}")
                #features_batch = response.get("audio_features", [])
                break
            except SpotifyException as exc:
                if exc.http_status == 429:
                    wait = int(exc.headers.get("Retry-After", 1))
                    print(f"Rate-limited. Waiting {wait}s…")
                    time.sleep(wait)
                elif exc.http_status == 403 and len(batch_ids) > 1:
                    # Fallback: split batch in half and retry
                    mid = len(batch_ids) // 2
                    batch_ids = batch_ids[:mid]
                    print(f"Received 403, splitting batch and retrying with {batch_ids}")
                    continue
                else:
                    raise  # re-throw other errors

        for feat in features_batch:
            if feat:  # skip None for local or unavailable tracks
                features_map[feat["id"]] = feat
        time.sleep(RATE_DELAY)

    return features_map


# ── Mood classification ─────────────────────────────────────────────────────
def classify_mood(features: dict) -> str:
    """Return the mood bucket for a track based on its audio features."""
    energy = features["energy"]
    danceability = features["danceability"]
    valence = features["valence"]
    tempo = features["tempo"]
    acoustic = features["acousticness"]

    if energy < ENERGY_LOW and danceability < DANCE_LOW:
        return "Chill"
    if valence > VALENCE_HIGH:
        return "Feel‑Good"
    if danceability > DANCE_HIGH:
        return "Dance"
    if energy > ENERGY_HIGH and tempo > TEMPO_WORKOUT:
        return "Workout"
    if acoustic > ACOUSTIC_HIGH:
        return "Mellow"
    return "Misc & Other"


# ── Main routine ────────────────────────────────────────────────────────────
def main() -> None:
    """Build or update one playlist per mood bucket."""
    sp_client = authenticate_spotify()
    token_info = sp_client.auth_manager.get_cached_token()
    print(token_info)
    user_id = sp_client.me()["id"]

    track_ids = fetch_liked_track_ids(sp_client)
    print(f"Fetched {len(track_ids)} liked track(s).")

    audio_features = fetch_audio_features(sp_client, track_ids)

    # Bucket track IDs by mood
    mood_dict: Dict[str, List[str]] = defaultdict(list)
    for tid in track_ids:
        feats = audio_features.get(tid)
        if feats:
            bucket = classify_mood(feats)
            mood_dict[bucket].append(tid)

    # Summary
    for bucket in MOOD_BUCKETS:
        print(f"{bucket}: {len(mood_dict.get(bucket, []))} track(s)")

    # Create/update playlists
    for bucket, ids in mood_dict.items():
        playlist_name = f"{PLAYLIST_PREFIX} - {bucket}"
        description = f"Auto‑generated {bucket} playlist {DESCRIPTION_TAG}"

        # Check if playlist exists
        playlist_id = None
        page = sp_client.current_user_playlists(limit=50)
        while page and not playlist_id:
            for pl in page["items"]:
                if pl["owner"]["id"] == user_id and pl["name"].lower() == playlist_name.lower():
                    playlist_id = pl["id"]
                    break
            page = sp_client.next(page) if page.get("next") else None

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

        # Add tracks in chunks of 100
        for start in range(0, len(ids), 100):
            sp_client.playlist_add_items(playlist_id, ids[start : start + 100])
            time.sleep(RATE_DELAY)


if __name__ == "__main__":
    main()
