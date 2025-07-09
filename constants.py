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


IMG_PROMPT = """You are an expert prompt engineer for the dall-e-3 image generation model working with artists to create the most unique pieces of art inspired by their song lyrics.

{lyrics}

For the above lyrics for `{song}` by `{artist}`, write a prompt to generate a visually striking, high-resolution, captivating {genres}piece of art. Choose a SINGLE distinctive art style that fits the themes in the lyrics (eg. surrealism, glitchcore, vaporwave, neo-expressionism, etc.)

Describe what you want to see in the artwork without making references to the song or lyrics. However, feel free to include elements present in the song title or song lyrics, or any that can be associated with the artist. Prioritize emotional tone and aesthetic impact.

Respond with the text for the prompt ONLY.
"""