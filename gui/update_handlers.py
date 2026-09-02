import logging
import flet as ft


class UpdateHandlers:
    def __init__(self, app):
        self.app = app
        self._info_snack = None

    def track_info(self, title, artist, album_art=None):
        self.app.content.update_track_info(title, artist, album_art)

    def progress(self, progress, duration):
        self.app.content.update_progress(progress, duration)

    def lyric(self, lyric):
        self.app.content.update_lyric(lyric)

    def _run_on_ui(self, fn):
        page = self.app.page
        if page and page.loop:
            page.loop.call_soon_threadsafe(fn)

    def _close_info(self):
        """Close the current startup/info snackbar, if any. Runs on the UI loop."""
        snack = self._info_snack
        self._info_snack = None
        if snack and snack.open:
            snack.open = False
            snack.update()

    def info(self, message):
        logging.info("%s", message)

        snack = ft.SnackBar(
            ft.Text(message, color=ft.Colors.BLACK),
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.Margin(40, 0, 40, 365),
            persist=True,
        )

        def show():
            # Only one startup message on screen at a time: replace the previous.
            self._close_info()
            self._info_snack = snack
            self.app.page.show_dialog(snack)

        self._run_on_ui(show)

    def error(self, message):
        logging.error("%s", message)

        snack = ft.SnackBar(
            ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.Margin(40, 0, 40, 365),
            persist=True,
            show_close_icon=True,
            close_icon_color=ft.Colors.WHITE,
        )

        def show():
            # An error ends the startup sequence; clear its info message.
            self._close_info()
            self.app.page.show_dialog(snack)

        self._run_on_ui(show)

    def reset(self):
        self.app.content.reset()

    def dismiss(self):
        self._run_on_ui(self._close_info)
