import flet as ft
from datetime import datetime
from utils.constants import FECHA_FORMAT, TIPOS_PERMISO
from utils.estado_utils import obtener_estado


class FilterPanel(ft.Container):
    def __init__(self, on_apply=None, on_close=None, tipos_permiso=None):
        super().__init__()
        self.bgcolor = ft.Colors.GREEN_800
        self.border = ft.border.all(1, ft.Colors.GREEN_600)
        self.border_radius = 10
        self.padding = 12
        self.width = 220
        self.shadow = ft.BoxShadow(blur_radius=15, spread_radius=2, color=ft.Colors.BLACK54)
        self.animate_opacity = ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT)

        tipos = tipos_permiso or TIPOS_PERMISO

        self.filtro_tipo = ft.Dropdown(
            label="Tipo",
            width=196,
            height=35,
            text_size=11,
            options=[ft.dropdown.Option("Todos")] + [ft.dropdown.Option(t) for t in tipos],
            value="Todos",
            bgcolor=ft.Colors.WHITE24,
            border_color=ft.Colors.TRANSPARENT,
            border_radius=8,
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
        )

        self.filtro_estado = ft.Dropdown(
            label="Estado",
            width=196,
            height=35,
            text_size=11,
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Vigente"),
                ft.dropdown.Option("Por Expirar"),
                ft.dropdown.Option("Expirado"),
            ],
            value="Todos",
            bgcolor=ft.Colors.WHITE24,
            border_color=ft.Colors.TRANSPARENT,
            border_radius=8,
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
        )

        self.filtro_fecha_desde = ft.TextField(
            label="Desde",
            width=165,
            height=35,
            text_size=11,
            read_only=True,
            hint_text="DD/MM/AAAA",
            hint_style=ft.TextStyle(color=ft.Colors.WHITE54),
            bgcolor=ft.Colors.WHITE24,
            color=ft.Colors.WHITE,
            border_color=ft.Colors.TRANSPARENT,
            border_radius=8,
            label_style=ft.TextStyle(color=ft.Colors.WHITE70),
        )
        self.btn_fecha_desde = ft.IconButton(
            icon=ft.Icons.CALENDAR_TODAY,
            icon_color=ft.Colors.WHITE,
            icon_size=16,
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
            width=165,
            height=35,
            text_size=11,
            read_only=True,
            hint_text="DD/MM/AAAA",
            hint_style=ft.TextStyle(color=ft.Colors.WHITE54),
            bgcolor=ft.Colors.WHITE24,
            color=ft.Colors.WHITE,
            border_color=ft.Colors.TRANSPARENT,
            border_radius=8,
            label_style=ft.TextStyle(color=ft.Colors.WHITE70),
        )
        self.btn_fecha_hasta = ft.IconButton(
            icon=ft.Icons.CALENDAR_TODAY,
            icon_color=ft.Colors.WHITE,
            icon_size=16,
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

        btn_aplicar = ft.IconButton(
            icon=ft.Icons.CHECK_CIRCLE,
            icon_color=ft.Colors.GREEN_300,
            icon_size=20,
            tooltip="Aplicar filtros",
            on_click=lambda e: on_apply() if on_apply else None,
        )

        btn_limpiar = ft.IconButton(
            icon=ft.Icons.FILTER_ALT_OFF,
            icon_color=ft.Colors.AMBER_300,
            icon_size=20,
            tooltip="Limpiar filtros",
            on_click=lambda e: self.limpiar_filtros(),
        )

        self.on_apply = on_apply
        self.page_ref = None

        self.content = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.FILTER_LIST, color=ft.Colors.GREEN_300, size=16),
                ft.Text("Filtros", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_300),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=ft.Colors.WHITE70,
                    icon_size=16,
                    tooltip="Cerrar",
                    on_click=lambda e: on_close() if on_close else None,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.filtro_tipo,
            self.filtro_estado,
            ft.Row([self.filtro_fecha_desde, self.btn_fecha_desde], spacing=0),
            ft.Row([self.filtro_fecha_hasta, self.btn_fecha_hasta], spacing=0),
            ft.Row([btn_aplicar, btn_limpiar], spacing=5, alignment=ft.MainAxisAlignment.END),
        ], spacing=6)

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
