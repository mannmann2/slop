import logging
import re
import time
from configparser import ConfigParser

import requests
from google import genai
from openai import OpenAI

config = ConfigParser()
config.read("config.ini")
gemini_client = genai.Client(api_key=config["gemini"]["API_KEY"])
openai_client = OpenAI(api_key=config["openai"]["API_KEY"])

WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
INSTAGRAM_PROPERTY_ID = "P2003"  # P2003 is the Wikidata property for Instagram username


def create_hashtag(text: str) -> str:
    """
    Removes all non-alphanumeric characters from a string.

    Args:
        text: The input string.

    Returns:
        The string with only alphanumeric characters.
    """
    hash_text = re.sub(r"[^a-zA-Z0-9]", "", text.lower())
    return "#" + hash_text if hash_text else ""


def get_img_prompt(prompt: str) -> str:

    response = gemini_client.models.generate_content(
        model="gemini-2.5-pro", contents=prompt
    )
    return response.text


def get_image(prompt: str) -> str | None:
    """Generate an image using OpenAI's DALL-E 3 model with a retry mechanism.

    Args:
        prompt: The text prompt for image generation.

    Returns:
        The URL of the generated image, or None if it fails after retries.
    """
    attempts = 2
    for i in range(attempts):
        try:
            img = openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
                response_format="url",
            )
            print(f"dall-e revised prompt: {img.data[0].revised_prompt}")

            url = img.data[0].url
            print(f"Image URL: {url}")
            return url

        except Exception as e:
            # Wait a second before retrying
            if i < attempts - 1:
                time.sleep(1)
            else:
                logging.error(str(e))

    return None


def get_wikidata(artist: str) -> str | None:
    """
    Searches Wikidata for an artist and retrieves their Instagram username if available.

    Args:
        artist: The name of the artist to search for.

    Returns:
        The artist's Instagram username as a string, or None if not found.
    """
    # The requests library automatically URL-encodes parameters
    search_params = {
        "action": "wbsearchentities",
        "search": artist,
        "language": "en",
        "format": "json",
    }
    try:
        response = requests.get(WIKIDATA_API_URL, params=search_params)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        search_results = response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Wikidata search request failed for '{artist}': {e}")
        return None
    except ValueError:  # Catches JSON decoding errors
        logging.error(f"Failed to decode JSON from Wikidata search for '{artist}'")
        return None

    if not search_results.get("search"):
        logging.info(f"No Wikidata search results for artist: '{artist}'")
        return None

    qid = search_results["search"][0].get("id")

    entity_params = {
        "action": "wbgetentities",
        "ids": qid,
        "format": "json",
        "props": "claims",
    }
    try:
        response = requests.get(WIKIDATA_API_URL, params=entity_params)
        response.raise_for_status()
        entity_data = response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Wikidata entity request failed for QID '{qid}': {e}")
        return None
    except ValueError:
        logging.error(
            f"Failed to decode JSON from Wikidata entity request for QID '{qid}'"
        )
        return None

    # Safely navigate the nested structure to find the Instagram username
    try:
        claims = entity_data["entities"][qid]["claims"]
        instagram_claims = claims[INSTAGRAM_PROPERTY_ID]
        return instagram_claims[0]["mainsnak"]["datavalue"]["value"]
    except (KeyError, IndexError):
        # This is not an error, just means the property doesn't exist for this entity.
        logging.info(f"Could not find Instagram username for '{artist}' (QID: {qid}).")
        return None
