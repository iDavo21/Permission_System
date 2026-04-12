import flet as ft
import asyncio
from datetime import datetime
from core.theme import theme_colors
from core.estado_utils import obtener_estado


class DashboardView(ft.Container):
    def __init__(self, personal_ctrl, permisos_ctrl, comisiones_ctrl, on_navigate_permisos=None, on_navigate_comisiones=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.personal_ctrl = personal_ctrl
        self.permisos_ctrl = permisos_ctrl
        self.comisiones_ctrl = comisiones_ctrl
        self.on_navigate_permisos = on_navigate_permisos
        self.on_navigate_comisiones = on_navigate_comisiones
        self.dark_mode = dark_mode

        self._build_ui()

    def _build_ui(self):
        tc = theme_colors(self.dark_mode)

        self.stat_permiso_vigente = self._stat_card(ft.Icons.CHECK_CIRCLE, "0", "Permisos Vigentes", ft.Colors.GREEN_400, "haz clic para ver")
        self.stat_permiso_expirar = self._stat_card(ft.Icons.WARNING, "0", "Por Expirar", ft.Colors.AMBER_400, "próximos 3 días")
        self.stat_permiso_expirado = self._stat_card(ft.Icons.CANCEL, "0", "Expirados", ft.Colors.RED_400, "vencidos")

        self.stat_personal_disponible = self._stat_card(ft.Icons.PERSON, "0", "Personal Disponible", ft.Colors.GREEN_400, "sin permisos ni comisiones")
        self.stat_personal_permiso = self._stat_card(ft.Icons.EVENT_NOTE, "0", "De Permiso", ft.Colors.ORANGE_400, "en permiso activo")
        self.stat_personal_comision = self._stat_card(ft.Icons.BUSINESS_CENTER, "0", "En Comisión", ft.Colors.CYAN_400, "en comisión activa")

        self._stat_personal_container = ft.Container(
            content=ft.Column([
                ft.Text("Estado del Personal", size=18, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Container(height=16),
                ft.Row([
                    self.stat_personal_disponible,
                    self.stat_personal_permiso,
                    self.stat_personal_comision,
                ], spacing=16),
            ], tight=True),
            padding=24,
            bgcolor=tc["bg_card"],
            border_radius=16,
            border=ft.border.all(1, tc["border_primary"]),
        )

        self._stat_permisos_container = ft.Container(
            content=ft.Column([
                ft.Text("Resumen de Permisos", size=18, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Container(height=16),
                ft.Row([
                    self.stat_permiso_vigente,
                    self.stat_permiso_expirar,
                    self.stat_permiso_expirado,
                ], spacing=16),
            ], tight=True),
            padding=24,
            bgcolor=tc["bg_card"],
            border_radius=16,
            border=ft.border.all(1, tc["border_primary"]),
        )

        self.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.DASHBOARD, color=ft.Colors.GREEN_400, size=28),
                                bgcolor=tc["icon_bg"],
                                border_radius=10,
                                padding=10,
                            ),
                            ft.Column([
                                ft.Text("Panel Principal", size=20, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                                ft.Text("Resumen del sistema", size=12, color=tc["text_secondary"]),
                            ], spacing=2),
                        ], spacing=14),
                    ], alignment=ft.MainAxisAlignment.START),
                    padding=ft.padding.symmetric(horizontal=24, vertical=16),
                    bgcolor=tc["header_bg"],
                    border=ft.border.all(1, tc["header_border"]),
                    margin=ft.margin.only(left=24, right=24, top=16),
                ),
                ft.Container(height=24),
                ft.Container(
                    content=self._stat_personal_container,
                    margin=ft.margin.only(left=24, right=24),
                ),
                ft.Container(height=24),
                ft.Container(
                    content=self._stat_permisos_container,
                    margin=ft.margin.only(left=24, right=24),
                ),
                ft.Container(expand=True),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

    def _stat_card(self, icon, value, label, accent, subtitle=""):
        tc = theme_colors(self.dark_mode)
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=24, color=accent),
                    ft.Container(expand=True),
                ]),
                ft.Text(value, size=32, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Text(label, size=14, weight=ft.FontWeight.W_600, color=tc["text_primary"]),
                ft.Text(subtitle, size=11, color=tc["text_secondary"]),
            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=tc["stat_bg"],
            border_radius=14,
            padding=ft.padding.symmetric(vertical=24, horizontal=20),
            expand=True,
            border=ft.border.all(1, tc["stat_border"]),
        )

    def _calcular_estadisticas(self):
        personal = self.personal_ctrl.obtener_todos()
        permisos = self.permisos_ctrl.obtener_todos()
        comisiones = self.comisiones_ctrl.obtener_todos()

        personal_disponible = 0
        personal_permiso = 0
        personal_comision = 0

        personal_ids = set(p.get("id") for p in personal)

        permisos_activos = []
        permisos_por_expirar = []
        permisos_expirados = []

        for p in permisos:
            estado, _ = obtener_estado(p.get("fecha_hasta", ""))
            if estado == "Vigente":
                permisos_activos.append(p)
            elif estado == "Por Expirar":
                permisos_por_expirar.append(p)
            elif estado == "Expirado":
                permisos_expirados.append(p)

        permisos_activos_ids = set(p.get("personal_id") for p in permisos_activos)
        comisiones_activas_ids = set(c.get("personal_id") for c in comisiones)

        for p in personal:
            pid = p.get("id")
            if pid in permisos_activos_ids:
                personal_permiso += 1
            elif pid in comisiones_activas_ids:
                personal_comision += 1
            else:
                personal_disponible += 1

        return {
            "personal_disponible": personal_disponible,
            "personal_permiso": personal_permiso,
            "personal_comision": personal_comision,
            "permisos_vigentes": len(permisos_activos),
            "permisos_por_expirar": len(permisos_por_expirar),
            "permisos_expirados": len(permisos_expirados),
            "permisos_por_expirar_lista": permisos_por_expirar,
        }

    def load_data(self):
        stats = self._calcular_estadisticas()

        self.stat_personal_disponible.content.controls[1].value = str(stats["personal_disponible"])
        self.stat_personal_permiso.content.controls[1].value = str(stats["personal_permiso"])
        self.stat_personal_comision.content.controls[1].value = str(stats["personal_comision"])

        self.stat_permiso_vigente.content.controls[1].value = str(stats["permisos_vigentes"])
        self.stat_permiso_expirar.content.controls[1].value = str(stats["permisos_por_expirar"])
        self.stat_permiso_expirado.content.controls[1].value = str(stats["permisos_expirados"])

        self.update()
        return stats

    def did_mount(self):
        self.load_data()
        async def animate():
            await asyncio.sleep(0.05)
            self.opacity = 1
            self.update()
        asyncio.create_task(animate())