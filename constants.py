CAPTION = """Listening to {track} by {artist} {handle}

{lyrics} @spotify @spotifyuk {hashtags}
"""

# IMG_PROMPT = """{lyrics}

# Create {genres}artwork capturing one or more of the themes in the above lyrics for `{song}` by `{artist}`. The image should be captivating and may include elements present in the song title, artist name, or song lyrics. Choose a distinct style for the art, and make sure the resulting image is high definition."""


# IMG_PROMPT = """{lyrics}

# Generate a visually striking, high-resolution {genres}album artwork inspired by the above lyrics for `{song}` by `{artist}`. Choose a single distinctive art style that fits the themes in the lyrics (eg. surrealism, glitchcore, vaporwave, neo-expressionism, etc.)

# Describe what you want to see in the artwork instead of references to the song/lyrics. Prioritize aesthetic impact.

# The generated artwork should either be hyper photorealistic, or an extremely professional digital artwork or painting. It should not look like basic illustration.
# """


IMG_PROMPT = """You are an expert prompt engineer working with the dall-e-3 image generation model to create WILDEST, most unusual paintings (no digital art) inspired by song lyrics.

For the following lyrics for `{song}` by `{artist}`, create a prompt to generate a high-resolution {genres}piece of art. Choose distinctive art styles that fit the themes in the lyrics. Describe what you want to see in the artwork without making references to the song or lyrics.

Lyrics:
{lyrics}

Feel free to include elements present in the song title or song lyrics, or any associated with the artist. Be creative! Don't pick the most obvious scenes or framings for the subject matter.

Respond with the text for the prompt ONLY.
"""
