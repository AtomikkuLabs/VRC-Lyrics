import logging
import flet as ft


class UpdateHandlers:
    def __init__(self, app):
        self.app = app
        self._info_snack = None
        self._info_message = None
        self._error_snack = None

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

    def _home_visible(self):
        container = self.app.content_container
        return bool(container and container.visible)

    def _close_snack(self, attr):
        snack = getattr(self, attr)
        setattr(self, attr, None)
        if snack and snack.open:
            snack.open = False
            snack.update()

    def _close_info_snack(self):
        self._close_snack("_info_snack")

    def _render_info(self):
        """Show the active startup message, but only on the home page."""
        self._close_info_snack()
        if self._info_message is None or not self._home_visible():
            return

        snack = ft.SnackBar(
            ft.Text(self._info_message, color=ft.Colors.BLACK),
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.Margin(40, 0, 40, 365),
            persist=True,
        )
        self._info_snack = snack
        self.app.page.show_dialog(snack)

    def info(self, message):
        logging.info("%s", message)

        def show():
            # Only one startup message at a time: it replaces the previous.
            self._info_message = message
            self._render_info()

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
            self._info_message = None
            self._close_info_snack()
            # Only one error on screen at a time: it replaces the previous.
            self._close_snack("_error_snack")
            self._error_snack = snack
            self.app.page.show_dialog(snack)

        self._run_on_ui(show)

    def reset(self):
        self.app.content.reset()

    def dismiss(self):
        def clear():
            self._info_message = None
            self._close_info_snack()
            self._close_snack("_error_snack")

        self._run_on_ui(clear)

    def page_changed(self):
        """Re-evaluate whether the startup message should be on screen."""
        self._run_on_ui(self._render_info)
