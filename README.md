# Camelot Song Recommender

A command-line song recommender for DJs that finds your favorite track's best mixing matches by scoring every other song on harmonic key (Camelot wheel), tempo, and vibe with a hand-weighted similarity formula.

## How it works

Each song is described by six traits. For every pair of songs, each trait gets a score from 0 (nothing alike) to 1 (identical), and the scores are blended using fixed weights:

```
similarity = 0.25 × key
           + 0.25 × bpm
           + 0.15 × energy
           + 0.15 × valence
           + 0.10 × danceability
           + 0.10 × acousticness
```

The weights add up to 1, so the result is shown as a percent match.

- **Key:** Spotify's numeric key and mode are converted to Camelot notation (e.g. 8A, 9B). Distance is measured around the wheel, so 12 and 1 count as neighbors, with a penalty for switching between major and minor.
- **BPM:** Songs within 10 BPM score well, and half-time / double-time tempos count as a match.
- **Energy, valence, danceability, acousticness:** Scored by how close the two values are.

This is a content-based recommender: it uses each song's own audio features, not other listeners' behavior. There is no training or machine learning involved, and the weights are chosen by hand. To change what matters most when mixing, edit the `WEIGHTS` dictionary in `main.py`.

## Requirements

- Python 3.8 or newer
- No third-party packages (only the standard library `csv` module)

## Your data

The script reads a CSV export of your songs with Spotify audio features. It expects these column names:

| Column | Meaning |
|---|---|
| `Track Name` | Song title |
| `Artist Name(s)` | Artist(s), separated by semicolons |
| `Tempo` | BPM |
| `Key` | 0–11 (0 = C, 1 = C#, ... 11 = B) |
| `Mode` | 1 = major, 0 = minor |
| `Energy` | 0–1 |
| `Valence` | 0–1 |
| `Danceability` | 0–1 |
| `Acousticness` | 0–1 |

Save the file as `my_go_to_songs.csv` in the same folder as `main.py`, or change the filename in the script. Rows with missing or invalid values are skipped, and duplicate title/artist pairs are removed.

### Getting your data with Exportify

[Exportify](https://exportify.app/) is a free, open-source web tool that exports your Spotify playlists to CSV. It runs in your browser and saves nothing.

1. Open Exportify and click **Get Started**.
2. Log in to Spotify and grant it read-only access to your playlists.
3. Turn on **Include audio features data** (this adds Danceability, Energy, Key, Mode, Tempo, Valence, Acousticness and more).
4. Click **Export** next to a playlist, or **Export All** to get a ZIP with a CSV for every playlist.
5. Rename the CSV to `my_go_to_songs.csv` and put it next to `main.py`.

Note: Spotify restricted its audio features endpoint for newer apps in late 2024, so the audio features option may not work for everyone. If your export is missing the Danceability, Energy, Tempo, Key or Mode columns, the script can't use it, and you'll need a dataset or another source that includes them.

## Usage

```
python main.py
```

Type part of a song or artist name, pick the song from the list of matches, and you'll get the 10 best matches:

```
If you like "Song Title", try:
   92% match  Another Song - Some Artist  (124 BPM, 8A)
   88% match  Third Song - Other Artist  (122 BPM, 9A)
   ...
```

Press Enter on an empty search to quit.

## Ideas for improvement

- Scale the BPM tolerance relative to the song's tempo instead of a fixed 10 BPM
- Let the user adjust the weights while running the program
- Filter results to only keys that mix harmonically
- Export recommendations as a playlist
