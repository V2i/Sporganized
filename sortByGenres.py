import os
import time
from collections import defaultdict
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

# ── 1. Load environment variables ──────────────────────────────────────────────
load_dotenv()
client_id     = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri  = os.getenv("SPOTIPY_REDIRECT_URI")

# ── 2. Spotify authentication ─────────────────────────────────────────────────
scope = "user-library-read playlist-modify-public playlist-modify-private ugc-image-upload"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id     = client_id,
    client_secret = client_secret,
    redirect_uri  = redirect_uri,
    scope         = scope
))
user_id = sp.me()['id']

# ── 3. Fetch all liked (saved) tracks ─────────────────────────────────────────
liked_tracks = []
results = sp.current_user_saved_tracks(limit=50)
while results:
    for item in results['items']:
        track = item['track']
        liked_tracks.append(track)
    results = sp.next(results) if results['next'] else None

print(f"Number of songs retrieved from liked tracks: {len(liked_tracks)}")

# ── 4. Collect unique artist IDs ──────────────────────────────────────────────
artist_ids = {artist['id'] for track in liked_tracks for artist in track['artists']}

# ── 5. Batch‑fetch genres for artists (handles API rate‑limits) ───────────────
def get_genres_for_artists(ids):
    artist_genres = {}
    for i in range(0, len(ids), 50):
        batch = list(ids)[i:i + 50]
        while True:
            try:
                artists_info = sp.artists(batch)['artists']
                break
            except SpotifyException as e:
                if e.http_status == 429:
                    wait = int(e.headers.get("Retry-After", 1))
                    print(f"Rate‑limited. Waiting {wait}s…")
                    time.sleep(wait)
                else:
                    raise
        for artist in artists_info:
            artist_genres[artist['id']] = artist.get('genres', [])
        time.sleep(0.2)          # polite delay
    return artist_genres

artist_genres = get_genres_for_artists(artist_ids)

# ── 6. Manual genre‑to‑group mapping  ─────────────────────────────────────────
genre_groups = {
    "Hip Hop & Rap": [
        "rap","emo rap","gangster rap","southern hip hop","old school hip hop",
        "italian trap","trap","crunk","j-rap","uk drill","brooklyn drill",
        "melodic rap","rage rap","alternative hip hop","experimental hip hop",
        "french rap","g-house","drift phonk","phonk"
    ],
    "Rock & Alternative": [
        "rock","alternative rock","progressive rock","psychedelic rock","indie rock",
        "classic rock","post-punk","pop punk","garage rock","grunge","britpop",
        "hardcore","emo","midwest emo","post-grunge","nu metal","metalcore",
        "metal","alternative metal","rap metal","industrial metal","glam rock",
        "art rock","folk rock","southern rock","jangle pop","dream pop",
        "bedroom pop","art pop","baroque pop","shoegaze"
    ],
    "Pop": [
        "pop","soft pop","indie","indie soul","french indie pop","french pop",
        "norwegian pop","variété française","pop urbaine","europop","city pop",
        "j-pop","italian singer-songwriter","lo-fi"
    ],
    "Electronic & Dance": [
        "house","tech house","future house","melodic house","disco house","afro house",
        "italo dance","italo disco","big room","electro swing","edm","eurodance",
        "nu disco","vaporwave","synthwave","synthpop","idm","trance","psytrance",
        "hardstyle","techno","bassline","drum and bass","dubstep","jungle",
        "hypertechno","hyperpop","electroclash","new rave","hi-nrg","g-house"
    ],
    "Jazz, Soul & Funk": [
        "jazz fusion","classic soul","funk rock","motown","blues","blues rock",
        "french jazz","soul","neo soul"
    ],
    "World & Regional": [
        "latin alternative","reggaeton","reggae","roots reggae","dancehall","afrobeats",
        "cumbia norteña","mizrahi","shatta","brega","anatolian rock","dansktop",
        "zouk","japanese vgm","cumbia","salsa"
    ],
    "Misc & Other": [
        "soundtrack","anime","anime rap","christmas","new age","dark ambient",
        "cold wave","experimental","anti-folk","industrial","noise"
    ]
}

def map_to_group(genre: str) -> str:
    for group, genres in genre_groups.items():
        if genre in genres:
            return group
    return "Misc & Other"

# ── 7. Group tracks by their genre‑cluster ────────────────────────────────────
group_dict = defaultdict(list)
for track in liked_tracks:
    # Use the first genre of the first artist as “main” genre, if available
    artist_id = track['artists'][0]['id']
    genres = artist_genres.get(artist_id, [])
    if genres:
        main_genre = genres[0]
        group = map_to_group(main_genre)
        group_dict[group].append(track['id'])

# Debug summary
for grp, ids in group_dict.items():
    print(f"{grp}: {len(ids)} track(s)")

# ── 8. Create (or update) one playlist per group ──────────────────────────────
folder_prefix = "Playlist"   # helps them sort together alphabetically
for group_name, track_ids in group_dict.items():
    playlist_name = f"{folder_prefix} - {group_name}"
    description   = f"Sporganized generated playlist · {group_name} [AUTO]"
    
    # Check if playlist already exists (idempotent)
    existing_id = None
    user_playlists = sp.current_user_playlists(limit=50)
    while user_playlists:
        for pl in user_playlists['items']:
            if pl['name'].lower() == playlist_name.lower() and pl['owner']['id'] == user_id:
                existing_id = pl['id']
                break
        if user_playlists['next'] and not existing_id:
            user_playlists = sp.next(user_playlists)
        else:
            break
    
    if existing_id:
        playlist_id = existing_id
        print(f"Updating playlist: {playlist_name}")
        sp.playlist_replace_items(playlist_id, [])  # clear it
    else:
        print(f"Creating playlist: {playlist_name}")
        playlist = sp.user_playlist_create(user_id, playlist_name, public=True, description=description)
        playlist_id = playlist['id']
    
    # Add tracks in batches of 100
    for i in range(0, len(track_ids), 100):
        sp.playlist_add_items(playlist_id, track_ids[i:i+100])
        time.sleep(0.2)  # avoid rate limit
