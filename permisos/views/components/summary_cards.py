import flet as ft
from core.estado_utils import obtener_estado
from core.theme import theme_colors


class SummaryCards(ft.Row):
    def __init__(self, permisos=None, dark_mode=True):
        super().__init__()
        self.spacing = 16
        self.alignment = ft.MainAxisAlignment.CENTER
        self.dark_mode = dark_mode
        tc = theme_colors(self.dark_mode)

        permisos = permisos or []
        total_permisos = len(permisos)
        vigentes = 0
        por_expirar = 0
        expirados = 0

        for p in permisos:
            estado_texto, _ = obtener_estado(p.get("fecha_hasta", ""))
            if estado_texto == "Vigente":
                vigentes += 1
            elif estado_texto == "Por Expirar":
                por_expirar += 1
            elif estado_texto == "Expirado":
                expirados += 1

        self.panel_vigentes = self._crear_card(
            icon=ft.Icons.CHECK_CIRCLE,
            icon_color=ft.Colors.GREEN_400,
            value=str(vigentes),
            label="Permisos Vigentes",
            anim_delay=400,
        )
        self.panel_totales = self._crear_card(
            icon=ft.Icons.ASSIGNMENT_OUTLINED,
            icon_color=ft.Colors.CYAN_400,
            value=str(total_permisos),
            label="Permisos Totales",
            anim_delay=500,
        )
        self.panel_por_expirar = self._crear_card(
            icon=ft.Icons.WARNING_AMBER_ROUNDED,
            icon_color=ft.Colors.AMBER_400,
            value=str(por_expirar),
            label="Por Expirar (3 dias)",
            anim_delay=600,
        )
        self.panel_expirados = self._crear_card(
            icon=ft.Icons.CANCEL_OUTLINED,
            icon_color=ft.Colors.RED_400,
            value=str(expirados),
            label="Expirados",
            anim_delay=700,
        )

        self.controls = [self.panel_vigentes, self.panel_totales, self.panel_por_expirar, self.panel_expirados]

    def _crear_card(self, icon, icon_color, value, label, anim_delay):
        tc = theme_colors(self.dark_mode)
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Icon(icon, size=20, color=icon_color),
                        ft.Container(expand=True),
                    ]),
                    ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                    ft.Text(label, size=11, color=tc["text_secondary"]),
                ],
                spacing=4,
            ),
            bgcolor=tc["stat_bg"],
            border_radius=14,
            padding=ft.padding.symmetric(vertical=16, horizontal=20),
            expand=True,
            border=ft.border.all(1, tc["stat_border"]),
            offset=ft.Offset(0, 0.3),
            animate_offset=ft.Animation(anim_delay, ft.AnimationCurve.EASE_OUT),
            opacity=0,
            animate_opacity=ft.Animation(anim_delay, ft.AnimationCurve.EASE_IN),
        )

    def actualizar(self, permisos):
        total_permisos = len(permisos)
        vigentes = 0
        por_expirar = 0
        expirados = 0

        for p in permisos:
            estado_texto, _ = obtener_estado(p.get("fecha_hasta", ""))
            if estado_texto == "Vigente":
                vigentes += 1
            elif estado_texto == "Por Expirar":
                por_expirar += 1
            elif estado_texto == "Expirado":
                expirados += 1

        self.panel_vigentes.content.controls[1].value = str(vigentes)
        self.panel_totales.content.controls[1].value = str(total_permisos)
        self.panel_por_expirar.content.controls[1].value = str(por_expirar)
        self.panel_expirados.content.controls[1].value = str(expirados)
