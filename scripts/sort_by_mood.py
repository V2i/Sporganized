"""Sort Spotify liked tracks into mood playlists using AcousticBrainz API + musicbrainzngs."""

import sys
import os
import time
from collections import defaultdict
from typing import Dict, List, Optional

import musicbrainzngs
import numpy as np
import requests
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import functions from other files
from src.authenticate_spotify import authenticate_spotify
from src.fetch_from_spotify import fetch_spotify_likes

# ── Constants ─────────────────────────────────────────────────────────────
RATE_DELAY = 0.3
N_CLUSTERS = 5
PLAYLIST_PREFIX = "Mood"
DESCRIPTION_TAG = "[AUTO-AB]"
MOOD_LABELS = ("Chill", "Feel‑Good", "Dance", "Workout", "Mellow")
ACOUSTIC_API_BASE = "https://acousticbrainz.org/api/v1"

# ── Init MusicBrainz client ───────────────────────────────────────────────
musicbrainzngs.set_useragent("SporganizedMoodSorter", "1.0", None)
musicbrainzngs.set_rate_limit(limit_or_interval=False, new_requests=1)


# ── MusicBrainz lookup (via musicbrainzngs) ───────────────────────────────
def mbid_for_isrc(isrc: str) -> Optional[str]:
    try:
        result: Dict = musicbrainzngs.get_recordings_by_isrc(isrc)
        mbid = result.get('isrc', {}).get('recording-list', [])[0].get('id')
        return mbid if mbid else None
    except musicbrainzngs.ResponseError as e:
        print(f"MusicBrainz error for ISRC {isrc}: {e}")
    except Exception as e:
        print(f"Unexpected error for ISRC {isrc}: {e}")
    return None

# ── AcousticBrainz query ────────────────────────────────────────────────────
def get_features_from_ab(mbid: str) -> Optional[List[float]]:
    try:
        url = f"{ACOUSTIC_API_BASE}/{mbid}/low-level"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        data: Dict = r.json()
        lowlevel: Dict = data.get('lowlevel', {})
        rhythm: Dict = data.get('rhythm', {})
        energy: Dict = lowlevel.get('spectral_energy', {})
        return [
            rhythm.get('danceability', 0),
            rhythm.get('bpm', 0),
            energy.get('mean', 0),
            lowlevel.get('average_loudness', 0)
        ]
    except Exception as e:
        print(f"AB fetch failed for {mbid}: {e}")
        return None

# ── ML helpers ─────────────────────────────────────────────────────────────
def cluster_features(mat: np.ndarray):
    scaler = StandardScaler()
    X = scaler.fit_transform(mat)
    labels = KMeans(n_clusters=N_CLUSTERS, random_state=42).fit_predict(X)
    return labels

def map_clusters_to_moods(mat: np.ndarray, labels: np.ndarray):
    arr = []
    for k in range(N_CLUSTERS):
        sub = mat[labels == k]
        if sub.size:
            arr.append((k, sub[:,2].mean(), sub[:,1].mean()))
    arr.sort(key=lambda x: (x[1], x[2]))
    return {idx: mood for (idx, *_), mood in zip(arr, MOOD_LABELS)}

# ── Main function ──────────────────────────────────────────────────────────
def main():
    sp = authenticate_spotify()
    uid = sp.me()['id']
    tracks = fetch_spotify_likes(sp)
    print(f"Got {len(tracks)} liked tracks with ISRCs")

    feats, ids = [], []
    for t in tracks:
        mbid = mbid_for_isrc(t['isrc'])
        if not mbid:
            continue
        f = get_features_from_ab(mbid)
        if f and all(v > 0 for v in f):
            feats.append(f)
            ids.append(t['id'])
        time.sleep(RATE_DELAY)

    if not feats:
        print("No AcousticBrainz data found—exiting.")
        return
    print(f"Valid feature vectors: {len(feats)} / {len(tracks)}")

    mat = np.array(feats)
    labels = cluster_features(mat)
    cmap = map_clusters_to_moods(mat, labels)

    bucket = defaultdict(list)
    for tid, lbl in zip(ids, labels):
        bucket[cmap[lbl]].append(tid)

    for mood in MOOD_LABELS:
        print(f"{mood}: {len(bucket[mood])} tracks")

    for mood, tids in bucket.items():
        if not tids:
            continue
        pname, desc = f"{PLAYLIST_PREFIX} - {mood}", f"Auto‑{mood} {DESCRIPTION_TAG}"
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
