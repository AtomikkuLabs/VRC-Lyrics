import time
import asyncio
from . import BasePlayback
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager


class WindowsPlayback(BasePlayback):
    def __init__(self):
        super().__init__()
        self._last_fetch_time = None

    def fetch_playback(self):
        return asyncio.run(self._fetch_playback_async())

    async def _fetch_playback_async(self):
        sessions = await MediaManager.request_async()
        current_session = sessions.get_current_session()
        if not current_session:
            return False

        info = await current_session.try_get_media_properties_async()
        playback_info = current_session.get_playback_info()
        timeline = current_session.get_timeline_properties()

        self.name = info.title
        self.artists = [{"name": info.artist}]
        self.duration_ms = timeline.end_time.total_seconds() * 1000
        self.is_playing = playback_info.playback_status == 4

        current_time = time.monotonic()

        if (self.name, self.artists) != (self._last_name, self._last_artists):
            if self.lyrics_provider:
                self.lyrics = self.lyrics_provider.get_lyrics(self)
                self.progress_ms = 800

        elif self.is_playing and self._last_fetch_time is not None:
            self.progress_ms += (current_time - self._last_fetch_time) * 1000
            if self.duration_ms:
                self.progress_ms = min(self.progress_ms, self.duration_ms)

        self._update_current_lyric()

        self._last_fetch_time = current_time
        return True
