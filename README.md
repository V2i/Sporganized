# 🎵 Sporganized

<a href="https://github.com/V2i/Sporganized/actions/workflows/pylint.yml" target="_blank"><img src="https://github.com/V2i/Sporganized/actions/workflows/pylint.yml/badge.svg" alt="Code Quality" /></a>
<a href="https://github.com/V2i/Sporganized/blob/main/LICENSE" target="_blank"><img src="https://img.shields.io/badge/Licence-Apache_2.0-blue.svg" alt="Licence" /></a>

<a href="https://www.python.org/doc" target="_blank"><img src="https://img.shields.io/badge/Python-3.13-ffd343?logo=python" alt="Python" /></a>
<a href="https://pypi.org/project/python-dotenv" target="_blank"><img src="https://img.shields.io/badge/python--dotenv-1.1.0-ffd343?logo=pypi" alt="python-dotenv v1.1.0" /></a>
<a href="https://pypi.org/project/spotipy" target="_blank"><img src="https://img.shields.io/badge/spotipy-2.25.1-ffd343?logo=pypi" alt="spotipy v2.25.1" /></a>

**Sporganized** is a small Python application to automatically organize your liked Spotify tracks by **genre** (and optionally by mood, danceability, etc.).  
It uses the [Spotify Web API](https://developer.spotify.com/documentation/web-api/) and Spotipy to fetch your saved tracks, analyze them, and create curated playlists grouped by genre.

---

## ✅ Features

- ✅ Automatically fetch all your liked songs from Spotify  
- ✅ Extract artist genres via Spotify's metadata and other metadata from [Discog](https://www.discogs.com/fr/) and [LastFM](https://www.last.fm/)
- ✅ Group tracks by genre (you can customize or filter genre groups by editing <a href="./src/genre_groups.py">`genre_groups.py`</a>)  
- ✅ Group tracks by moop (using ML and metadata from other databases)
- ✅ Delete all the playlist created with scripts 
- ✅ Cross-platform support (tested on **Windows** and **Linux**)

---

## 📦 Requirements

- Python 3.7 or newer  
- A Spotify Developer Account (to get `client_id`, `client_secret`)  
- Git (for cloning, optional)  
- `spotipy`, `python-dotenv`

Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Setup

1. **Clone the repository** (or download as ZIP):

   ```bash
   git clone https://github.com/your-username/sporganized.git
   cd sporganized
   ```

2.  **Create your Spotify App (to get API credentials):**

   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Log in with your Spotify account
   - Click **"Create an App"**
   - Fill in:
     - **App name**: e.g., `Sporganized`
     - **App description**: e.g., `Organize liked songs by genre`
     - Agree to the terms
     - Click **Create**
   - Click **"Edit Settings"** on your new app
     - Under **Redirect URIs**, add:
       ```
       http://127.0.0.1:8888/callback
       ```
     - Click **Add** and then **Save**
   - Copy your **Client ID** and **Client Secret**

3. **Create a `.env` file**

    - Copy the `.env.exemple`
    - Rename it `.env`
    - Add your client **Client ID** and **Client Secret** from step 2

   ```
   SPOTIPY_CLIENT_ID=your_spotify_client_id
   SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
   ```

4. **Run any script:**

   - `python -m sort_by_genres.py`: This will authenticate via your browser (only the first time), fetch your liked songs, and start organizing them by genre.
   - `python -m sort_by_mood.py`: This script takes your liked songs and sorts them into playlists based on mood, using extra info from music databases like MusicBrainz, Last.fm, and Discogs.
   - `python -m delete_created_playlist.py`: Clean up your auto-generated playlists in one click. ⚠️ This deletes **ANY** playlists with `[AUTO]` in their description.

---

## 📁 File Structure

```
sporganized/
├── .env.example             # Example env config
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
├── LICENSE                  # License file
├── .gitignore               # Git ignore rules
├── .github/
│   └── workflows/
│       └── pylint.yml       # CI to lint the code
├── scripts/
│   ├── delete_created_playlist.py   # Delete generated playlist
│   ├── sort_by_genres.py            # Sort playlist by genre
│   └── sort_by_mood.py              # Sort playlist by mood
└── src/
    ├── authenticate_spotify.py      # Spotify auth handling
    ├── constants.py                 # Constants
    ├── fetch_from_spotify.py        # Get liked tracks
    └── genre_groups.py              # Genre grouping
```

---

## 💡 Ideas for Future

- Support tagging by **decade/year** or **country**
- Web-based interface
- Periodic auto-sync

---

## 🧑‍💻 Author

Made with ❤️ by <a href="https://www.linkedin.com/in/valentin-guyon">**Valentin Guyon**</a>.  
Feel free to fork, contribute or suggest features.

---

## 📜 License

This project is licensed under the <a href="./LICENSE">MIT License</a>.
