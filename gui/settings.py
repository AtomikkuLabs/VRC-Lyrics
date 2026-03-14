import os
import config
import flet as ft
from flet import Colors

CONTAINER_WIDTH = 315


class Settings:
    def __init__(self, page):
        self.page = page
        self.ip_field = None
        self.port_field = None
        self.chatbox_format_field = None
        self.chatbox_format_container = None
        self.playback_provider_dropdown = None
        self.lyric_provider_dropdown = None
        self.lyric_fields_container = None
        self.playback_fields_container = None
        self.client_id_field = None
        self.sp_dc_field = None

    def build(self):
        page = self.page
        form_color = Colors.GREY_800

        # ───── Common OSC Fields ─────
        self.ip_field = ft.TextField(
            label="IP",
            value=config.get('ip', '127.0.0.1'),
            width=CONTAINER_WIDTH / 2 - 5,
            bgcolor=form_color,
            input_filter=ft.InputFilter(
                regex_string=r"^((25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$"
            ),
        )

        self.port_field = ft.TextField(
            label="Port",
            value=config.get('port', 9000),
            width=CONTAINER_WIDTH / 2 - 5,
            bgcolor=form_color,
            input_filter=ft.InputFilter(
                regex_string=r"^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"
            ),
        )

        self.chatbox_format_field = ft.TextField(
            label="Chatbox Output Format",
            value=config.get("chatbox_format", "{name} - {artist}\n{lyrics}"),
            bgcolor=form_color,
            multiline=True,
            min_lines=1,
            max_lines=9,
            width=CONTAINER_WIDTH,
        )

        # ───── Provider Dropdowns ─────
        self.playback_provider_dropdown = ft.Dropdown(
            label="Playback Provider",
            value=config.get('playback_provider'),
            options=[ft.dropdown.Option("Windows"), ft.dropdown.Option("Spotify")],
            width=CONTAINER_WIDTH,
            bgcolor=form_color,
            filled=True,
            fill_color=form_color,
        )
        self.lyric_provider_dropdown = ft.Dropdown(
            label="Lyric Provider",
            value=config.get('lyric_provider'),
            width=CONTAINER_WIDTH,
            bgcolor=form_color,
            filled=True,
            fill_color=form_color,
        )
        clear_icon = ft.Container(
            margin=ft.Margin(left=245, top=4, bottom=0, right=0),
            content=ft.IconButton(
                icon=ft.Icons.CLOSE,
                icon_size=12,
                style=ft.ButtonStyle(
                    icon_color={
                        ft.ControlState.DEFAULT: ft.Colors.WHITE70,
                        ft.ControlState.HOVERED: ft.Colors.WHITE,
                    },
                    overlay_color="transparent",
                ),
                on_click=lambda e: clear_lyric_provider(),
            )
        )

        lyric_provider_stack = ft.Stack(controls=[self.lyric_provider_dropdown, clear_icon])

        # ───── Shared Fields ─────
        self.client_id_field = ft.TextField(
            label="Client ID",
            value=config.get('client_id', ''),
            width=CONTAINER_WIDTH,
            bgcolor=form_color,
        )

        self.sp_dc_field = ft.TextField(
            label="SP_DC",
            value=config.get('sp_dc', ''),
            width=CONTAINER_WIDTH,
            bgcolor=form_color,
        )

        # Containers
        self.chatbox_format_container = ft.Container(content=None)
        self.playback_fields_container = ft.Container(content=ft.Column(spacing=10), width=CONTAINER_WIDTH)
        self.lyric_fields_container = ft.Container(content=ft.Column(spacing=10), width=CONTAINER_WIDTH)

        def apply_chatbox_field():
            port = int(self.port_field.value)
            self.chatbox_format_container.content = self.chatbox_format_field if port == 9000 else None

        def apply_playback_fields():
            pb = self.playback_provider_dropdown.value
            match pb:
                case "Spotify":
                    self.playback_fields_container.visible = True
                    self.playback_fields_container.content = ft.Column(controls=[self.client_id_field])
                    self.lyric_provider_dropdown.options = [ft.dropdown.Option("LRCLib"), ft.dropdown.Option("Spotify")]
                case "Windows":
                    self.playback_fields_container.visible = False
                    self.lyric_provider_dropdown.options = [ft.dropdown.Option("LRCLib")]
                    if self.lyric_provider_dropdown.value == "Spotify":
                        clear_lyric_provider()

        def apply_lyric_fields():
            lp = self.lyric_provider_dropdown.value
            match lp:
                case "Spotify":
                    self.lyric_fields_container.content = ft.Column(controls=[ft.Container(content=self.sp_dc_field)])
                    self.lyric_fields_container.visible = True
                    clear_icon.visible = True
                case "LRCLib":
                    self.lyric_fields_container.visible = False
                    clear_icon.visible = True
                case _:
                    self.lyric_fields_container.visible = False
                    clear_icon.visible = False

        def clear_lyric_provider():
            self.lyric_provider_dropdown = ft.Dropdown(
                label="Lyric Provider",
                width=CONTAINER_WIDTH,
                bgcolor=form_color,
                value="",
                filled=True,
                fill_color=form_color,
            )
            self.lyric_provider_dropdown.on_select = lambda e: (apply_lyric_fields(), page.update(self.lyric_fields_container, clear_icon))
            lyric_provider_stack.controls = [self.lyric_provider_dropdown, clear_icon]
            apply_playback_fields()
            apply_lyric_fields()
            page.update(self.playback_fields_container, self.lyric_provider_dropdown, self.lyric_fields_container, clear_icon, lyric_provider_stack)

        self.playback_provider_dropdown.on_select = lambda e: (
            apply_playback_fields(),
            apply_lyric_fields(),
            page.update(self.playback_fields_container, self.lyric_provider_dropdown, self.lyric_fields_container, clear_icon),
        )
        self.lyric_provider_dropdown.on_select = lambda e: (apply_lyric_fields(), page.update(self.lyric_fields_container, clear_icon))
        self.port_field.on_change = lambda e: (apply_chatbox_field(), self.chatbox_format_container.update())

        # Set initial state (no updates needed — initial render handles it)
        apply_playback_fields()
        apply_lyric_fields()
        apply_chatbox_field()

        return ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.ALWAYS,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                controls=[
                    ft.Text(value="OSC Settings", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[self.ip_field, self.port_field]),
                    self.chatbox_format_container,
                    ft.Text(value="Playback Provider", size=16, weight=ft.FontWeight.BOLD),
                    self.playback_provider_dropdown,
                    self.playback_fields_container,
                    ft.Text(value="Lyric Provider", size=16, weight=ft.FontWeight.BOLD),
                    lyric_provider_stack,
                    self.lyric_fields_container,
                    ft.Text(value="", size=16, weight=ft.FontWeight.BOLD),
                ],
            ),
        )

    def save_settings(self):
        settings = {
            'ip': self.ip_field.value,
            'port': int(self.port_field.value),
            'playback_provider': self.playback_provider_dropdown.value,
            'lyric_provider': self.lyric_provider_dropdown.value,
            'chatbox_format': self.chatbox_format_field.value.strip()
        }

        if config.get('chatbox_format') != settings['chatbox_format']:
            lines = settings['chatbox_format'].splitlines()
            if len(lines) > 9:
                return 2, "Chatbox must be 9 lines or fewer."

        if settings['playback_provider'] == "Spotify":
            new_client_id = self.client_id_field.value.strip()
            if config.get('client_id') != new_client_id:
                cache_path = os.path.join(config.get_base_dir(), ".cache")
                if os.path.exists(cache_path):
                    os.remove(cache_path)
            settings['client_id'] = new_client_id

        if settings['lyric_provider'] == "Spotify":
            settings['sp_dc'] = self.sp_dc_field.value.strip()

        changed = 0
        for key, value in settings.items():
            if config.get(key) != value:
                config.set_config(key, value)
                changed = 1

        return changed, ""
