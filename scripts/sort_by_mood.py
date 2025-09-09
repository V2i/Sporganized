"""Sort Spotify liked tracks into mood playlists using multi-source fallback:
MusicBrainz, Last.fm, Discogs, Genius.

Environment variables to be set in a `.env` file (handled by python‑dotenv):
    - SPOTIPY_CLIENT_ID
    - SPOTIPY_CLIENT_SECRET
    - SPOTIPY_REDIRECT_URI
"""

import os
import time
from collections import defaultdict
from typing import Dict, List, Optional
import musicbrainzngs
import numpy as np
import requests
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ── Constants & Functions ─────────────────────────────────────────────────
from src.fetch_from_spotify import fetch_spotify_likes
from src.authenticate_spotify import authenticate_spotify
import src.constants

# ── Init MusicBrainz client ───────────────────────────────────────────────
musicbrainzngs.set_useragent("SporganizedMoodSorter", "1.0", None)
musicbrainzngs.set_rate_limit(limit_or_interval=False, new_requests=1)


# ── MusicBrainz lookup ────────────────────────────────────────────────────
def mbid_for_isrc(isrc: str) -> Optional[str]:
    try:
        result: Dict = musicbrainzngs.get_recordings_by_isrc(isrc)
        return result.get('isrc', {}).get('recording-list', [])[0].get('id')
    except Exception:
        return None

# ── Last.fm lookup ─────────────────────────────────────────────────────────
def get_lastfm_tags(artist: str, track: str) -> List[str]:
    API_KEY = os.getenv("LASTFM_API_KEY")
    url = f"{src.constants.LASTFM_API_URL}?method=track.gettoptags&artist={artist}&track={track}&api_key={API_KEY}&format=json"
    try:
        r = requests.get(url, timeout=10)
        tags = r.json().get("toptags", {}).get("tag", [])
        return [tag["name"] for tag in tags if float(tag.get("count", 0)) > 10]
    except Exception:
        return []

# ── Discogs lookup ─────────────────────────────────────────────────────────
def get_discogs_genre(artist: str, track: str) -> List[str]:
    TOKEN = os.getenv("DISCOGS_TOKEN")
    headers = {"Authorization": f"Discogs token={TOKEN}"}
    url = f"{src.constants.DISCOG_API_URL}?artist={artist}&track={track}&token={TOKEN}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        results = r.json().get("results", [])
        return results[0].get("genre", []) if results else []
    except Exception:
        return []

# ── Placeholder for Genius or fallback features ────────────────────────────
def get_fallback_features(track: dict) -> List[float]:
    tags = get_lastfm_tags(track['artist'], track['name'])
    genres = get_discogs_genre(track['artist'], track['name'])
    score = float(bool(set(tags + genres)))  # crude feature: 1 if any metadata found
    return [score, 0, 0, 0] if score else []

# ── ML helpers ─────────────────────────────────────────────────────────────
def cluster_features(mat: np.ndarray):
    scaler = StandardScaler()
    X = scaler.fit_transform(mat)
    labels = KMeans(n_clusters=src.constants.N_CLUSTERS, random_state=42).fit_predict(X)
    return labels

def map_clusters_to_moods(mat: np.ndarray, labels: np.ndarray):
    arr = []
    for k in range(src.constants.N_CLUSTERS):
        sub = mat[labels == k]
        if sub.size:
            arr.append((k, sub[:,0].mean()))
    arr.sort(key=lambda x: x[1])
    return {idx: mood for (idx, *_), mood in zip(arr, src.constants.MOOD_LABELS)}

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    sp = authenticate_spotify()
    uid = sp.me()['id']
    tracks = fetch_spotify_likes(sp)
    print(f"Got {len(tracks)} liked tracks with ISRCs")

    feats, ids = [], []
    for t in tracks:
        mbid = mbid_for_isrc(t['isrc'])
        f = get_fallback_features(t)  # replace AB call with fallback
        if f:
            feats.append(f)
            ids.append(t['id'])
        time.sleep(src.constants.RATE_DELAY)

    if not feats:
        print("No usable metadata—exiting.")
        return

    print(f"Valid feature vectors: {len(feats)} / {len(tracks)}")
    mat = np.array(feats)
    labels = cluster_features(mat)
    cmap = map_clusters_to_moods(mat, labels)

    bucket = defaultdict(list)
    for tid, lbl in zip(ids, labels):
        bucket[cmap[lbl]].append(tid)

    for mood in src.constants.MOOD_LABELS:
        print(f"{mood}: {len(bucket[mood])} tracks")

    for mood, tids in bucket.items():
        if not tids:
            continue
        pname, desc = f"{src.constants.PLAYLIST_PREFIX} - {mood}", f"Auto‑{mood} {src.constants.DESCRIPTION_TAG}"
        pid = None
        pg = sp.current_user_playlists(limit=50)
        while pg:
            for pl in pg['items']:
                if pl['owner']['id'] == uid and pl['name'].lower() == pname.lower():
                    pid = pl['id']
                    break
            if pid or not pg['next']:
                break
            pg = sp.next(pg)

        if pid:
            print("Updating", pname)
            sp.playlist_replace_items(pid, [])
        else:
            print("Creating", pname)
            pid = sp.user_playlist_create(uid, pname, description=desc)['id']

        for i in range(0, len(tids), 100):
            sp.playlist_add_items(pid, tids[i:i+100])

if __name__ == "__main__":
    main()
