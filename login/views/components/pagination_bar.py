import flet as ft


class PaginationBar(ft.Container):
    def __init__(self, on_change_page=None, on_change_ppp=None):
        super().__init__()
        self.padding = ft.padding.only(top=8, bottom=8)

        self.btn_anterior = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            icon_color=ft.Colors.WHITE,
            icon_size=20,
            on_click=lambda e: on_change_page(-1) if on_change_page else None,
            tooltip="Página anterior",
        )
        self.btn_siguiente = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            icon_color=ft.Colors.WHITE,
            icon_size=20,
            on_click=lambda e: on_change_page(1) if on_change_page else None,
            tooltip="Página siguiente",
        )
        self.lbl_pagina = ft.Text("", size=13, color=ft.Colors.WHITE)

        self.dropdown_ppp = ft.Dropdown(
            value="10",
            width=90,
            height=35,
            text_size=12,
            options=[
                ft.dropdown.Option("5"),
                ft.dropdown.Option("10"),
                ft.dropdown.Option("20"),
                ft.dropdown.Option("50"),
            ],
            bgcolor=ft.Colors.GREEN_700,
            border_color=ft.Colors.GREEN_600,
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
            on_select=lambda e: on_change_ppp() if on_change_ppp else None,
        )

        self.content = ft.Row([
            ft.Text("Mostrar", size=12, color=ft.Colors.WHITE70),
            self.dropdown_ppp,
            ft.Text("por página", size=12, color=ft.Colors.WHITE70),
            ft.Container(width=20),
            self.btn_anterior,
            self.lbl_pagina,
            self.btn_siguiente,
        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)

    def actualizar(self, pagina_actual, total_paginas, total_registros):
        self.lbl_pagina.value = f"P\u00e1gina {pagina_actual} de {total_paginas}"
        self.btn_anterior.disabled = pagina_actual <= 1
        self.btn_siguiente.disabled = pagina_actual >= total_paginas
        self.visible = total_registros > 0

    def get_ppp(self):
        try:
            return int(self.dropdown_ppp.value)
        except (ValueError, TypeError):
            return 10
