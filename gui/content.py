import flet as ft
from flet import Colors, Icons


class Content:
    def __init__(self, page):
        self.page = page
        self.lyrics_text = None
        self.current_time = None
        self.total_time = None
        self.progress_bar = None
        self.artist = None
        self.song_title = None
        self.album_art = None
        self.album_art_icon = None
        self.album_art_container = None

    def _update(self, *controls):
        try:
            self.page.loop.call_soon_threadsafe(self.page.update, *controls)
        except RuntimeError:
            pass

    def build(self):
        self.song_title = ft.Text(
            "Song Title",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        self.artist = ft.Text(
            "Artist Name",
            size=18,
            color=Colors.GREY_300,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
            text_align=ft.TextAlign.CENTER
        )

        track_info = ft.Container(
            content=ft.Column(
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.song_title,
                    self.artist,
                ]
            ),
        )

        self.progress_bar = ft.ProgressBar(
            width=350,
            value=0.0,
            bgcolor=Colors.GREY_800
        )
        self.current_time = ft.Text("0:00", size=12, color=Colors.GREY_300)
        self.total_time = ft.Text("0:00", size=12, color=Colors.GREY_300)

        time_info = ft.Row(
            [
                self.current_time,
                self.total_time
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            width=350
        )

        time_container = ft.Container(
            content=ft.Column(
                spacing=5,
                controls=[
                    self.progress_bar,
                    time_info,
                ]
            ),
        )

        self.lyrics_text = ft.Text(
            "Lyrics will appear here...",
            size=15,
            text_align=ft.TextAlign.CENTER,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
            weight=ft.FontWeight.BOLD
        )

        lyrics_container = ft.Container(
            content=self.lyrics_text,
            height=50,
            border_radius=10,
            bgcolor=Colors.GREY_800,
            padding=10,
            alignment=ft.Alignment(0, 0)
        )

        return ft.Container(
            expand=True,
            content=ft.Column(
                controls=[
                    self.build_album_art(),
                    track_info,
                    time_container,
                    lyrics_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
        )

    def build_album_art(self):
        self.album_art_icon = ft.Container(
            border_radius=10,
            bgcolor=Colors.GREY_800,
            alignment=ft.Alignment(0, 0),
            content=ft.Icon(Icons.MUSIC_NOTE, size=60, color=Colors.GREY_500),
            visible=True
        )

        self.album_art = ft.Image(
            src="",
            width=165,
            height=165,
            fit=ft.BoxFit.COVER,
            border_radius=10,
            visible=False
        )

        self.album_art_container = ft.Stack(
            controls=[self.album_art_icon, self.album_art],
            width=165,
            height=165
        )

        return self.album_art_container

    def update_track_info(self, title, artist, album_art=None):
        self.song_title.value = title
        self.artist.value = artist

        if album_art:
            self.album_art.src = album_art
            self.album_art.visible = True
            self.album_art_icon.visible = False
        else:
            self.album_art.visible = False
            self.album_art_icon.visible = True

        self._update(self.song_title, self.artist, self.album_art, self.album_art_icon)

    def update_progress(self, progress, duration):
        if progress is not None and duration:
            progress_seconds = progress / 1000.0
            duration_seconds = duration / 1000.0

            if duration_seconds > 0:
                self.progress_bar.value = progress_seconds / duration_seconds
                self.current_time.value = format_time(progress_seconds)
                self.total_time.value = format_time(duration_seconds)

            self._update(self.progress_bar, self.current_time, self.total_time)

    def update_lyric(self, lyric):
        self.lyrics_text.value = lyric or ""
        self._update(self.lyrics_text)

    def reset(self):
        self.update_track_info(title="Song Title", artist="Artist Name", album_art=None)
        self.update_lyric("Lyrics will appear here...")
        self.update_progress(progress=0, duration=1)


def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"
