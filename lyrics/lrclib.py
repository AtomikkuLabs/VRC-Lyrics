import time
from lrclib import LrcLibAPI
from .parsing import lrc_to_dictionary


class LRCLibLyrics:
    def __init__(self):
        self.lyrics_api = LrcLibAPI(user_agent="VRC-Lyrics")
        self.max_retries = 2
        self.retry_delay_s = 0.5

    def _search_lyrics(self, title, artist):
        for attempt in range(1, self.max_retries + 1):
            try:
                return self.lyrics_api.search_lyrics(track_name=title, artist_name=artist)
            except:
                if attempt == self.max_retries:
                    return None
                time.sleep(self.retry_delay_s * attempt)

    def get_lyrics(self, playback):
        duration = playback.duration_ms / 1000
        words = playback.name.split()

        for wc in range(len(words), 0, -1):
            title = ' '.join(words[:wc])
            for artist in playback.artists:
                results = self._search_lyrics(title, artist['name'])
                if results is None:
                    return None
                filtered = [r for r in results if r.synced_lyrics and abs(r.duration - duration) <= 3]
                if filtered:
                    return lrc_to_dictionary(filtered[0].synced_lyrics)

        return None
