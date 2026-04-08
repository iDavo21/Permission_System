import flet as ft
from datetime import datetime
from core.constants import FECHA_FORMAT, TIPOS_PERMISO
from core.estado_utils import obtener_estado
from core.theme import theme_colors


class FilterPanel(ft.Container):
    def __init__(self, on_apply=None, on_close=None, tipos_permiso=None, dark_mode=True):
        super().__init__()
        self.dark_mode = dark_mode
        tc = theme_colors(self.dark_mode)

        self.bgcolor = tc["bg_dialog"]
        self.border = ft.border.all(1, tc["border_primary"])
        self.border_radius = 14
        self.padding = 16
        self.width = 240
        self.shadow = ft.BoxShadow(blur_radius=20, spread_radius=2, color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK))
        self.animate_opacity = ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT)

        tipos = tipos_permiso or TIPOS_PERMISO

        self.filtro_tipo = ft.Dropdown(
            label="Tipo",
            width=208,
            height=40,
            text_size=12,
            options=[ft.dropdown.Option("Todos")] + [ft.dropdown.Option(t) for t in tipos],
            value="Todos",
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            border_radius=8,
            text_style=ft.TextStyle(color=tc["input_text"]),
            border=ft.InputBorder.OUTLINE,
        )

        self.filtro_estado = ft.Dropdown(
            label="Estado",
            width=208,
            height=40,
            text_size=12,
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Vigente"),
                ft.dropdown.Option("Por Expirar"),
                ft.dropdown.Option("Expirado"),
            ],
            value="Todos",
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            border_radius=8,
            text_style=ft.TextStyle(color=tc["input_text"]),
            border=ft.InputBorder.OUTLINE,
        )

        self.filtro_fecha_desde = ft.TextField(
            label="Desde",
            width=170,
            height=40,
            text_size=12,
            read_only=True,
            hint_text="DD/MM/AAAA",
            hint_style=ft.TextStyle(color=tc["text_hint"]),
            bgcolor=tc["input_bg"],
            color=tc["input_text"],
            border_color=tc["input_border"],
            border_radius=8,
            label_style=ft.TextStyle(color=tc["input_label"]),
            border=ft.InputBorder.OUTLINE,
        )
        self.btn_fecha_desde = ft.IconButton(
            icon=ft.Icons.CALENDAR_TODAY,
            icon_color=tc["text_secondary"],
            icon_size=18,
            tooltip="Desde",
            on_click=self._abrir_calendario_desde,
        )
        self.dp_filtro_desde = ft.DatePicker(
            first_date=datetime(2000, 1, 1),
            last_date=datetime(2050, 12, 31),
            on_change=self._cambio_filtro_desde,
        )

        self.filtro_fecha_hasta = ft.TextField(
            label="Hasta",
            width=170,
            height=40,
            text_size=12,
            read_only=True,
            hint_text="DD/MM/AAAA",
            hint_style=ft.TextStyle(color=tc["text_hint"]),
            bgcolor=tc["input_bg"],
            color=tc["input_text"],
            border_color=tc["input_border"],
            border_radius=8,
            label_style=ft.TextStyle(color=tc["input_label"]),
            border=ft.InputBorder.OUTLINE,
        )
        self.btn_fecha_hasta = ft.IconButton(
            icon=ft.Icons.CALENDAR_TODAY,
            icon_color=tc["text_secondary"],
            icon_size=18,
            tooltip="Hasta",
            on_click=self._abrir_calendario_hasta,
        )
        self.dp_filtro_hasta = ft.DatePicker(
            first_date=datetime(2000, 1, 1),
            last_date=datetime(2050, 12, 31),
            on_change=self._cambio_filtro_hasta,
        )

        self.fecha_filtro_desde = None
        self.fecha_filtro_hasta = None

        btn_aplicar = ft.ElevatedButton(
            "Aplicar",
            icon=ft.Icons.CHECK_CIRCLE,
            icon_color=ft.Colors.WHITE,
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8), padding=ft.padding.symmetric(horizontal=12, vertical=6)),
            on_click=lambda e: on_apply() if on_apply else None,
        )

        btn_limpiar = ft.OutlinedButton(
            "Limpiar",
            icon=ft.Icons.FILTER_ALT_OFF,
            style=ft.ButtonStyle(color=ft.Colors.AMBER_400, shape=ft.RoundedRectangleBorder(radius=8)),
            on_click=lambda e: self.limpiar_filtros(),
        )

        self.on_apply = on_apply
        self.page_ref = None

        self.content = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.FILTER_LIST, color=ft.Colors.GREEN_400, size=18),
                ft.Text("Filtros", size=14, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=tc["text_secondary"],
                    icon_size=18,
                    tooltip="Cerrar",
                    on_click=lambda e: on_close() if on_close else None,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(color=tc["divider"]),
            self.filtro_tipo,
            self.filtro_estado,
            ft.Row([self.filtro_fecha_desde, self.btn_fecha_desde], spacing=4),
            ft.Row([self.filtro_fecha_hasta, self.btn_fecha_hasta], spacing=4),
            ft.Divider(color=tc["divider"]),
            ft.Row([btn_aplicar, btn_limpiar], spacing=8, alignment=ft.MainAxisAlignment.END),
        ], spacing=8)

    def set_page(self, page):
        self.page_ref = page

    def _abrir_calendario_desde(self, e):
        if self.page_ref and self.dp_filtro_desde not in self.page_ref.overlay:
            self.page_ref.overlay.append(self.dp_filtro_desde)
        self.dp_filtro_desde.open = True
        if self.page_ref:
            self.page_ref.update()

    def _cambio_filtro_desde(self, e):
        if self.dp_filtro_desde.value:
            self.fecha_filtro_desde = self.dp_filtro_desde.value.replace(tzinfo=None).date()
            self.filtro_fecha_desde.value = self.fecha_filtro_desde.strftime(FECHA_FORMAT)
            if self.page_ref:
                self.filtro_fecha_desde.update()
            if self.on_apply:
                self.on_apply()

    def _abrir_calendario_hasta(self, e):
        if self.page_ref and self.dp_filtro_hasta not in self.page_ref.overlay:
            self.page_ref.overlay.append(self.dp_filtro_hasta)
        self.dp_filtro_hasta.open = True
        if self.page_ref:
            self.page_ref.update()

    def _cambio_filtro_hasta(self, e):
        if self.dp_filtro_hasta.value:
            self.fecha_filtro_hasta = self.dp_filtro_hasta.value.replace(tzinfo=None).date()
            self.filtro_fecha_hasta.value = self.fecha_filtro_hasta.strftime(FECHA_FORMAT)
            if self.page_ref:
                self.filtro_fecha_hasta.update()
            if self.on_apply:
                self.on_apply()

    def limpiar_filtros(self):
        self.filtro_tipo.value = "Todos"
        self.filtro_estado.value = "Todos"
        self.filtro_fecha_desde.value = ""
        self.filtro_fecha_hasta.value = ""
        self.fecha_filtro_desde = None
        self.fecha_filtro_hasta = None
        if self.on_apply:
            self.on_apply()

    def get_filtros(self):
        return {
            "tipo": self.filtro_tipo.value,
            "estado": self.filtro_estado.value,
            "fecha_desde": self.fecha_filtro_desde,
            "fecha_hasta": self.fecha_filtro_hasta,
        }
