import flet as ft


def build_title_bar(app):
    app.play_stop_button = ft.IconButton(
        on_click=lambda e: app.toggle_service(),
        padding=0,
        icon_size=34
    )

    return ft.WindowDragArea(
        maximizable=False,
        content=ft.Container(
            bgcolor=ft.Colors.BLACK45,
            padding=10,
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(-1, 0),
                        content=ft.Row(
                            spacing=0,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.SETTINGS,
                                    tooltip="Settings",
                                    on_click=lambda e: app.toggle_settings(),
                                ),
                                app.play_stop_button,
                            ]
                        )
                    ),

                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(
                            "VRC LYRICS",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER
                        )
                    ),

                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.REMOVE,
                                    tooltip="Minimize",
                                    on_click=lambda e: app.minimize_app()
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    tooltip="Close",
                                    on_click=app.close_app
                                )
                            ]
                        )
                    )
                ]
            )
        )
    )
