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

    def info(self, message):
        logging.info("%s", message)

        snack = ft.SnackBar(
            ft.Text(message, color=ft.Colors.BLACK),
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.Margin(40, 0, 40, 365),
            persist=True,
        )
        self._info_snack = snack
        if self.app.page and self.app.page.loop:
            self.app.page.loop.call_soon_threadsafe(
                lambda: self.app.page.show_dialog(snack)
            )

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
        if self.app.page and self.app.page.loop:
            self.app.page.loop.call_soon_threadsafe(
                lambda: self.app.page.show_dialog(snack)
            )

    def reset(self):
        self.app.content.reset()

    def dismiss(self):
        def update_ui():
            if self._info_snack:
                self._info_snack.open = False
                self._info_snack = None
                self.app.page.update()

        if self.app.page and self.app.page.loop:
            self.app.page.loop.call_soon_threadsafe(update_ui)