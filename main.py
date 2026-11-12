import csv
CSV_FILES = "my_go_to_songs.csv"

##Turn Spotify's key numbers into Camelot keys
##Spotify stores the key as 0-11 (0=C, 1=C#, 2=D... 11=B) and the mode as #1 major, 0 = minor.
##DJs use the Camelot Wheel for music analyzing like (8A, 9B...) so we convert.
##Whole idea is based on hand-weighted similarity formula

##Dictionary for CAMELOT KEYS

CAMELOT = {
    # minor songs (mode 0) end in A
    (0, 0): "5A", (1, 0): "12A", (2, 0): "7A", (3, 0): "2A",
    (4, 0): "9A", (5, 0): "4A", (6, 0): "11A", (7, 0): "6A",
    (8, 0): "1A", (9, 0): "8A", (10, 0): "3A", (11, 0): "10A",
    # major songs (mode 1) end in B
    (0, 1): "8B", (1, 1): "3B", (2, 1): "10B", (3, 1): "5B",
    (4, 1): "12B", (5, 1): "7B", (6, 1): "2B", (7, 1): "9B",
    (8, 1): "4B", (9, 1): "11B", (10, 1): "6B", (11, 1): "1B"

}

#(load_tracks) read the spotify-export CSV and return one dictionary per song
def load_tracks (filename = "my_go_to_songs.csv"):
    tracks = []
    seen = set()  #to remember items and ignore repeats
    with open(filename, encoding="utf-8-sig", newline="") as f:

        for row in csv.DictReader(f): #read the file one row at a time, so each row is like a dictionary

            try: #create a dictionary describing one song
                track = {
                    "title": row ["Track Name"],
                    "artist": row ["Artist Name(s)"].replace (";", ","),
                    "bpm":float(row["Tempo"]),
                    "key": CAMELOT[(int (row["Key"]), int (row["Mode"]))],
                    "energy": float(row["Energy"]),
                    "valence": float(row["Valence"]),
                    "dance": float(row["Danceability"]),
                    "acoustic": float(row["Acousticness"]),
                }
            except (ValueError, KeyError, TypeError):
                continue
            ident = (track["title"], track["artist"])
            if ident in seen:
                continue       #have we already added this song? if yes skip it if no then remember it NOW
            seen.add(ident)
            tracks.append(track)
        return tracks

# (bpm_score) takes two tempos, returns a score from 0 to 1
# 1 = same pace
# Smallest of three gaps: normal, a vs double b, double a vs b, so half/double-time songs count as the same pace.
def bpm_score(a, b):
    gap = min(abs(a - b), abs(a - 2 * b), abs(2 * a - b))
    return max(0, 1 - gap / 10)


#(key_score) rate how well two Camelot keys mix
def key_score(a, b):
    num_a = int (a[:-1])
    letter_a = a[-1]
    num_b = int (b[:-1])
    letter_b = b[-1]

    gap = abs(num_a - num_b)            # how far apart the numbers are
    gap = min(gap, 12 - gap)            # the wheel is a circle: 12 and 1 are neighbours, so take the shorter way round
    if letter_a != letter_b:
        gap += 1
    return max(0, 1 - gap / 3)

#(closeness) rates how similiar two 0-to-1 values are (like key, bpm etc.)
#1 = identical, 0 = opposite ends of the scale
def closeness(a,b):
    return 1 - abs (a-b)

WEIGHTS = {                             # how important each trait is; all numbers add up to 1
    "key": 0.25, "bpm": 0.25,
    "energy": 0.15, "valence": 0.15,
    "dance": 0.10, "acoustic": 0.10,
}

#(similarity) combines six trait scores (key, bpm, energy, valence, dance, acoustic) into one OVERALL match using weights.
def similarity(t1, t2):                 # t1 and t2 are two songs (dictionaries)
    return (
         WEIGHTS["key"]      * key_score(t1["key"], t2["key"])
        + WEIGHTS["bpm"]      * bpm_score(t1["bpm"], t2["bpm"])
        + WEIGHTS["energy"]   * closeness(t1["energy"], t2["energy"])
        + WEIGHTS["valence"]  * closeness(t1["valence"], t2["valence"])
        + WEIGHTS["dance"]    * closeness(t1["dance"], t2["dance"])
        + WEIGHTS["acoustic"] * closeness(t1["acoustic"], t2["acoustic"])

    )

# (recommend) score every other song against the favourite and return how many best matches as (score, song) pairs, highest score first
def recommend(favorite, tracks, how_many=10):
    scored = []                                 # empty list for (score, song) pairs
    for t in tracks:                            # go through every song
        if t is not favorite and t["title"] != favorite["title"]:
                                                # skip the song itself and anything with the same title
            scored.append((similarity(favorite, t), t))
                                                # compute the score, store it together with the song
    scored.sort(key=lambda pair: pair[0], reverse=True)

                                                # "lambda" is a tiny one-line function telling sort what to look at;
                                                # reverse=True puts the highest score first
    return scored[:how_many]

#(describe) Turn a song into one display line: "Title - Artist (BPM, Key)"
def describe(t):                                # [:10] = "just the first 10 items"
    return f"{t['title']} - {t['artist']}  ({t['bpm']:.0f} BPM, {t['key']})"

#(find_song) ask the user to type part of a title or artist, show up to 10 matches, and return the song they choose.
#Returns "quit" if they press Enter on an empty search, or None if there is no match or no valid pick (so the caller seacher again)
def find_song(tracks):
    text = input("\nType part of a song or artist name (Enter to quit): ").strip().lower()
    if text == "":
        return "quit"
    matches = [t for t in tracks if text in t["title"].lower() or text in t["artist"].lower()]
    if not matches:
        print("No match. Try another spelling.")
        return None
    if len(matches) == 1:
        return matches[0]
    shown = matches[:10]
    for i, t in enumerate(shown, start=1):
        print(f"  {i:2}. {describe(t)}")
    if len(matches) > 10:
        print(f"  ...and {len(matches) - 10} more. Type more letters to narrow it down.")
    pick = input("Pick a number (or Enter to search again): ").strip()
    if pick.isdigit() and 1 <= int(pick) <= len(shown):


        return shown[int(pick) - 1]
    return None

#(Main) loads the songs, then repeatedly let the user pick a favourite and prints its recommendations as percent matches, until they quit
def main():
    tracks = load_tracks()
    print(f"Loaded {len(tracks)} songs from {CSV_FILES}.")
    while True:
        favorite = find_song(tracks)
        if favorite == "quit":
            print("Bye!")
            break
        if favorite is None:
            continue
        print(f"\nIf you like \"{favorite['title']}\", try:")
        for score, t in recommend(favorite, tracks):
            print(f"  {score * 100:3.0f}% match  {describe(t)}")


if __name__ == "__main__":
    main()
