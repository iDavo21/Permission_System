import flet as ft
from utils.estado_utils import obtener_estado


class SummaryCards(ft.Row):
    def __init__(self, permisos=None):
        super().__init__()
        self.spacing = 20
        self.alignment = ft.MainAxisAlignment.CENTER

        permisos = permisos or []
        total_permisos = len(permisos)
        por_expirar = 0
        expirados = 0

        for p in permisos:
            estado_texto, _ = obtener_estado(p.get("fecha_hasta", ""))
            if estado_texto == "Por Expirar":
                por_expirar += 1
            elif estado_texto == "Expirado":
                expirados += 1

        self.panel_totales = self._crear_card(
            icon=ft.Icons.ASSIGNMENT_OUTLINED,
            icon_color=ft.Colors.GREEN_300,
            value=str(total_permisos),
            label="Permisos Totales",
            bgcolor=ft.Colors.GREEN_800,
            border_color=ft.Colors.GREEN_600,
            anim_delay=500,
        )
        self.panel_por_expirar = self._crear_card(
            icon=ft.Icons.WARNING_AMBER_ROUNDED,
            icon_color=ft.Colors.AMBER_300,
            value=str(por_expirar),
            label="Por Expirar (3 d\u00edas)",
            bgcolor=ft.Colors.AMBER_800,
            border_color=ft.Colors.AMBER_600,
            anim_delay=600,
        )
        self.panel_expirados = self._crear_card(
            icon=ft.Icons.CANCEL_OUTLINED,
            icon_color=ft.Colors.RED_300,
            value=str(expirados),
            label="Expirados",
            bgcolor=ft.Colors.RED_800,
            border_color=ft.Colors.RED_600,
            anim_delay=700,
        )

        self.controls = [self.panel_totales, self.panel_por_expirar, self.panel_expirados]

    def _crear_card(self, icon, icon_color, value, label, bgcolor, border_color, anim_delay):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(icon, size=22, color=icon_color),
                    ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text(label, size=10, color=ft.Colors.GREEN_200 if "GREEN" in str(bgcolor) else ft.Colors.AMBER_200 if "AMBER" in str(bgcolor) else ft.Colors.RED_200),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            bgcolor=bgcolor,
            border_radius=10,
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
            expand=True,
            alignment=ft.Alignment(0, 0),
            border=ft.border.all(1, border_color),
            offset=ft.Offset(0, 0.3),
            animate_offset=ft.Animation(anim_delay, ft.AnimationCurve.EASE_OUT),
            opacity=0,
            animate_opacity=ft.Animation(anim_delay, ft.AnimationCurve.EASE_IN),
        )

    def actualizar(self, permisos):
        total_permisos = len(permisos)
        por_expirar = 0
        expirados = 0

        for p in permisos:
            estado_texto, _ = obtener_estado(p.get("fecha_hasta", ""))
            if estado_texto == "Por Expirar":
                por_expirar += 1
            elif estado_texto == "Expirado":
                expirados += 1

        self.panel_totales.content.controls[1].value = str(total_permisos)
        self.panel_por_expirar.content.controls[1].value = str(por_expirar)
        self.panel_expirados.content.controls[1].value = str(expirados)
