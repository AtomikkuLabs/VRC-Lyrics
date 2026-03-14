import logging
import os
import threading
import flet as ft
from flet import Colors
from core import ServiceManager
from gui import build_title_bar, Content, Settings, UpdateHandlers
import config


def _setup_logging():
    from datetime import datetime
    log_path = os.path.join(config.get_base_dir(), "output.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(module)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, mode="w", encoding="utf-8"),
            logging.StreamHandler(),
        ]
    )
    for noisy in ("flet", "flet_core", "urllib3", "spotipy", "asyncio", "pyppeteer", "websockets"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    logging.info("VRC Lyrics started at %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class SpotifyOSCApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.content = None
        self.settings = None
        self.settings_container = None
        self.content_container = None
        self.play_stop_button = None

        self.build_ui()
        self.handlers = UpdateHandlers(self)

        self.service = ServiceManager()
        self.toggle_service()

    def build_ui(self):
        self.page.controls.clear()
        self.settings = Settings(self.page)
        self.settings_container = self.settings.build()
        self.settings_container.visible = False
        self.content = Content(self.page)
        self.content_container = self.content.build()

        layout = ft.Container(
            expand=True,
            border_radius=20,
            bgcolor=Colors.GREY_900,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.2, Colors.BLACK),
                offset=ft.Offset(0, 2)
            ),
            content=ft.Column(spacing=0, controls=[
                build_title_bar(self),
                ft.Container(
                    padding=23,
                    expand=True,
                    content=ft.Stack(expand=True, controls=[self.content_container, self.settings_container])
                )
            ]),
        )

        self.page.add(layout)

    def minimize_app(self):
        self.page.window.minimized = True

    async def close_app(self):
        threading.Thread(target=self.service.stop, daemon=True).start()
        await self.page.window.close()

    def _toggle_service(self):
        if self.service.running and self.service.running.is_set():
            self.play_stop_button.icon = ft.Icons.PLAY_ARROW_ROUNDED
            self.play_stop_button.tooltip = "Start"
            self.service.stop(self.handlers)
        else:
            changed, message = self.settings.save_settings()
            if changed == 2:
                self.handlers.error(message)
                return
            self.play_stop_button.icon = ft.Icons.STOP_ROUNDED
            self.play_stop_button.tooltip = "Stop"
            self.service.start(self.handlers)
        self.page.loop.call_soon_threadsafe(self.page.update, self.play_stop_button)

    def toggle_service(self):
        threading.Thread(target=self._toggle_service, daemon=True).start()

    def toggle_settings(self):
        changed = 0

        if self.settings_container.visible:
            changed, message = self.settings.save_settings()
            if changed == 2:
                self.handlers.error(message)
                return

        self.settings_container.visible = not self.settings_container.visible
        self.settings_container.update()
        self.content_container.visible = not self.content_container.visible
        self.content_container.update()

        if changed == 1:
            was_running = self.service.running and self.service.running.is_set()
            if was_running:
                threading.Thread(target=lambda: (self._toggle_service(), self._toggle_service()), daemon=True).start()
            else:
                threading.Thread(target=self._toggle_service, daemon=True).start()


async def main(page: ft.Page):
    _setup_logging()

    page.title = "VRC Lyrics"
    _white = ft.TextStyle(color=ft.Colors.WHITE)
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.WHITE,
            surface=ft.Colors.WHITE,
            on_surface=ft.Colors.WHITE,
        ),
        text_theme=ft.TextTheme(
            body_large=_white,
            body_medium=_white,
            body_small=_white,
            title_large=_white,
            title_medium=_white,
            title_small=_white,
            headline_large=_white,
            headline_medium=_white,
            headline_small=_white,
            label_large=_white,
            label_medium=_white,
            label_small=_white,
        ),
        icon_button_theme=ft.IconButtonTheme(
            style=ft.ButtonStyle(
                overlay_color=ft.Colors.TRANSPARENT,
                icon_color={
                    ft.ControlState.DEFAULT: ft.Colors.WHITE70,
                    ft.ControlState.HOVERED: ft.Colors.WHITE,
                },
            )
        )
    )
    SpotifyOSCApp(page)
    page.window.maximizable = False
    page.window.frameless = True
    page.window.width = 450
    page.window.height = 500
    page.window.bgcolor = Colors.TRANSPARENT
    page.bgcolor = Colors.TRANSPARENT
    page.update()

    await page.window.center()
    page.window.visible = True
    page.update()

ft.run(main, view=ft.AppView.FLET_APP_HIDDEN)
