import flet as ft
import asyncio
from datetime import datetime
from core.theme import theme_colors
from core.estado_utils import obtener_estado
from core.constants import FECHA_FORMAT
from core.components.charts import ProgressChart, MiniStatsRow


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

        self._build_stat_cards(tc)
        self._build_charts(tc)
        self._build_summary_row(tc)

        self.content = ft.Column(
            controls=[
                self._build_header(tc),
                ft.Container(height=16),
                self._build_stats_section(),
                ft.Container(height=20),
                self._build_charts_section(),
                ft.Container(height=20),
                self._build_summary_section(),
                ft.Container(height=20),
                self._build_alerts_section(),
                ft.Container(expand=True),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        )

    def _build_header(self, tc):
        return ft.Container(
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
        )

    def _build_stat_cards(self, tc):
        self.card_personal = self._create_stat_card(ft.Icons.PEOPLE, "0", "Personal", ft.Colors.GREEN_400)
        self.card_permisos = self._create_stat_card(ft.Icons.EVENT_NOTE, "0", "Permisos", ft.Colors.CYAN_400)
        self.card_comisiones = self._create_stat_card(ft.Icons.BUSINESS_CENTER, "0", "Comisiones", ft.Colors.ORANGE_400)
        self.card_disponibles = self._create_stat_card(ft.Icons.CHECK_CIRCLE, "0", "Disponibles", ft.Colors.GREEN_400)

        self.stats_row = ft.Container(
            content=ft.Row([
                self.card_personal,
                self.card_permisos,
                self.card_comisiones,
                self.card_disponibles,
            ], spacing=16),
        )

    def _build_stats_section(self):
        return ft.Container(
            content=self.stats_row,
            margin=ft.margin.only(left=16, right=24),
        )

    def _build_charts(self, tc):
        self.chart_permisos = ProgressChart(
            title="Estado de Permisos",
            data=[
                {"label": "Vigente", "value": 0, "color": ft.Colors.GREEN_400},
                {"label": "Por Expirar", "value": 0, "color": ft.Colors.AMBER_400},
                {"label": "Expirado", "value": 0, "color": ft.Colors.RED_400},
            ],
            dark_mode=self.dark_mode,
            width=None,
            height=180,
        )

        self.chart_comisiones = ProgressChart(
            title="Estado de Comisiones",
            data=[
                {"label": "Activas", "value": 0, "color": ft.Colors.ORANGE_400},
                {"label": "Finalizadas", "value": 0, "color": ft.Colors.GREEN_400},
                {"label": "Por Salir", "value": 0, "color": ft.Colors.CYAN_400},
            ],
            dark_mode=self.dark_mode,
            width=None,
            height=180,
        )

    def _build_charts_section(self):
        return ft.Container(
            content=ft.Row([
                ft.Container(content=self.chart_permisos, expand=1),
                ft.Container(width=16),
                ft.Container(content=self.chart_comisiones, expand=1),
            ], spacing=0),
            margin=ft.margin.only(left=16, right=24),
        )

    def _build_summary_row(self, tc):
        self.summary_row = MiniStatsRow(
            items=[
                {"label": "En Permiso", "value": "0", "icon": ft.Icons.EVENT_NOTE, "color": ft.Colors.CYAN_400},
                {"label": "En Comisión", "value": "0", "icon": ft.Icons.BUSINESS_CENTER, "color": ft.Colors.ORANGE_400},
                {"label": "En Situación", "value": "0", "icon": ft.Icons.WARNING, "color": ft.Colors.RED_400},
                {"label": "Con Cargo", "value": "0", "icon": ft.Icons.BADGE, "color": ft.Colors.PURPLE_400},
            ],
            dark_mode=self.dark_mode,
            spacing=12,
        )

    def _build_summary_section(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("Estado del Personal", size=16, weight=ft.FontWeight.BOLD, color=theme_colors(self.dark_mode)["text_primary"]),
                ft.Container(height=12),
                self.summary_row,
            ], spacing=0),
            margin=ft.margin.only(left=16, right=24),
        )

    def _build_alerts_section(self):
        tc = theme_colors(self.dark_mode)
        
        self._alert_list = ft.Column([], spacing=8)
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=20, color=ft.Colors.AMBER_400),
                    ft.Text("Alertas Recientes", size=16, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ], spacing=10),
                ft.Container(height=12),
                self._alert_list,
            ], tight=True),
            padding=20,
            bgcolor=tc["bg_card"],
            border_radius=14,
            border=ft.border.all(1, tc["border_primary"]),
            margin=ft.margin.only(left=16, right=24),
        )

    def _create_stat_card(self, icon, value, label, accent):
        tc = theme_colors(self.dark_mode)
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, color=accent, size=24),
                        bgcolor=tc["icon_bg"],
                        border_radius=12,
                        padding=12,
                    ),
                    ft.Container(expand=True),
                ]),
                ft.Container(height=8),
                ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Text(label, size=12, color=tc["text_secondary"]),
            ], spacing=0),
            bgcolor=tc["bg_card"],
            border_radius=16,
            border=ft.border.all(1, tc["stat_border"]),
            padding=ft.padding.all(20),
            expand=1,
            ink=True,
        )

    def load_data(self):
        stats = self._calcular_estadisticas()

        self.card_personal.content.controls[2].value = str(stats["total_personal"])
        self.card_permisos.content.controls[2].value = str(stats["permisos_vigent"] + stats["permisos_por_expirar"])
        self.card_comisiones.content.controls[2].value = str(stats["comisiones_activas"])
        self.card_disponibles.content.controls[2].value = str(stats["disponibles"])

        permisos_total = stats["permisos_vigent"] + stats["permisos_por_expirar"] + stats["permisos_expirados"]
        self.chart_permisos.data = [
            {"label": f"Vigente ({stats['permisos_vigent']})", "value": stats["permisos_vigent"] + 1, "color": ft.Colors.GREEN_400},
            {"label": f"Por Expirar ({stats['permisos_por_expirar']})", "value": stats["permisos_por_expirar"] + 1, "color": ft.Colors.AMBER_400},
            {"label": f"Expirado ({stats['permisos_expirados']})", "value": stats["permisos_expirados"] + 1, "color": ft.Colors.RED_400},
        ]
        self.chart_permisos._build_chart()

        comisiones_total = stats["comisiones_activas"] + stats["comisiones_finalizadas"] + stats["comisiones_por_salir"]
        self.chart_comisiones.data = [
            {"label": f"Activas ({stats['comisiones_activas']})", "value": stats["comisiones_activas"] + 1, "color": ft.Colors.ORANGE_400},
            {"label": f"Finalizadas ({stats['comisiones_finalizadas']})", "value": stats["comisiones_finalizadas"] + 1, "color": ft.Colors.GREEN_400},
            {"label": f"Por Salir ({stats['comisiones_por_salir']})", "value": stats["comisiones_por_salir"] + 1, "color": ft.Colors.CYAN_400},
        ]
        self.chart_comisiones._build_chart()

        items = [
            {"label": "En Permiso", "value": str(stats["personal_permiso"]), "icon": ft.Icons.EVENT_NOTE, "color": ft.Colors.CYAN_400},
            {"label": "En Comisión", "value": str(stats["personal_comision"]), "icon": ft.Icons.BUSINESS_CENTER, "color": ft.Colors.ORANGE_400},
            {"label": "En Situación", "value": str(stats["personal_situacion"]), "icon": ft.Icons.WARNING, "color": ft.Colors.RED_400},
            {"label": "Con Cargo", "value": str(stats["con_cargo"]), "icon": ft.Icons.BADGE, "color": ft.Colors.PURPLE_400},
        ]
        self.summary_row = MiniStatsRow(items=items, dark_mode=self.dark_mode, spacing=12)

        self._build_alerts(stats)

        try:
            self.update()
        except RuntimeError:
            pass

    def _build_alerts(self, stats):
        tc = theme_colors(self.dark_mode)
        self._alert_list.controls.clear()

        alertas = []

        if stats["permisos_por_expirar"] > 0:
            alertas.append({
                "icon": ft.Icons.WARNING_AMBER_ROUNDED,
                "color": ft.Colors.AMBER_400,
                "text": f"{stats['permisos_por_expirar']} permisos por expirar"
            })

        if stats["comisiones_por_salir"] > 0:
            alertas.append({
                "icon": ft.Icons.SCHEDULE,
                "color": ft.Colors.CYAN_400,
                "text": f"{stats['comisiones_por_salir']} comisiones por salir"
            })

        if stats["situaciones_activas"] > 0:
            alertas.append({
                "icon": ft.Icons.WARNING,
                "color": ft.Colors.RED_400,
                "text": f"{stats['situaciones_activas']} situaciones irregulares activas"
            })

        if stats["permisos_expirados"] > 0:
            alertas.append({
                "icon": ft.Icons.CANCEL,
                "color": ft.Colors.RED_400,
                "text": f"{stats['permisos_expirados']} permisos expirados"
            })

        if not alertas:
            alertas.append({
                "icon": ft.Icons.CHECK_CIRCLE,
                "color": ft.Colors.GREEN_400,
                "text": "No hay alertas pendientes"
            })

        for alerta in alertas:
            self._alert_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(alerta["icon"], color=alerta["color"], size=20),
                        ft.Container(width=12),
                        ft.Text(alerta["text"], size=13, color=tc["text_primary"]),
                    ], spacing=0),
                    padding=ft.padding.symmetric(vertical=8, horizontal=12),
                    bgcolor=tc["input_bg"],
                    border_radius=8,
                )
            )

    def _calcular_estadisticas(self):
        personal = self.personal_ctrl.obtener_todos() if self.personal_ctrl else []
        permisos = self.permisos_ctrl.obtener_todos() if self.permisos_ctrl else []
        comisiones = self.comisiones_ctrl.obtener_todos() if self.comisiones_ctrl else []
        situaciones = self.situaciones_ctrl.obtener_todos() if self.situaciones_ctrl else []

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

        activas = 0
        finalizadas = 0
        por_salir = 0
        hoy = datetime.now().strftime(FECHA_FORMAT)

        for c in comisiones:
            if c.get("finalizada"):
                finalizadas += 1
            elif c.get("fecha_salida", "") > hoy:
                por_salir += 1
            else:
                activas += 1

        situaciones_activas = sum(1 for s in situaciones if s.get("estado", "Activo") == "Activo")
        situaciones_resueltas = total_situaciones - situaciones_activas

        permisos_activos_ids = set(p.get("personal_id") for p in permisos if obtener_estado(p.get("fecha_hasta", ""))[0] in ("Vigente", "Por Expirar"))
        comisiones_activas_ids = set(c.get("personal_id") for c in comisiones if not c.get("finalizada", 0))
        situaciones_activas_ids = set(s.get("personal_id") for s in situaciones if s.get("estado", "Activo") == "Activo")

        ocupados_ids = permisos_activos_ids | comisiones_activas_ids | situaciones_activas_ids
        disponibles = sum(1 for p in personal if p.get("id") not in ocupados_ids)
        personal_permiso = sum(1 for p in personal if p.get("id") in permisos_activos_ids)
        personal_comision = sum(1 for p in personal if p.get("id") in comisiones_activas_ids and p.get("id") not in permisos_activos_ids)
        personal_situacion = sum(1 for p in personal if p.get("id") in situaciones_activas_ids and p.get("id") not in permisos_activos_ids and p.get("id") not in comisiones_activas_ids)

        return {
            "total_personal": total_personal,
            "total_permisos": total_permisos,
            "total_comisiones": total_comisiones,
            "total_situaciones": total_situaciones,
            "disponibles": disponibles,
            "personal_permiso": personal_permiso,
            "personal_comision": personal_comision,
            "personal_situacion": personal_situacion,
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

    def _build_charts(self, tc):
        self.chart_permisos = ProgressChart(
            title="Estado de Permisos",
            data=[
                {"label": "Vigente", "value": 0, "color": ft.Colors.GREEN_400},
                {"label": "Por Expirar", "value": 0, "color": ft.Colors.AMBER_400},
                {"label": "Expirado", "value": 0, "color": ft.Colors.RED_400},
            ],
            dark_mode=self.dark_mode,
            width=None,
            height=180,
        )

        self.chart_comisiones = ProgressChart(
            title="Estado de Comisiones",
            data=[
                {"label": "Activas", "value": 0, "color": ft.Colors.ORANGE_400},
                {"label": "Finalizadas", "value": 0, "color": ft.Colors.GREEN_400},
                {"label": "Por Salir", "value": 0, "color": ft.Colors.CYAN_400},
            ],
            dark_mode=self.dark_mode,
            width=None,
            height=180,
        )

    def _build_charts_section(self):
        return ft.Container(
            content=ft.Row([
                ft.Container(content=self.chart_permisos, expand=1),
                ft.Container(width=16),
                ft.Container(content=self.chart_comisiones, expand=1),
            ], spacing=0),
            margin=ft.margin.only(left=16, right=24),
        )

    def _build_summary_row(self, tc):
        self.summary_row = MiniStatsRow(
            items=[
                {"label": "En Permiso", "value": "0", "icon": ft.Icons.EVENT_NOTE, "color": ft.Colors.CYAN_400},
                {"label": "En Comisión", "value": "0", "icon": ft.Icons.BUSINESS_CENTER, "color": ft.Colors.ORANGE_400},
                {"label": "En Situación", "value": "0", "icon": ft.Icons.WARNING, "color": ft.Colors.RED_400},
                {"label": "Con Cargo", "value": "0", "icon": ft.Icons.BADGE, "color": ft.Colors.PURPLE_400},
            ],
            dark_mode=self.dark_mode,
            spacing=12,
        )

    def _build_summary_section(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("Estado del Personal", size=16, weight=ft.FontWeight.BOLD, color=theme_colors(self.dark_mode)["text_primary"]),
                ft.Container(height=12),
                self.summary_row,
            ], spacing=0),
            margin=ft.margin.only(left=16, right=24),
        )

    def _build_alerts_section(self):
        tc = theme_colors(self.dark_mode)
        
        self._alert_list = ft.Column([], spacing=8)
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=20, color=ft.Colors.AMBER_400),
                    ft.Text("Alertas Recientes", size=16, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ], spacing=10),
                ft.Container(height=12),
                self._alert_list,
            ], tight=True),
            padding=20,
            bgcolor=tc["bg_card"],
            border_radius=14,
            border=ft.border.all(1, tc["border_primary"]),
            margin=ft.margin.only(left=16, right=24),
        )

    def _create_stat_card(self, icon, value, label, accent):
        tc = theme_colors(self.dark_mode)
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, color=accent, size=24),
                        bgcolor=tc["icon_bg"],
                        border_radius=12,
                        padding=12,
                    ),
                    ft.Container(expand=True),
                ]),
                ft.Container(height=8),
                ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Text(label, size=12, color=tc["text_secondary"]),
            ], spacing=0),
            bgcolor=tc["bg_card"],
            border_radius=16,
            border=ft.border.all(1, tc["stat_border"]),
            padding=ft.padding.all(20),
            expand=1,
            ink=True,
        )

    def load_data(self):
        stats = self._calcular_estadisticas()

        self.card_personal.content.controls[2].value = str(stats["total_personal"])
        self.card_permisos.content.controls[2].value = str(stats["permisos_vigent"] + stats["permisos_por_expirar"])
        self.card_comisiones.content.controls[2].value = str(stats["comisiones_activas"])
        self.card_disponibles.content.controls[2].value = str(stats["disponibles"])

        permisos_total = stats["permisos_vigent"] + stats["permisos_por_expirar"] + stats["permisos_expirados"]
        self.chart_permisos.data = [
            {"label": f"Vigente ({stats['permisos_vigent']})", "value": stats["permisos_vigent"] + 1, "color": ft.Colors.GREEN_400},
            {"label": f"Por Expirar ({stats['permisos_por_expirar']})", "value": stats["permisos_por_expirar"] + 1, "color": ft.Colors.AMBER_400},
            {"label": f"Expirado ({stats['permisos_expirados']})", "value": stats["permisos_expirados"] + 1, "color": ft.Colors.RED_400},
        ]
        self.chart_permisos._build_chart()

        comisiones_total = stats["comisiones_activas"] + stats["comisiones_finalizadas"] + stats["comisiones_por_salir"]
        self.chart_comisiones.data = [
            {"label": f"Activas ({stats['comisiones_activas']})", "value": stats["comisiones_activas"] + 1, "color": ft.Colors.ORANGE_400},
            {"label": f"Finalizadas ({stats['comisiones_finalizadas']})", "value": stats["comisiones_finalizadas"] + 1, "color": ft.Colors.GREEN_400},
            {"label": f"Por Salir ({stats['comisiones_por_salir']})", "value": stats["comisiones_por_salir"] + 1, "color": ft.Colors.CYAN_400},
        ]
        self.chart_comisiones._build_chart()

        items = [
            {"label": "En Permiso", "value": str(stats["personal_permiso"]), "icon": ft.Icons.EVENT_NOTE, "color": ft.Colors.CYAN_400},
            {"label": "En Comisión", "value": str(stats["personal_comision"]), "icon": ft.Icons.BUSINESS_CENTER, "color": ft.Colors.ORANGE_400},
            {"label": "En Situación", "value": str(stats["personal_situacion"]), "icon": ft.Icons.WARNING, "color": ft.Colors.RED_400},
            {"label": "Con Cargo", "value": str(stats["con_cargo"]), "icon": ft.Icons.BADGE, "color": ft.Colors.PURPLE_400},
        ]
        self.summary_row = MiniStatsRow(items=items, dark_mode=self.dark_mode, spacing=12)

        self._build_alerts(stats)

        try:
            self.update()
        except RuntimeError:
            pass

    def _build_alerts(self, stats):
        tc = theme_colors(self.dark_mode)
        self._alert_list.controls.clear()

        alertas = []

        if stats["permisos_por_expirar"] > 0:
            alertas.append({
                "icon": ft.Icons.WARNING_AMBER_ROUNDED,
                "color": ft.Colors.AMBER_400,
                "text": f"{stats['permisos_por_expirar']} permisos por expirar"
            })

        if stats["comisiones_por_salir"] > 0:
            alertas.append({
                "icon": ft.Icons.SCHEDULE,
                "color": ft.Colors.CYAN_400,
                "text": f"{stats['comisiones_por_salir']} comisiones por salir"
            })

        if stats["situaciones_activas"] > 0:
            alertas.append({
                "icon": ft.Icons.WARNING,
                "color": ft.Colors.RED_400,
                "text": f"{stats['situaciones_activas']} situaciones irregulares activas"
            })

        if stats["permisos_expirados"] > 0:
            alertas.append({
                "icon": ft.Icons.CANCEL,
                "color": ft.Colors.RED_400,
                "text": f"{stats['permisos_expirados']} permisos expirados"
            })

        if not alertas:
            alertas.append({
                "icon": ft.Icons.CHECK_CIRCLE,
                "color": ft.Colors.GREEN_400,
                "text": "No hay alertas pendientes"
            })

        for alerta in alertas:
            self._alert_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(alerta["icon"], color=alerta["color"], size=20),
                        ft.Container(width=12),
                        ft.Text(alerta["text"], size=13, color=tc["text_primary"]),
                    ], spacing=0),
                    padding=ft.padding.symmetric(vertical=8, horizontal=12),
                    bgcolor=tc["input_bg"],
                    border_radius=8,
                )
            )

    def _calcular_estadisticas(self):
        personal = self.personal_ctrl.obtener_todos() if self.personal_ctrl else []
        permisos = self.permisos_ctrl.obtener_todos() if self.permisos_ctrl else []
        comisiones = self.comisiones_ctrl.obtener_todos() if self.comisiones_ctrl else []
        situaciones = self.situaciones_ctrl.obtener_todos() if self.situaciones_ctrl else []

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

        activas = 0
        finalizadas = 0
        por_salir = 0
        hoy = datetime.now().strftime(FECHA_FORMAT)

        for c in comisiones:
            if c.get("finalizada"):
                finalizadas += 1
            elif c.get("fecha_salida", "") > hoy:
                por_salir += 1
            else:
                activas += 1

        situaciones_activas = sum(1 for s in situaciones if s.get("estado", "Activo") == "Activo")
        situaciones_resueltas = total_situaciones - situaciones_activas

        permisos_activos_ids = set(p.get("personal_id") for p in permisos if obtener_estado(p.get("fecha_hasta", ""))[0] in ("Vigente", "Por Expirar"))
        comisiones_activas_ids = set(c.get("personal_id") for c in comisiones if not c.get("finalizada", 0))
        situaciones_activas_ids = set(s.get("personal_id") for s in situaciones if s.get("estado", "Activo") == "Activo")

        ocupados_ids = permisos_activos_ids | comisiones_activas_ids | situaciones_activas_ids
        disponibles = sum(1 for p in personal if p.get("id") not in ocupados_ids)
        personal_permiso = sum(1 for p in personal if p.get("id") in permisos_activos_ids)
        personal_comision = sum(1 for p in personal if p.get("id") in comisiones_activas_ids and p.get("id") not in permisos_activos_ids)
        personal_situacion = sum(1 for p in personal if p.get("id") in situaciones_activas_ids and p.get("id") not in permisos_activos_ids and p.get("id") not in comisiones_activos_ids)

        return {
            "total_personal": total_personal,
            "total_permisos": total_permisos,
            "total_comisiones": total_comisiones,
            "total_situaciones": total_situaciones,
            "disponibles": disponibles,
            "personal_permiso": personal_permiso,
            "personal_comision": personal_comision,
            "personal_situacion": personal_situacion,
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

    def did_mount(self):
        self.load_data()
        async def animate():
            await asyncio.sleep(0.05)
            self.opacity = 1
            try:
                self.update()
            except RuntimeError:
                pass
        asyncio.create_task(animate())