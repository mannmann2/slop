import json
import time
import logging
from configparser import ConfigParser

import pandas as pd

from constants import CAPTION, IMG_PROMPT
from instagram import Instagram
from spotify import Spotify
from genius import Genius
from utils import create_hashtag, get_wikidata, get_img_prompt, get_image

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

config = ConfigParser()
config.read('config.ini')

IG_ID = config["instagram"]["IG_ID"]
INSTA_TOKEN = config["instagram"]["TOKEN"]
GENIUS_TOKEN = config["genius"]["TOKEN"]

CLIENT_ID = config["spotify"]["CLIENT_ID"]
CLIENT_SECRET = config["spotify"]["CLIENT_SECRET"]

ENABLE_GENAI = True
GEN_IMG_URL = None
# GEN_IMG_URL = "https://oaidalleapiprodscus.blob.core.windows.net/private/org-EGAV58Sx57CtmQ97HnglER5U/user-fN38DqAeQd6YbDH02pZzajR5/img-B750oKjC0v7GTdp2o42jfMhS.png?st=2025-07-08T06%3A53%3A10Z&se=2025-07-08T08%3A53%3A10Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=52f8f7b3-ca8d-4b21-9807-8b9df114d84c&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2025-07-07T13%3A26%3A47Z&ske=2025-07-08T13%3A26%3A47Z&sks=b&skv=2024-08-04&sig=UFenGomvXJGVCeIC7QG61yIZk1JCQLC%2B8Y4MeILJe78%3D"

with open("user.json", "r") as f:
    user = json.load(f)

spot = Spotify(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user=user)
insta = Instagram(IG_ID, INSTA_TOKEN)
gen = Genius(token=GENIUS_TOKEN)

while True:
    # try:
    item = spot.get_currently_playing()

    if item["item"] is None:
        logging.info("Nothing is playing...")
        time.sleep(60)
        continue

    new_row = {
        'track': item['item']['name'],
        'album': item['item']['album']['name'],
        'artist': item['item']['artists'][0]['name'],
        'track_id': item['item']['id'],
        'album_id': item['item']['album']['id'],
    }
    logging.info(f"Currently playing: {new_row}")

    df = pd.read_csv('archive.csv')
    # if artwork not in last 30 played items TODO should check last 30 posted?
    if new_row['album_id'] not in df.tail(30)['album_id'].values:

        logging.info("Preparing new post...")

        gen_img_url = None
        img_prompt = None
        image_url = item['item']['album']['images'][0]['url']

        lyrics_str = gen.get_lyrics(new_row['track'], new_row['artist']) or ""

        # gen img flow
        if lyrics_str:
            if GEN_IMG_URL:
                gen_img_url = GEN_IMG_URL

            elif ENABLE_GENAI:
                # get artist genres
                artist_obj = spot.get_artists(ids=[item['item']['artists'][0]['id']])
                genres = ', '.join(artist_obj[0]['genres'])
                if genres:
                    genres = f"`{genres}` "

                prompt = IMG_PROMPT.format(song=new_row["track"], artist=new_row["artist"], lyrics=lyrics_str, genres=genres)
                print(prompt)

                img_prompt = get_img_prompt(prompt)
                print(img_prompt)

                gen_img_url = get_image(img_prompt)
                # gen_img_url = get_image("DO NOT CHANGE THE FOLLOWING PROMPT:\n" + img_prompt)

            lyrics_str += "\n\n"

        # get handle and hashtags
        handle = get_wikidata(new_row["artist"])
        if handle:
            hash_items = item['item']['artists'] + [item['item']['album']]
            artist_tag = "@" + handle
        else:
            hash_items = item['item']['artists'][1:] + [item['item']['album']]
            artist_tag = create_hashtag(new_row["artist"])
        hashtags = " ".join(create_hashtag(x['name']) for x in hash_items)

        # prepare caption
        caption = CAPTION.format(track=new_row['track'], artist=new_row['artist'], lyrics=lyrics_str, handle=artist_tag, hashtags=hashtags)
        if len(caption) > 2200:
            caption = CAPTION.format(track=new_row['track'], artist=new_row['artist'], lyrics="", handle=artist_tag, hashtags=hashtags)

        # upload content
        if gen_img_url:
            # add img prompt to alt text if within char limit
            alt_text = img_prompt if img_prompt and len(img_prompt) <=1000 else None
            img1 = insta.create_container(url=gen_img_url, is_carousel=True, user_tag=handle, alt_text=alt_text)
            logging.info(f"Created gen img container: {img1}")

            img2 = insta.create_container(url=image_url, is_carousel=True)
            logging.info(f"Created album container: {img2}")

            res = insta.create_carousel(caption=caption, children=[img1["id"], img2['id']])
            logging.info(f"Created carousel: {res}")

        else:
            res = insta.create_container(url=image_url, caption=caption, user_tag=handle)
            logging.info(f"Created container: {res}")

        # publish content
        res = insta.post_media(res['id'])
        logging.info(f"Posted media: {res}")

    # update archive
    last_row = df.iloc[-1] if not df.empty else None
    if last_row is None or any(last_row[col] != new_row[col] for col in new_row):
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv('archive.csv', index=False)

    # except Exception as e:
    #     print("Error:", str(e))

    time.sleep(60)
