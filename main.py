import json
import logging
import time
from configparser import ConfigParser

import pandas as pd

from constants import CAPTION, IMG_PROMPT
from instagram import Instagram
from spotify import Spotify
from utils import create_hashtag, get_handle, get_image, get_img_prompt, get_lyrics

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

config = ConfigParser()
config.read("config.ini")

IG_ID = config["instagram"]["IG_ID"]
INSTA_TOKEN = config["instagram"]["TOKEN"]

CLIENT_ID = config["spotify"]["CLIENT_ID"]
CLIENT_SECRET = config["spotify"]["CLIENT_SECRET"]

ENABLE_GENAI = True
GEN_IMG_URL = None
# GEN_IMG_URL = ""

with open("user.json", "r") as f:
    user = json.load(f)

spot = Spotify(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user=user)
insta = Instagram(IG_ID, INSTA_TOKEN)

while True:
    try:
        current = spot.get_currently_playing()
        if current:
            with open("current.json", "w") as f:
                json.dump(current, f)
        else:
            logging.info("Nothing is playing...")
            time.sleep(120)
            continue

        track = current["item"]["name"]
        artist = current["item"]["artists"][0]["name"]
        album = current["item"]["album"]["name"]
        album_id = current["item"]["album"]["id"]

        logging.info(f"Currently playing: `{track}` by `{artist}` / `{album}`")

        df = pd.read_csv("archive.tsv", sep="\t")
        # if artwork not in last 30 played items
        # recent_album_ids = df["album_id"].drop_duplicates(keep="last").tail(30x).values
        recent_album_ids = df.tail(30)["album_id"].values
        if album_id not in recent_album_ids and (
            current["context"]["type"] != "album"
            or current["context"]["uri"] == current["item"]["album"]["uri"]
        ):

            logging.info("Preparing new post...")

            gen_img_url = None
            image_url = current["item"]["album"]["images"][0]["url"]

            lyrics_str = get_lyrics(track, artist) or ""

            # gen img flow
            if lyrics_str:
                if GEN_IMG_URL:
                    gen_img_url = GEN_IMG_URL
                    img_prompt = ""

                elif ENABLE_GENAI:
                    # get artist genres
                    artist_obj = spot.get_artists(
                        ids=[current["item"]["artists"][0]["id"]]
                    )
                    genres = ", ".join(artist_obj[0]["genres"])
                    if genres:
                        logging.info(f"Genres: {genres}")
                        genres = f"`{genres}` "

                    prompt = IMG_PROMPT.format(
                        song=track,
                        artist=artist,
                        lyrics=lyrics_str,
                        genres=genres,
                    )

                    img_prompt = get_img_prompt(prompt)
                    print()
                    print(img_prompt)

                    gen_img_url = get_image(img_prompt)
                    # gen_img_url = get_image("DO NOT CHANGE THE FOLLOWING PROMPT:\n" + img_prompt)

                lyrics_str += "\n\n"

            # get handle and hashtags
            handle = get_handle(artist)
            if handle:
                hash_items = current["item"]["artists"] + [current["item"]["album"]]
                artist_tag = "@" + handle
            else:
                hash_items = current["item"]["artists"][1:] + [current["item"]["album"]]
                artist_tag = create_hashtag(artist)
            hashtags = " ".join(set(create_hashtag(x["name"]) for x in hash_items))

            # prepare caption
            caption = CAPTION.format(
                track=track,
                artist=artist,
                lyrics=lyrics_str,
                handle=artist_tag,
                hashtags=hashtags,
            )
            if len(caption) > 2200:
                caption = CAPTION.format(
                    track=track,
                    artist=artist,
                    lyrics="",
                    handle=artist_tag,
                    hashtags=hashtags,
                )

            # upload content
            if gen_img_url:
                # add img prompt to alt text if within char limit
                alt_text = img_prompt if len(img_prompt) <= 1000 else None
                img1 = insta.create_container(
                    url=gen_img_url,
                    is_carousel=True,
                    user_tag=handle,
                    alt_text=alt_text,
                )
                logging.info(f"Created gen img container: {img1}")

                img2 = insta.create_container(url=image_url, is_carousel=True)
                logging.info(f"Created album container: {img2}")

                res = insta.create_carousel(
                    caption=caption, children=[img1["id"], img2["id"]], user_tag=handle
                )
                logging.info(f"Created carousel: {res}")

            else:
                res = insta.create_container(
                    url=image_url, caption=caption, user_tag=handle
                )
                logging.info(f"Created container: {res}")

            # publish content
            res = insta.post_media(res["id"])
            logging.info(f"Posted media: {res}")

        # update archive
        new_row = {
            "track": track,
            "album": album,
            "artist": artist,
            "track_id": current["item"]["id"],
            "album_id": album_id,
        }
        last_row = df.iloc[-1] if not df.empty else None
        if last_row is None or any(last_row[col] != new_row[col] for col in new_row):
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv("archive.tsv", index=False, sep="\t")

    except Exception as e:
        print("Error:", str(e))

    time.sleep(90)
