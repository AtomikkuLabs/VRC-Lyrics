import queue
import logging
import config
from pythonosc.udp_client import SimpleUDPClient
from .messages import LyricUpdate, SongUpdate, IsPlayingUpdate


class BaseOSCManager:
    def __init__(self, ip, port, song_data_queue, running, osc_path):
        self.client = SimpleUDPClient(ip, port)
        self.song_data_queue = song_data_queue
        self.running = running
        self.track = None
        self.last_lyric = None
        self.osc_path = osc_path
        self.is_playing = None
        self.song_display = config.get("chatbox_format")

    def send_osc_message(self, lyric=None):
        if lyric is not None:
            self.client.send_message(self.osc_path, [lyric, True, False])

        else:
            if self.is_playing:
                self.client.send_message(self.osc_path, [self.last_lyric, True, False])
            else:
                self.client.send_message(self.osc_path, ["", True, False])

    def handle_song_update(self, playback):
        self.last_lyric = None
        self.track = playback
        self.is_playing = playback.is_playing
        lyric = playback.current_lyric
        self.last_lyric = lyric
        self.send_osc_message(lyric=lyric)

    def handle_lyric_update(self, lyric):
        if lyric == "♪":
            self.send_osc_message(lyric="")
            self.last_lyric = ""
            return

        self.send_osc_message(lyric=lyric)
        self.last_lyric = lyric

    def process_queue_messages(self):
        while not self.song_data_queue.empty():
            message = self.song_data_queue.get_nowait()

            if isinstance(message, SongUpdate):
                self.handle_song_update(message.playback)
            elif isinstance(message, IsPlayingUpdate):
                self.is_playing = message.is_playing
                self.send_osc_message()
            elif isinstance(message, LyricUpdate):
                self.handle_lyric_update(message.lyric)

    def run(self):
        while self.running.is_set():
            try:
                msg = self.song_data_queue.get(timeout=10)
            except queue.Empty:
                self._safe(self.send_osc_message)
            else:
                if msg is None:
                    break

                self.song_data_queue.put(msg)
                self._safe(self.process_queue_messages)

        self._safe(lambda: self.client.send_message(self.osc_path, ["", True, False]))

    def _safe(self, fn):
        """Runs fn, logging and swallowing errors instead of letting them kill this thread.

        OSC sends can fail transiently (e.g. VRChat not listening yet during a
        world load, or a dropped connection) - without this, an unhandled
        OSError here silently kills the OSC thread for the rest of the
        session, since nothing else supervises or restarts it.
        """
        try:
            fn()
        except OSError as e:
            logging.warning("OSC send failed, will retry: %s", e)
        except Exception:
            # Same reasoning, one level out: _safe also wraps
            # process_queue_messages, which parses messages and can fail in ways
            # that aren't OSError. Nothing supervises this thread either, so a
            # single bad message must not end OSC output for the session.
            logging.exception("OSC worker error, continuing")


class ChatboxManager(BaseOSCManager):
    OSC_CHATBOX_PATH = "/chatbox/input"
    PLAY_EMOJI = "\U000025B6"
    PAUSE_EMOJI = "\U000023F8"
    MIC_EMOJI = "\U0001F3A4"

    def __init__(self, ip, port, song_data_queue, running):
        super().__init__(ip, port, song_data_queue, running, self.OSC_CHATBOX_PATH)
        self.is_playing = None

    def send_osc_message(self, lyric=None):
        if not self.track:
            return

        status = self.PLAY_EMOJI if self.is_playing else self.PAUSE_EMOJI
        name = self.track.name
        artist = self.track.artists[0]["name"]
        mic = ""
        lyrics = ""

        if self.is_playing:
            if lyric:
                mic = self.MIC_EMOJI
                lyrics = lyric
            elif lyric is None and self.last_lyric:
                mic = self.MIC_EMOJI
                lyrics = self.last_lyric

        try:
            message = self.song_display.format(status=status, name=name, artist=artist, mic=mic, lyrics=lyrics).strip()
        except KeyError:
            message = f"{status} {name} - {artist}\n{mic} {lyrics}".strip()

        self.client.send_message(self.osc_path, [message, True, False])


class ParamManager(BaseOSCManager):
    OSC_LYRICS_PATH = "/Atomikku/VRCSpotifyOSC/Lyrics"

    def __init__(self, ip, port, song_data_queue, running):
        super().__init__(ip, port, song_data_queue, running, self.OSC_LYRICS_PATH)
