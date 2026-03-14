class BasePlayback:
    def __init__(self):
        self.name = None
        self.artists = []
        self.progress_ms = 0
        self.duration_ms = 0
        self.is_playing = None
        self.lyrics = None
        self.current_lyric = None
        self.current_lyric_key = None
        self._last_lyric_key = None
        self._last_name = None
        self._last_artists = None
        self.lyrics_provider = None

    def fetch_playback(self):
        raise NotImplementedError("fetch_playback must be implemented in subclasses")

    def has_changed_track(self):
        result = (self.name, self.artists) != (self._last_name, self._last_artists)
        if result:
            self.current_lyric, self._last_lyric_key, self.current_lyric_key = None, None, None
            self._last_name = self.name
            self._last_artists = self.artists
        return result

    def is_instrumental(self):
        return "instrumental" in self.name.lower()

    def _update_current_lyric(self):
        if self.lyrics:
            self.current_lyric_key = max((k for k in self.lyrics.keys() if k <= self.progress_ms), default=None)
            if self.current_lyric_key is not None and self.current_lyric_key != self._last_lyric_key:
                self.current_lyric = self.lyrics[self.current_lyric_key]
                self._last_lyric_key = self.current_lyric_key
