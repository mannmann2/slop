# slop

Monitors Spotify playback and auto-posts AI-generated art to Instagram whenever a new album is detected.

## What it does

1. Polls Spotify every 90 seconds for the currently playing track
2. When a new album is detected (not in the last 30 posts), fetches lyrics via Genius
3. Uses Gemini to write an image generation prompt inspired by the lyrics and artist genres
4. Generates artwork with **gpt-image-2** (OpenAI)
5. Commits the image to a GitHub repository and uses the raw URL to post an Instagram carousel (generated art + album cover)

## Setup

### Dependencies

```
pip install -r reqiurements.txt
```

### config.ini

```ini
[spotify]
CLIENT_ID     = ...
CLIENT_SECRET = ...

[instagram]
IG_ID  = ...
TOKEN  = ...

[gemini]
API_KEY = ...
MODEL   = gemini-2.0-flash

[openai]
API_KEY = ...

[genius]
TOKEN = ...

[github]
TOKEN = ghp_...
REPO  = username/repo-name
PATH  = images
```

### user.json

Spotify OAuth token cache — generated on first run.

### archive.tsv

Tracks posted albums. Create an empty one before first run:

```
track	album	artist	track_id	album_id
```

## Running

```
python main.py
```
