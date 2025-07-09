from lyricsgenius import Genius as LyricsGenius


class Genius:
    def __init__(self, token):
        self.genius = LyricsGenius(token)
        self.genius.verbose = False

    def get_lyrics(self, song, artist) -> str:
        song = self.genius.search_song(song, artist)
        if song:
            return song.lyrics.split('Lyrics', 1)[1].split('You might also like')[0]
        else:
            return None
