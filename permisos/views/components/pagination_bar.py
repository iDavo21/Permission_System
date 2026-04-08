import flet as ft
from core.theme import theme_colors


class PaginationBar(ft.Container):
    def __init__(self, on_change_page=None, on_change_ppp=None, dark_mode=True):
        super().__init__()
        self.dark_mode = dark_mode
        self.padding = ft.padding.only(top=10, bottom=10)

        self.btn_anterior = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            icon_color=theme_colors(self.dark_mode)["text_secondary"],
            icon_size=20,
            on_click=lambda e: on_change_page(-1) if on_change_page else None,
            tooltip="Pagina anterior",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )
        self.btn_siguiente = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            icon_color=theme_colors(self.dark_mode)["text_secondary"],
            icon_size=20,
            on_click=lambda e: on_change_page(1) if on_change_page else None,
            tooltip="Pagina siguiente",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )
        self.lbl_pagina = ft.Text("", size=13, color=theme_colors(self.dark_mode)["text_secondary"])

        self.dropdown_ppp = ft.Dropdown(
            value="10",
            width=100,
            height=40,
            text_size=12,
            options=[
                ft.dropdown.Option("5"),
                ft.dropdown.Option("10"),
                ft.dropdown.Option("20"),
                ft.dropdown.Option("50"),
            ],
            bgcolor=theme_colors(self.dark_mode)["input_bg"],
            border_color=theme_colors(self.dark_mode)["input_border"],
            text_style=ft.TextStyle(color=theme_colors(self.dark_mode)["input_text"]),
            on_select=lambda e: on_change_ppp() if on_change_ppp else None,
            border=ft.InputBorder.OUTLINE,
            border_radius=8,
        )

        tc = theme_colors(self.dark_mode)
        self.content = ft.Container(
            content=ft.Row([
                ft.Text("Mostrar", size=12, color=tc["text_secondary"]),
                self.dropdown_ppp,
                ft.Text("por pagina", size=12, color=tc["text_secondary"]),
                ft.Container(width=24),
                self.btn_anterior,
                self.lbl_pagina,
                self.btn_siguiente,
            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
            bgcolor=tc["bg_card"],
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=16, vertical=6),
            border=ft.border.all(1, tc["border_primary"]),
        )

    def actualizar(self, pagina_actual, total_paginas, total_registros):
        self.lbl_pagina.value = "Pagina %d de %d" % (pagina_actual, total_paginas)
        self.btn_anterior.disabled = pagina_actual <= 1
        self.btn_siguiente.disabled = pagina_actual >= total_paginas
        self.visible = total_registros > 0

    def get_ppp(self):
        try:
            return int(self.dropdown_ppp.value)
        except (ValueError, TypeError):
            return 10
