import time
import logging
import requests
import config
from lyrics import LRCLibLyrics, SpotifyLyrics, SpotifyAuthError
from playback import SpotifyPlayback, WindowsPlayback
from .messages import LyricUpdate, SongUpdate, IsPlayingUpdate


def _validate_spotify_client_id(client_id):
    """Returns True if valid, False if invalid_client."""
    try:
        resp = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "client_id": client_id,
                "grant_type": "authorization_code",
                "code": "invalid_code",
                "redirect_uri": "http://127.0.0.1:5000/callback",
                "code_verifier": "x",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        if resp.status_code == 400 and resp.json().get("error") == "invalid_client":
            return False
    except Exception:
        pass
    return True


def poll_playback(playback, song_data_queue, running, handlers):
    previous_position = 0
    previous_key = None
    connected = False

    handlers.info("Connected, waiting for data...")

    while running.is_set():
        previous_is_playing = playback.is_playing
        result = playback.fetch_playback()

        if result is None:
            handlers.error("Spotify auth expired - please restart and log in again")
            running.clear()
            return

        if result is False:
            time.sleep(1)
            continue

        if not connected:
            connected = True
            logging.info("Connected to playback provider")
            handlers.dismiss()

        handlers.progress(progress=playback.progress_ms, duration=playback.duration_ms)

        if playback.has_changed_track():
            handle_track_change(playback, song_data_queue, handlers)
            previous_position = playback.progress_ms
            previous_key = playback.current_lyric_key

        else:
            if playback.is_playing != previous_is_playing:
                song_data_queue.put(IsPlayingUpdate(is_playing=playback.is_playing))

            if playback.lyrics:
                previous_key = update_lyrics(playback, previous_position, previous_key, song_data_queue, handlers)
                previous_position = playback.progress_ms

        time.sleep(1)


def handle_track_change(playback, song_data_queue, handlers):
    handlers.track_info(title=playback.name,
                        artist=", ".join(artist['name'] for artist in playback.artists),
                        album_art=getattr(playback, "album_cover", None))
    handlers.lyric(lyric=playback.current_lyric)
    song_data_queue.put(SongUpdate(playback=playback))

    if not playback.lyrics_provider:
        handlers.lyric(lyric="No lyric provider selected in settings")
        return

    if playback.is_instrumental() or not playback.lyrics:
        handlers.lyric(lyric="Lyrics for this track are not available")


def update_lyrics(playback, previous_position, previous_key, song_data_queue, handlers):
    current_key = playback.current_lyric_key

    if playback.progress_ms < previous_position - 1000 and current_key is None:
        song_data_queue.put(LyricUpdate(lyric=""))
        handlers.lyric(lyric="")
        return None

    if current_key is not None and current_key != previous_key:
        lyric = playback.lyrics[current_key]
        if lyric is not None:
            handlers.lyric(lyric=lyric)
            song_data_queue.put(LyricUpdate(lyric=lyric))
        return current_key

    return previous_key


def lrc(song_data_queue, running, handlers):
    playback, lyrics = None, None
    playback_provider = config.get('playback_provider')
    lyric_provider = config.get('lyric_provider')

    match playback_provider:
        case "Spotify":
            import os
            client_id = config.get('client_id')
            if not _validate_spotify_client_id(client_id):
                logging.error("Invalid Spotify client_id: %s", client_id)
                handlers.error("Invalid Spotify Client ID")
                return
            cache_path = os.path.join(config.get_base_dir(), ".cache")
            if not os.path.exists(cache_path):
                logging.info("No Spotify auth cache found, browser login required")
                handlers.info("Please log in to Spotify in the browser")
            playback = SpotifyPlayback(client_id=client_id)

        case "Windows":
            playback = WindowsPlayback()

    match lyric_provider:
        case "Spotify":
            try:
                sp_dc = config.get('sp_dc')
                playback.lyrics_provider = SpotifyLyrics(sp_dc=sp_dc, handlers=handlers)
            except SpotifyAuthError:
                handlers.error("Invalid sp_dc cookie")

        case "LRCLib":
            playback.lyrics_provider = LRCLibLyrics(handlers=handlers)

    if playback:
        poll_playback(playback, song_data_queue, running, handlers)
