import logging
import requests
from lrclib import LrcLibAPI
from .parsing import lrc_to_dictionary


class LRCLibLyrics:
    def __init__(self, handlers):
        self.lyrics_api = LrcLibAPI(user_agent="VRC-Lyrics")
        self.handlers = handlers

    def get_lyrics(self, playback):
        duration = playback.duration_ms / 1000
        words = playback.name.split()

        try:
            for wc in range(len(words), 0, -1):
                title = ' '.join(words[:wc])
                for artist in playback.artists:
                    results = self.lyrics_api.search_lyrics(track_name=title, artist_name=artist['name'])
                    filtered = [r for r in results if r.synced_lyrics and abs(r.duration - duration) <= 3]
                    if filtered:
                        return lrc_to_dictionary(filtered[0].synced_lyrics)
        except requests.exceptions.ConnectionError:
            logging.warning("Connection failed, skipping lyrics fetch")
            self.handlers.error("Connection failed, skipping lyrics fetch")

        return None
