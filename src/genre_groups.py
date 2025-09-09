from typing import Dict, List

# --------------------------------------------------------------------------- #
# Manual genre-cluster mapping                                                #
# Can be edited to your personal preferences                                  #
# --------------------------------------------------------------------------- #
GENRE_GROUPS: Dict[str, List[str]] = {
    "Hip Hop & Rap": [
        "rap", "emo rap", "gangster rap", "southern hip hop", "old school hip hop",
        "italian trap", "trap", "crunk", "j-rap", "uk drill", "brooklyn drill",
        "melodic rap", "rage rap", "alternative hip hop", "experimental hip hop",
        "french rap", "g-house", "drift phonk", "phonk", "conscious hip hop",
        "hip hop", "underground hip hop", "boom bap",
    ],
    "Rock & Alternative": [
        "rock", "alternative rock", "progressive rock", "psychedelic rock",
        "indie rock", "classic rock", "post-punk", "pop punk", "garage rock",
        "grunge", "britpop", "hardcore", "emo", "midwest emo", "post-grunge",
        "nu metal", "metalcore", "metal", "alternative metal", "rap metal",
        "industrial metal", "glam rock", "art rock", "folk rock", "southern rock",
        "jangle pop", "dream pop", "bedroom pop", "art pop", "baroque pop",
        "shoegaze", "indie pop rock", "punk rock", "math rock", "stoner rock",
        "post-rock",
    ],
    "Pop": [
        "pop", "soft pop", "indie", "indie soul", "french indie pop", "french pop",
        "norwegian pop", "variété française", "pop urbaine", "europop", "city pop",
        "j-pop", "italian singer-songwriter", "lo-fi", "k-pop", "dance pop",
        "bedroom pop", "pop rap", "boy band", "girl group",
    ],
    "Electronic & Dance": [
        "house", "tech house", "future house", "melodic house", "disco house",
        "afro house", "italo dance", "italo disco", "big room", "electro swing",
        "edm", "eurodance", "nu disco", "vaporwave", "synthwave", "synthpop",
        "idm", "trance", "psytrance", "hardstyle", "techno", "bassline",
        "drum and bass", "dubstep", "jungle", "hypertechno", "hyperpop",
        "electroclash", "new rave", "hi-nrg", "g-house", "progressive house",
        "progressive trance", "deep house", "minimal techno", "chillwave",
        "future bass", "downtempo", "ambient", "breakbeat",
    ],
    "Jazz, Soul & Funk": [
        "jazz fusion", "classic soul", "funk rock", "motown", "blues", "blues rock",
        "french jazz", "soul", "neo soul", "jazz", "vocal jazz", "bebop",
        "contemporary jazz", "smooth jazz", "r&b", "contemporary r&b", "funk",
    ],
    "World & Regional": [
        "latin alternative", "reggaeton", "reggae", "roots reggae", "dancehall",
        "afrobeats", "cumbia norteña", "mizrahi", "shatta", "brega", "anatolian rock",
        "dansktop", "zouk", "japanese vgm", "cumbia", "salsa", "korean ost",
        "mariachi", "flamenco", "bossa nova", "tango", "forró", "highlife", "afrobeat",
        "carioca funk",
    ],
    "Classical & Score": [
        "classical", "orchestral", "contemporary classical", "early music",
        "baroque", "romantic", "opera", "chamber music", "choral", "symphony",
        "film score", "video game music", "soundtrack", "modern classical",
    ],
    "Misc & Other": [
        "soundtrack", "anime", "anime rap", "christmas", "new age", "dark ambient",
        "cold wave", "experimental", "anti-folk", "industrial", "noise",
        "spoken word", "comedy", "children’s music", "field recording",
    ],
}
