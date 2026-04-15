import flet as ft
import asyncio
from datetime import datetime
from core.constants import FECHA_FORMAT, TIPOS_SITUACION
from core.theme import theme_colors
from core.components.loading import LoadingIndicator
from core.components.pagination import PaginationControl
from core.components.filter_panel_base import FilterPanelBase, FilterPanelContainer
from core.components.stats_panel import StatsPanel


class SituacionesDashboard(ft.Container):
    def __init__(self, controller, personal_id=None, on_back=None, on_add=None, on_edit=None, on_delete=None, on_view_detail=None, on_resolver=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.controller = controller
        self.personal_id = personal_id
        self.on_back = on_back
        self.on_add = on_add
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_view_detail = on_view_detail
        self.on_resolver = on_resolver
        self.dark_mode = dark_mode

        self.todos_los_registros = []
        self.registros_filtrados = []
        self.pagina_actual = 1
        self.registros_por_pagina = 10

        self.filtros_abiertos = False

        self._build_ui()

    def _build_ui(self):
        tc = theme_colors(self.dark_mode)

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("#", weight=ft.FontWeight.BOLD, size=12, color=tc["table_header"])),
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD, size=13, color=tc["table_header"])),
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD, size=13, color=tc["table_header"])),
                ft.DataColumn(ft.Text("Fecha Inicio", weight=ft.FontWeight.BOLD, size=13, color=tc["table_header"])),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD, size=13, color=tc["table_header"])),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, size=13, color=tc["table_header"])),
            ],
            rows=[],
            column_spacing=16,
            data_row_min_height=52,
            heading_row_color=tc["table_header_bg"],
            heading_row_height=44,
            border_radius=14,
            border=ft.border.all(1, tc["table_border"]),
        )

        self.tabla_container = ft.Container(
            content=self.data_table,
            border_radius=14,
            border=ft.border.all(1, tc["table_border"]),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            bgcolor=tc["bg_card"],
        )

        self.lbl_count = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.TABLE_CHART, size=18, color=tc["text_secondary"]),
                ft.Text("0", size=14, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Text("registrados", size=12, color=tc["text_secondary"]),
            ], spacing=6),
            bgcolor=tc["bg_card"],
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border=ft.border.all(1, tc["border_primary"]),
        )

        self.stats_config = [
            {"key": "activas", "icon": ft.Icons.WARNING, "value": "0", "label": "Situaciones Activas", "accent": ft.Colors.RED_400},
            {"key": "resueltas", "icon": ft.Icons.CHECK_CIRCLE, "value": "0", "label": "Resueltas", "accent": ft.Colors.GREEN_400},
            {"key": "privados", "icon": ft.Icons.GAVEL, "value": "0", "label": "Privados de Libertad", "accent": ft.Colors.ORANGE_400},
            {"key": "desertores", "icon": ft.Icons.RUN_CIRCLE, "value": "0", "label": "Presuntos Desertores", "accent": ft.Colors.AMBER_400},
        ]
        
        self.stats_panel = StatsPanel(
            cards_config=self.stats_config,
            dark_mode=self.dark_mode,
            spacing=16,
            margin=ft.margin.only(left=16, right=24)
        )
        
        self.panel_stats = self.stats_panel

        self.mensaje_vacio = ft.Column(
            controls=[
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=72, color=tc["empty_icon"]),
                            bgcolor=tc["empty_icon_bg"],
                            border_radius=20,
                            padding=24,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(height=16),
                        ft.Text(
                            "No hay situaciones irregulares registradas.", 
                            size=20, 
                            color=tc["empty_text"], 
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            "Las situaciones aparecerán aquí cuando se registren", 
                            size=14, 
                            color=tc["empty_subtext"]
                        ),
                      ],
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                      alignment=ft.Alignment(0, 0),
                  ),
                  ft.Container(expand=True),
            ],
            expand=True,
            visible=False,
        )

        self.search_field = ft.TextField(
            hint_text="Buscar por nombre o cedula...",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            on_submit=self._on_search,
            border_radius=12,
            filled=True,
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            focused_border_color=ft.Colors.GREEN_400,
            color=tc["input_text"],
            label_style=ft.TextStyle(color=tc["input_label"]),
            text_size=13,
        )

        self.btn_add = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD, size=18, color=ft.Colors.WHITE),
                ft.Text("Nueva", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            ], spacing=6),
            bgcolor=ft.Colors.GREEN_700,
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            ink=True,
            on_click=lambda e: self.on_add() if self.on_add else None,
        )

        self.btn_filter = ft.Container(
            content=ft.Icon(ft.Icons.FILTER_LIST, color=tc["text_secondary"], size=22),
            padding=8,
            border_radius=8,
            ink=True,
            on_click=self._toggle_filtros,
        )

        self._pagination = PaginationControl(
            on_change_page=self._cambiar_pagina,
            on_change_ppp=self._cambiar_registros_pagina,
            dark_mode=self.dark_mode,
        )

        self.content_area = ft.Column(
            controls=[
                self.panel_stats,
                ft.Row([self.lbl_count, ft.Container(expand=True)], margin=ft.margin.only(left=16, right=24)),
                ft.Container(content=self.tabla_container, margin=ft.margin.only(left=16, right=24, bottom=12)),
                self._pagination,
            ],
            expand=True,
        )
        
        self.loading_indicator = LoadingIndicator("Cargando situaciones...", dark_mode=self.dark_mode)

        self._build_filter_panel(tc)

        self.content = ft.Stack(
            controls=[
                ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Row([
                                ft.Row([
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.ORANGE_400, size=26),
                                        bgcolor=tc["icon_bg"],
                                        border_radius=10,
                                        padding=10,
                                    ),
                                    ft.Column([
                                        ft.Text("Situaciones Irregulares", size=20, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                                        ft.Text("Control de situaciones especiales", size=12, color=tc["text_secondary"]),
                                    ], spacing=2),
                                ], spacing=14),
                                ft.Container(expand=True),
                                self.search_field,
                                ft.Container(width=8),
                                self.btn_filter,
                                ft.Container(width=8),
                                self.btn_add,
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=ft.padding.symmetric(horizontal=24, vertical=16),
                            bgcolor=tc["header_bg"],
                            border=ft.border.all(1, tc["header_border"]),
                            border_radius=14,
                            margin=ft.margin.only(left=16, right=24, top=16),
                        ),
                        ft.Container(height=12),
                        ft.Stack([
                            self.content_area,
                            self.mensaje_vacio,
                        ], expand=True),
                    ],
                    expand=True,
                ),
                self._filter_container,
            ],
            expand=True,
        )

    def _cambiar_registros_pagina(self):
        self.registros_por_pagina = self._pagination.get_ppp()
        self.pagina_actual = 1
        self._render_tabla()

    def _actualizar_pagination_controls(self):
        total = len(self.registros_filtrados)
        total_paginas = max(1, (total + self.registros_por_pagina - 1) // self.registros_por_pagina)
        self._pagination.actualizar(self.pagina_actual, total_paginas, total)
        self.tabla_container.visible = total > 0
        self.mensaje_vacio.visible = total == 0
        try:
            self.update()
        except RuntimeError:
            pass

    def _cambiar_pagina(self, delta):
        nuevo = self.pagina_actual + delta
        if nuevo >= 1:
            self.pagina_actual = nuevo
            self._render_tabla()

    def _toggle_filtros(self, e):
        self.filtros_abiertos = not self.filtros_abiertos
        self._filter_panel_container.visible = self.filtros_abiertos
        self._filter_panel_container.opacity = 1.0 if self.filtros_abiertos else 0.0
        try:
            self._filter_panel_container.update()
        except RuntimeError:
            pass

    def _get_unique_values(self, field):
        valores = set()
        for s in self.todos_los_registros:
            val = s.get(field, "")
            if val:
                valores.add(val)
        return sorted(valores)

    def _build_filter_panel(self, tc):
        self._tipos_situacion = self._get_unique_values("tipo_situacion")

        self._filter_panel = FilterPanelBase(
            on_apply=self._on_filter_apply,
            on_close=self._toggle_filtros,
            dark_mode=self.dark_mode,
            show_search=False
        )
        
        self._filter_panel.add_dropdown("tipo", "Tipo de Situación", self._tipos_situacion)
        
        opciones_estado = ["Todos", "Activo", "Resuelto"]
        self._filter_panel.add_dropdown("estado", "Estado", opciones_estado)
        
        self._filter_container = FilterPanelContainer(
            filter_panel=self._filter_panel,
            dark_mode=self.dark_mode
        )

    def _on_filter_apply(self, filtros):
        tipo = filtros.get("tipo", "Todos")
        estado = filtros.get("estado", "Todos")

        resultado = []
        for s in self.todos_los_registros:
            if tipo and tipo != "Todos":
                if s.get("tipo_situacion", "") != tipo:
                    continue

            if estado and estado != "Todos":
                estado_texto = s.get("estado", "Activo")
                if estado_texto != estado:
                    continue

            resultado.append(s)

        self.registros_filtrados = resultado
        self.pagina_actual = 1
        self._render_tabla()
        self._toggle_filtros(None)

    def _on_filter_apply(self, filtros):
        tipo = filtros.get("tipo", "Todos")
        estado = filtros.get("estado", "Todos")

        resultado = []
        for s in self.todos_los_registros:
            if tipo and tipo != "Todos":
                if s.get("tipo_situacion", "") != tipo:
                    continue

            if estado and estado != "Todos":
                estado_texto = s.get("estado", "Activo")
                if estado_texto != estado:
                    continue

            resultado.append(s)

        self.registros_filtrados = resultado
        self.pagina_actual = 1
        self._render_tabla()

    def _limpiar_filtros(self):
        self._filter_panel._limpiar()
        self.registros_filtrados = list(self.todos_los_registros)
        self.pagina_actual = 1
        self._render_tabla()

    def _toggle_filtros(self, e=None):
        self.filtros_abiertos = not self.filtros_abiertos
        if self.filtros_abiertos:
            self._filter_container.show()
        else:
            self._filter_container.hide()

    def _on_search(self, e):
        filtros = self._filter_panel.get_filtros() if self._filter_panel else {}
        filtros["texto"] = self.search_field.value or ""
        self._on_filter_apply(filtros)

    def _render_tabla(self):
        tc = theme_colors(self.dark_mode)
        self.data_table.rows.clear()
        total = len(self.registros_filtrados)
        self.lbl_count.content.controls[1].value = str(total)

        total_paginas = max(1, (total + self.registros_por_pagina - 1) // self.registros_por_pagina)
        self.pagina_actual = max(1, min(self.pagina_actual, total_paginas))

        inicio = (self.pagina_actual - 1) * self.registros_por_pagina
        fin = inicio + self.registros_por_pagina
        pagina = self.registros_filtrados[inicio:fin]

        for i, s in enumerate(pagina):
            num = inicio + i + 1
            nombre = "%s %s" % (s.get("nombres", ""), s.get("apellidos", ""))
            estado = s.get("estado", "Activo")
            estado_texto = "RESUELTO" if estado == "Resuelto" else "ACTIVO"
            estado_color = ft.Colors.GREEN_700 if estado == "Resuelto" else ft.Colors.RED_700
            sid = s.get("id")

            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(num), size=12, color=tc["text_tertiary"])),
                        ft.DataCell(ft.GestureDetector(
                            content=ft.Text(nombre, size=14, color=ft.Colors.CYAN_400, weight=ft.FontWeight.W_500),
                            on_tap=lambda e, _sid=sid: self.on_view_detail(_sid) if self.on_view_detail else None,
                            mouse_cursor=ft.MouseCursor.CLICK,
                        )),
                        ft.DataCell(ft.Container(
                            content=ft.Text(s.get("tipo_situacion", ""), size=12, color=ft.Colors.ORANGE_400),
                            bgcolor=tc["badge_orange"], border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )),
                        ft.DataCell(ft.Text(s.get("fecha_inicio", ""), size=13, color=tc["table_row_text"])),
                        ft.DataCell(ft.Container(
                            content=ft.Text(estado_texto, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            bgcolor=estado_color, border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )),
                        ft.DataCell(ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400 if estado != "Resuelto" else tc["text_tertiary"], size=18),
                                padding=6, border_radius=6, ink=True,
                                on_click=lambda e, _sid=sid, _nombre=nombre, _estado=estado: self._confirmar_resolver(_sid, _nombre, _estado) if self.on_resolver and _estado != "Resuelto" else None,
                                tooltip="Resolver" if estado != "Resuelto" else "Resuelto",
                            ),
                            ft.Container(
                                content=ft.Icon(ft.Icons.EDIT, color=tc["text_secondary"], size=18),
                                padding=6, border_radius=6, ink=True,
                                on_click=lambda e, _sid=sid: self.on_edit(_sid) if self.on_edit else None,
                                tooltip="Editar",
                            ),
                            ft.Container(
                                content=ft.Icon(ft.Icons.DELETE, color=ft.Colors.RED_400, size=18),
                                padding=6, border_radius=6, ink=True,
                                on_click=lambda e, _sid=sid: self._confirm_delete(_sid),
                                tooltip="Eliminar",
                            ),
                        ], spacing=2)),
                    ],
                    color={ft.ControlState.HOVERED: tc["table_row_hover"]},
                ),
            )

        self._actualizar_pagination_controls()

    def _confirm_delete(self, situacion_id):
        tc = theme_colors(self.dark_mode)

        def cerrar(e):
            self.page.pop_dialog()

        def eliminar(e):
            self.page.pop_dialog()
            ok, err, msg = self.on_delete(situacion_id)
            if ok:
                self.load_data()
                self.page.snack_bar = ft.SnackBar(
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                        ft.Text(msg or "Eliminado correctamente", color=ft.Colors.WHITE),
                    ], spacing=10),
                    bgcolor=ft.Colors.GREEN_700,
                    duration=3000,
                    open=True,
                )
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Row([
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE, size=20),
                        ft.Text(err, color=ft.Colors.WHITE),
                    ], spacing=10),
                    bgcolor=ft.Colors.RED_700,
                    duration=4000,
                    open=True,
                )
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación", color=tc["text_primary"]),
            content=ft.Text("¿Está seguro? Esta acción no se puede deshacer.", color=tc["text_secondary"]),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar),
                ft.ElevatedButton("Eliminar", on_click=eliminar, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_700, shape=ft.RoundedRectangleBorder(radius=8))),
            ],
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=tc["bg_dialog"],
        )
        self.page.show_dialog(dlg)

    def _confirmar_resolver(self, situacion_id, nombre, ya_resuelto):
        if ya_resuelto == "Resuelto":
            return
        
        tc = theme_colors(self.dark_mode)

        def cerrar(e):
            self.page.pop_dialog()

        def resolver(e):
            self.page.pop_dialog()
            fecha_resolucion = datetime.now().strftime(FECHA_FORMAT)
            ok, err, msg = self.on_resolver(situacion_id, fecha_resolucion)
            if ok:
                self.load_data()
                self.page.snack_bar = ft.SnackBar(
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                        ft.Text(msg or "Situación resuelta correctamente", color=ft.Colors.WHITE),
                    ], spacing=10),
                    bgcolor=ft.Colors.GREEN_700,
                    duration=3000,
                    open=True,
                )
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Row([
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE, size=20),
                        ft.Text(err, color=ft.Colors.WHITE),
                    ], spacing=10),
                    bgcolor=ft.Colors.RED_700,
                    duration=4000,
                    open=True,
                )
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Resolver Situación", color=tc["text_primary"]),
            content=ft.Text(f"¿Confirmar que la situación de {nombre} ha sido resuelta?", color=tc["text_secondary"]),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar),
                ft.ElevatedButton("Confirmar", on_click=resolver, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700, shape=ft.RoundedRectangleBorder(radius=8))),
            ],
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=tc["bg_dialog"],
        )
        self.page.show_dialog(dlg)

    def load_data(self):
        self._show_loading(True)
        
        if self.personal_id:
            self.todos_los_registros = self.controller.obtener_por_personal(self.personal_id)
        else:
            self.todos_los_registros = self.controller.obtener_todos()
        self.registros_filtrados = list(self.todos_los_registros)
        self._actualizar_panel_info()
        self._rebuild_filter_panel()
        self._render_tabla()
        
        self._show_loading(False)

    def _rebuild_filter_panel(self):
        if hasattr(self, '_filter_panel'):
            self._tipos_situacion = self._get_unique_values("tipo_situacion")
            self._filter_panel._dropdowns.clear()
            self._filter_panel.add_dropdown("tipo", "Tipo de Situación", self._tipos_situacion)
            opciones_estado = ["Todos", "Activo", "Resuelto"]
            self._filter_panel.add_dropdown("estado", "Estado", opciones_estado)

    def _actualizar_panel_info(self):
        total = len(self.todos_los_registros)
        activas = sum(1 for s in self.todos_los_registros if s.get("estado", "Activo") == "Activo")
        resueltas = total - activas
        privados = sum(1 for s in self.todos_los_registros if s.get("tipo_situacion") == "Privado de libertad")
        desertores = sum(1 for s in self.todos_los_registros if s.get("tipo_situacion") == "Presunto desertor")

        self.stats_panel.actualizar({
            "activas": activas,
            "resueltas": resueltas,
            "privados": privados,
            "desertores": desertores,
        })
        
        self.panel_stats.visible = total > 0

    def _show_loading(self, show):
        if show:
            if not hasattr(self, '_loading_overlay') or not self._loading_overlay:
                self._loading_overlay = ft.Container(
                    content=self.loading_indicator,
                    alignment=ft.Alignment(0, 0),
                    bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
                    expand=True,
                )
            self._loading_overlay.visible = True
        else:
            if hasattr(self, '_loading_overlay'):
                self._loading_overlay.visible = False
        if hasattr(self, '_loading_overlay'):
            try:
                self._loading_overlay.update()
            except RuntimeError:
                pass

    def did_mount(self):
        self.load_data()