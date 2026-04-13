import flet as ft
import asyncio
from datetime import datetime
from core.theme import theme_colors
from core.estado_utils import obtener_estado


class DashboardView(ft.Container):
    def __init__(self, personal_ctrl, permisos_ctrl, comisiones_ctrl, situaciones_ctrl=None, on_navigate_personal=None, on_navigate_permisos=None, on_navigate_comisiones=None, on_navigate_situaciones=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.personal_ctrl = personal_ctrl
        self.permisos_ctrl = permisos_ctrl
        self.comisiones_ctrl = comisiones_ctrl
        self.situaciones_ctrl = situaciones_ctrl
        self.on_navigate_personal = on_navigate_personal
        self.on_navigate_permisos = on_navigate_permisos
        self.on_navigate_comisiones = on_navigate_comisiones
        self.on_navigate_situaciones = on_navigate_situaciones
        self.dark_mode = dark_mode

        self._build_ui()

    def _build_ui(self):
        tc = theme_colors(self.dark_mode)
        W_FULL = 900

        self._build_stat_cards(tc)
        self._build_sections(tc, W_FULL)

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
                                ft.Text("Panel de Control", size=22, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                                ft.Text("Resumen general del sistema", size=12, color=tc["text_secondary"]),
                            ], spacing=2),
                        ], spacing=14),
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.UPDATE, size=16, color=tc["text_secondary"]),
                                ft.Text(datetime.now().strftime("%d/%m/%Y %H:%M"), size=12, color=tc["text_secondary"]),
                            ], spacing=6),
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(horizontal=24, vertical=16),
                    bgcolor=tc["header_bg"],
                    border=ft.border.all(1, tc["header_border"]),
                    border_radius=14,
                    margin=ft.margin.only(left=16, right=24, top=16),
                ),
                ft.Container(height=20),
                ft.Container(
                    content=self.stats_row,
                    margin=ft.margin.only(left=16, right=24),
                ),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Row([
                        self._build_section_card(tc, "Personal", ft.Icons.PEOPLE, ft.Colors.GREEN_400, self._personal_stats, self.on_navigate_personal),
                        self._build_section_card(tc, "Permisos", ft.Icons.EVENT_NOTE, ft.Colors.CYAN_400, self._permisos_stats, self.on_navigate_permisos),
                        self._build_section_card(tc, "Comisiones", ft.Icons.BUSINESS_CENTER, ft.Colors.ORANGE_400, self._comisiones_stats, self.on_navigate_comisiones),
                        self._build_section_card(tc, "Situaciones", ft.Icons.WARNING_AMBER_ROUNDED, ft.Colors.RED_400, self._situaciones_stats, self.on_navigate_situaciones),
                    ], spacing=16, alignment=ft.MainAxisAlignment.CENTER, expand=True),
                    padding=ft.padding.only(left=16),
                ),
                ft.Container(height=20),
                ft.Container(
                    content=self._alerts_container,
                    margin=ft.margin.only(left=16, right=24),
                ),
                ft.Container(expand=True),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        )

    def _build_stat_cards(self, tc):
        self.stat_total_personal = self._create_stat_card(ft.Icons.PEOPLE, "0", "Total Personal", ft.Colors.GREEN_400)
        self.stat_total_permisos = self._create_stat_card(ft.Icons.EVENT_NOTE, "0", "Total Permisos", ft.Colors.CYAN_400)
        self.stat_total_comisiones = self._create_stat_card(ft.Icons.BUSINESS_CENTER, "0", "Total Comisiones", ft.Colors.ORANGE_400)
        self.stat_activos = self._create_stat_card(ft.Icons.CHECK_CIRCLE, "0", "Disponibles", ft.Colors.GREEN_400)

        self.stats_row = ft.Container(
            content=ft.Row([
                self.stat_total_personal,
                self.stat_total_permisos,
                self.stat_total_comisiones,
                self.stat_activos,
            ], spacing=16),
        )

    def _build_sections(self, tc, W_FULL):
        self._personal_stats = self._create_section_stats([
            ("Con Cargo", "0"),
            ("Sin Cargo", "0"),
            ("Grados Únicos", "0"),
        ], ft.Colors.GREEN_400)

        self._permisos_stats = self._create_section_stats([
            ("Vigentes", "0"),
            ("Por Expirar", "0"),
            ("Expirados", "0"),
        ], ft.Colors.CYAN_400)

        self._comisiones_stats = self._create_section_stats([
            ("Activas", "0"),
            ("Finalizadas", "0"),
            ("Por Salir", "0"),
        ], ft.Colors.ORANGE_400)

        self._situaciones_stats = self._create_section_stats([
            ("Activas", "0"),
            ("Resueltas", "0"),
            ("Total", "0"),
        ], ft.Colors.RED_400)

        self._alert_list = ft.Column([], spacing=8)
        
        self._alerts_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=20, color=ft.Colors.AMBER_400),
                    ft.Text("Alertas y Notificaciones", size=16, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ], spacing=10),
                ft.Container(height=12),
                self._alert_list,
            ], tight=True),
            padding=20,
            bgcolor=tc["bg_card"],
            border_radius=14,
            border=ft.border.all(1, tc["border_primary"]),
        )

    def _create_stat_card(self, icon, value, label, accent):
        tc = theme_colors(self.dark_mode)
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=22, color=accent),
                    ft.Container(expand=True),
                ]),
                ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Text(label, size=11, color=tc["text_secondary"]),
            ], spacing=2),
            bgcolor=tc["stat_bg"],
            border_radius=14,
            padding=ft.padding.symmetric(vertical=18, horizontal=20),
            expand=True,
            border=ft.border.all(1, tc["stat_border"]),
        )

    def _create_section_stats(self, items, accent_color):
        tc = theme_colors(self.dark_mode)
        controls = []
        for label, value in items:
            controls.append(
                ft.Row([
                    ft.Text(label, size=12, color=tc["text_secondary"], expand=True),
                    ft.Text(value, size=14, weight=ft.FontWeight.BOLD, color=accent_color),
                ], spacing=8)
            )
        return ft.Column(controls, spacing=6)

    def _build_section_card(self, tc, title, icon, icon_color, stats_col, on_click):
        def navigate(e):
            if on_click:
                on_click()

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=24, color=icon_color),
                        bgcolor=tc["icon_bg"],
                        border_radius=10,
                        padding=10,
                    ),
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ], spacing=12),
                ft.Container(height=12),
                stats_col,
                ft.Container(height=12),
                ft.Container(
                    content=ft.Row([
                        ft.Text("Ver más", size=12, color=ft.Colors.GREEN_400),
                        ft.Icon(ft.Icons.ARROW_FORWARD, size=14, color=ft.Colors.GREEN_400),
                    ], spacing=4),
                    on_click=navigate,
                    ink=True,
                ),
            ], tight=True),
            padding=20,
            bgcolor=tc["bg_card"],
            border_radius=14,
            border=ft.border.all(1, tc["border_primary"]),
            expand=True,
        )

    def _calcular_estadisticas(self):
        personal = self.personal_ctrl.obtener_todos()
        permisos = self.permisos_ctrl.obtener_todos()
        comisiones = self.comisiones_ctrl.obtener_todos()
        
        situaciones = []
        if self.situaciones_ctrl:
            situaciones = self.situaciones_ctrl.obtener_todos()

        total_personal = len(personal)
        total_permisos = len(permisos)
        total_comisiones = len(comisiones)
        total_situaciones = len(situaciones)

        con_cargo = sum(1 for p in personal if p.get("cargo"))
        sin_cargo = total_personal - con_cargo
        grados_unicos = len(set(p.get("grado_jerarquia", "") for p in personal if p.get("grado_jerarquia")))

        permisos_vigent = 0
        permisos_por_expirar = 0
        permisos_expirados = 0

        for p in permisos:
            estado, _ = obtener_estado(p.get("fecha_hasta", ""))
            if estado == "Vigente":
                permisos_vigent += 1
            elif estado == "Por Expirar":
                permisos_por_expirar += 1
            elif estado == "Expirado":
                permisos_expirados += 1

        activas = sum(1 for c in comisiones if not c.get("finalizada", 0))
        finalizadas = total_comisiones - activas
        
        from datetime import datetime
        hoy = datetime.now().strftime("%d/%m/%Y")
        por_salir = sum(1 for c in comisiones if not c.get("finalizada", 0) and c.get("fecha_salida", "") > hoy)

        situaciones_activas = sum(1 for s in situaciones if s.get("estado", "Activo") == "Activo")
        situaciones_resueltas = total_situaciones - situaciones_activas

        permisos_activos_ids = set(p.get("personal_id") for p in permisos if obtener_estado(p.get("fecha_hasta", ""))[0] == "Vigente")
        comisiones_activas_ids = set(c.get("personal_id") for c in comisiones if not c.get("finalizada", 0))

        disponibles = sum(1 for p in personal if p.get("id") not in permisos_activos_ids and p.get("id") not in comisiones_activas_ids)
        personal_permiso = sum(1 for p in personal if p.get("id") in permisos_activos_ids)
        personal_comision = sum(1 for p in personal if p.get("id") in comisiones_activas_ids and p.get("id") not in permisos_activos_ids)

        return {
            "total_personal": total_personal,
            "total_permisos": total_permisos,
            "total_comisiones": total_comisiones,
            "total_situaciones": total_situaciones,
            "disponibles": disponibles,
            "personal_permiso": personal_permiso,
            "personal_comision": personal_comision,
            "con_cargo": con_cargo,
            "sin_cargo": sin_cargo,
            "grades_unicos": grados_unicos,
            "permisos_vigent": permisos_vigent,
            "permisos_por_expirar": permisos_por_expirar,
            "permisos_expirados": permisos_expirados,
            "comisiones_activas": activas,
            "comisiones_finalizadas": finalizadas,
            "comisiones_por_salir": por_salir,
            "situaciones_activas": situaciones_activas,
            "situaciones_resueltas": situaciones_resueltas,
            "permisos_por_expirar_lista": [p for p in permisos if obtener_estado(p.get("fecha_hasta", ""))[0] == "Por Expirar"],
        }

    def load_data(self):
        stats = self._calcular_estadisticas()

        self.stat_total_personal.content.controls[1].value = str(stats["total_personal"])
        self.stat_total_permisos.content.controls[1].value = str(stats["total_permisos"])
        self.stat_total_comisiones.content.controls[1].value = str(stats["total_comisiones"])
        self.stat_activos.content.controls[1].value = str(stats["disponibles"])

        self._update_section_stats(self._personal_stats, [
            ("Con Cargo", str(stats["con_cargo"])),
            ("Sin Cargo", str(stats["sin_cargo"])),
            ("Grados Únicos", str(stats["grades_unicos"])),
        ])

        self._update_section_stats(self._permisos_stats, [
            ("Vigentes", str(stats["permisos_vigent"])),
            ("Por Expirar", str(stats["permisos_por_expirar"])),
            ("Expirados", str(stats["permisos_expirados"])),
        ])

        self._update_section_stats(self._comisiones_stats, [
            ("Activas", str(stats["comisiones_activas"])),
            ("Finalizadas", str(stats["comisiones_finalizadas"])),
            ("Por Salir", str(stats["comisiones_por_salir"])),
        ])
        
        self._update_section_stats(self._situaciones_stats, [
            ("Activas", str(stats["situaciones_activas"])),
            ("Resueltas", str(stats["situaciones_resueltas"])),
            ("Total", str(stats["total_situaciones"])),
        ])

        self._build_alerts(stats)

        self.update()
        return stats

    def _update_section_stats(self, col, items):
        for i, (label, value) in enumerate(items):
            col.controls[i].controls[1].value = value

    def _build_alerts(self, stats):
        tc = theme_colors(self.dark_mode)
        self._alert_list.controls.clear()

        if stats["permisos_por_expirar"] > 0:
            alert = self._create_alert(
                ft.Icons.WARNING_AMBER_ROUNDED,
                ft.Colors.AMBER_400,
                f"{stats['permisos_por_expirar']} permiso(s) por expirar en los próximos días",
                f"Último: {stats['permisos_por_expirar_lista'][0].get('nombres', '')} {stats['permisos_por_expirar_lista'][0].get('apellidos', '')}" if stats["permisos_por_expirar_lista"] else "",
                lambda: self.on_navigate_permisos() if self.on_navigate_permisos else None
            )
            self._alert_list.controls.append(alert)

        if stats["comisiones_activas"] > 0:
            alert = self._create_alert(
                ft.Icons.BUSINESS_CENTER,
                ft.Colors.ORANGE_400,
                f"{stats['comisiones_activas']} comisión(es) activa(s)",
                "Personal en comisión actualmente",
                lambda: self.on_navigate_comisiones() if self.on_navigate_comisiones else None
            )
            self._alert_list.controls.append(alert)

        if stats["personal_permiso"] > 0 or stats["personal_comision"] > 0:
            alert = self._create_alert(
                ft.Icons.GROUP,
                ft.Colors.CYAN_400,
                f"Personal ocupado: {stats['personal_permiso']} de permiso, {stats['personal_comision']} en comisión",
                f"{stats['disponibles']} disponibles",
                lambda: self.on_navigate_personal() if self.on_navigate_personal else None
            )
            self._alert_list.controls.append(alert)

        if not self._alert_list.controls:
            self._alert_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=20, color=ft.Colors.GREEN_400),
                        ft.Text("Todo al día - Sin alertas pendientes", size=13, color=tc["text_secondary"]),
                    ], spacing=8),
                    padding=8,
                )
            )

    def _create_alert(self, icon, icon_color, title, subtitle, on_click):
        tc = theme_colors(self.dark_mode)
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=20, color=icon_color),
                    bgcolor=ft.Colors.with_opacity(0.1, icon_color),
                    border_radius=8,
                    padding=8,
                ),
                ft.Column([
                    ft.Text(title, size=13, weight=ft.FontWeight.W_500, color=tc["text_primary"]),
                    ft.Text(subtitle, size=11, color=tc["text_secondary"]),
                ], spacing=2, expand=True),
                ft.Container(
                    content=ft.Icon(ft.Icons.CHEVRON_RIGHT, size=18, color=tc["text_tertiary"]),
                    on_click=on_click,
                    ink=True,
                ),
            ], spacing=12, alignment=ft.MainAxisAlignment.CENTER),
            padding=12,
            bgcolor=tc["bg_card"],
            border_radius=10,
            border=ft.border.all(1, tc["border_primary"]),
            on_click=on_click,
            ink=True,
        )

    def did_mount(self):
        self.load_data()
        async def animate():
            await asyncio.sleep(0.05)
            self.opacity = 1
            self.update()
        asyncio.create_task(animate())