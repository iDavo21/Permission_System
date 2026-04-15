import flet as ft
import asyncio
from datetime import datetime
from core.estado_utils import obtener_estado, fecha_a_datetime, contar_expiracion_proxima
from core.constants import FECHA_FORMAT, TIPOS_COMISION
from core.theme import theme_colors
from core.components.loading import LoadingIndicator
from core.components.pagination import PaginationControl
from core.components.filter_panel_base import FilterPanelBase, FilterPanelContainer
from core.components.stats_panel import StatsPanel


class ComisionesDashboard(ft.Container):
    def __init__(self, controller, personal_id=None, on_back=None, on_add=None, on_edit=None, on_delete=None, on_view_detail=None, on_finalizar=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.controller = controller
        self.personal_id = personal_id
        self.on_back = on_back
        self.on_add = on_add
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_view_detail = on_view_detail
        self.on_finalizar = on_finalizar
        self.dark_mode = dark_mode

        self.todos_los_registros = []
        self.registros_filtrados = []
        self.pagina_actual = 1
        self.registros_por_pagina = 10

        self.filtros_abiertos = False

        self._build_ui()

    def _build_ui(self):
        tc = theme_colors(self.dark_mode)

        self.search_field = ft.TextField(
            hint_text="Buscar por nombre, cedula o destino...",
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
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )

        self.btn_filter = ft.Container(
            content=ft.Icon(ft.Icons.FILTER_LIST, color=tc["text_secondary"], size=22),
            padding=10,
            border_radius=10,
            ink=True,
            on_click=self._toggle_filtros,
        )

        self.btn_add = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=20),
                ft.Text("Nueva", color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.CENTER_LEFT,
                end=ft.Alignment.CENTER_RIGHT,
                colors=["#1b5e20", "#2e7d32"],
            ),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            ink=True,
            on_click=lambda e: self.on_add() if self.on_add else None,
        )

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("#", weight=ft.FontWeight.BOLD, size=12, color=tc["table_header"])),
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD, size=13, color=tc["table_header"])),
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD, size=13, color=tc["table_header"])),
                ft.DataColumn(ft.Text("Destino", weight=ft.FontWeight.BOLD, size=13, color=tc["table_header"])),
                ft.DataColumn(ft.Text("Desde", weight=ft.FontWeight.BOLD, size=13, color=tc["table_header"])),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD, size=13, color=tc["table_header"])),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, size=13, color=tc["table_header"])),
            ],
            rows=[],
            column_spacing=16,
            heading_row_color=tc["table_header_bg"],
            heading_row_height=50,
            data_row_min_height=48,
            border_radius=12,
            border=ft.border.all(1, tc["table_border"]),
        )

        self.lbl_titulo = ft.Text("Comisiones", size=20, weight=ft.FontWeight.BOLD, color=tc["text_primary"])
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
            {"key": "activas", "icon": ft.Icons.PLAY_ARROW, "value": "0", "label": "Comisión Activa", "accent": ft.Colors.ORANGE_400},
            {"key": "finalizadas", "icon": ft.Icons.CHECK_CIRCLE, "value": "0", "label": "Comisiones Finalizadas", "accent": ft.Colors.GREEN_400},
            {"key": "por_salir", "icon": ft.Icons.SCHEDULE, "value": "0", "label": "Por Salir", "accent": ft.Colors.CYAN_400},
        ]
        
        self.stats_panel = StatsPanel(
            cards_config=self.stats_config,
            dark_mode=self.dark_mode,
            spacing=16,
            margin=ft.margin.only(left=24, right=24, bottom=12)
        )
        
        self.panel_stats = self.stats_panel

        self.mensaje_vacio = ft.Column(
            controls=[
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(ft.Icons.BUSINESS_CENTER_OUTLINED, size=72, color=tc["empty_icon"]),
                            bgcolor=tc["empty_icon_bg"],
                            border_radius=20,
                            padding=24,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(height=16),
                        ft.Text(
                            "No hay comisiones registradas.", 
                            size=20, 
                            color=tc["empty_text"], 
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            "Las comisiones aparecerán aquí cuando se registren", 
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

        self.tabla_container = ft.Container(
            content=self.data_table,
            border_radius=14,
            border=ft.border.all(1, tc["table_border"]),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            bgcolor=tc["bg_card"],
        )

        self.lbl_prev = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            icon_color=tc["text_secondary"],
            icon_size=20,
            on_click=lambda e: self._cambiar_pagina(-1),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )
        self.lbl_next = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            icon_color=tc["text_secondary"],
            icon_size=20,
            on_click=lambda e: self._cambiar_pagina(1),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )
        self.lbl_page_info = ft.Text("Pagina 1 de 1", size=13, color=tc["text_secondary"])

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
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            text_style=ft.TextStyle(color=tc["input_text"]),
            on_select=lambda e: self._cambiar_registros_pagina(),
            border=ft.InputBorder.OUTLINE,
            border_radius=8,
        )

        pagination_row = ft.Container(
            content=ft.Row([
                ft.Text("Mostrar", size=12, color=tc["text_secondary"]),
                self.dropdown_ppp,
                ft.Text("por pagina", size=12, color=tc["text_secondary"]),
                ft.Container(width=24),
                self.lbl_prev,
                self.lbl_page_info,
                self.lbl_next,
            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
            bgcolor=tc["bg_card"],
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            border=ft.border.all(1, tc["border_primary"]),
            margin=ft.margin.only(left=24, right=24, bottom=16),
            visible=False,
        )
        self.pagination_row = pagination_row

        self.content_area = ft.Column(
            controls=[
                self.panel_stats,
                ft.Row([self.lbl_count, ft.Container(expand=True)], margin=ft.margin.only(left=24, right=24)),
                ft.Container(content=self.tabla_container, margin=ft.margin.only(left=24, right=24, bottom=12)),
                self.pagination_row,
            ],
            expand=True,
        )
        
        self.loading_indicator = LoadingIndicator("Cargando comisiones...", dark_mode=self.dark_mode)

        self._build_filter_panel(tc)

        self.content = ft.Stack(
            controls=[
                ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Row([
                                ft.Row([
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.BUSINESS_CENTER, color=ft.Colors.GREEN_400, size=26),
                                        bgcolor=tc["icon_bg"],
                                        border_radius=10,
                                        padding=10,
                                    ),
                                    ft.Column([
                                        ft.Text("Control de Comisiones", size=20, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                                        ft.Text("Gestiona las comisiones del personal", size=12, color=tc["text_secondary"]),
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
                            margin=ft.margin.only(left=24, right=24, top=16),
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

    def _build_filter_panel(self, tc):
        self._tipos_comision = self._get_unique_values("tipo_comision")

        self._filter_panel = FilterPanelBase(
            on_apply=self._on_filter_apply,
            on_close=self._toggle_filtros,
            dark_mode=self.dark_mode,
            show_search=False
        )
        
        self._filter_panel.add_dropdown("tipo", "Tipo de Comisión", self._tipos_comision)
        
        opciones_estado = ["Todos", "Por Salir", "Activa", "Finalizada"]
        self._filter_panel.add_dropdown("estado", "Estado", opciones_estado)
        
        self._filter_panel.add_date_field("fecha_desde", "Desde")
        self._filter_panel.add_date_field("fecha_hasta", "Hasta")
        
        self._filter_container = FilterPanelContainer(
            filter_panel=self._filter_panel,
            dark_mode=self.dark_mode
        )

    def _on_filter_apply(self, filtros):
        tipo = filtros.get("tipo", "Todos")
        estado = filtros.get("estado", "Todos")
        fecha_desde = filtros.get("fecha_desde", "").strip()
        fecha_hasta = filtros.get("fecha_hasta", "").strip()

        resultado = []
        for c in self.todos_los_registros:
            if tipo and tipo != "Todos":
                if c.get("tipo_comision", "") != tipo:
                    continue

            if estado and estado != "Todos":
                from datetime import datetime
                finalizada = c.get("finalizada", 0)
                fecha_salida = c.get("fecha_salida", "")
                hoy = datetime.now().strftime(FECHA_FORMAT)
                
                if finalizada:
                    estado_texto = "Finalizada"
                elif fecha_salida and fecha_salida > hoy:
                    estado_texto = "Por Salir"
                else:
                    estado_texto = "Activa"
                    
                if estado_texto != estado:
                    continue
            
            if fecha_desde or fecha_hasta:
                fecha_comision = c.get("fecha_salida", "")
                if fecha_comision:
                    if fecha_desde and fecha_comision < fecha_desde:
                        continue
                    if fecha_hasta and fecha_comision > fecha_hasta:
                        continue

            resultado.append(c)

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

    def _get_unique_values(self, field):
        valores = set()
        for c in self.todos_los_registros:
            val = c.get(field, "")
            if val:
                valores.add(val)
        return sorted(valores)

    def _toggle_filtros(self, e=None):
        self.filtros_abiertos = not self.filtros_abiertos
        if self.filtros_abiertos:
            self._filter_container.show()
        else:
            self._filter_container.hide()

    def _limpiar_filtros(self):
        self._filter_panel._limpiar()
        self.registros_filtrados = list(self.todos_los_registros)
        self.pagina_actual = 1
        self._render_tabla()
        self._toggle_filtros(None)

    def _on_search(self, e):
        filtros = self._filter_panel.get_filtros() if self._filter_panel else {}
        filtros["texto"] = self.search_field.value or ""
        self._on_filter_apply(filtros)
        
        texto = self.search_field.value.strip().lower()
        
        if not texto:
            return
        
        resultado = []
        for c in self.registros_filtrados:
            nombres = c.get("nombres", "")
            apellidos = c.get("apellidos", "")
            if isinstance(nombres, tuple):
                nombres = " ".join(str(n) for n in nombres) if nombres else ""
            if isinstance(apellidos, tuple):
                apellidos = " ".join(str(a) for a in apellidos) if apellidos else ""
            
            nombre_completo = ("%s %s" % (nombres, apellidos)).lower()
            cedula = str(c.get("cedula", "")).lower()
            
            if texto in nombre_completo or texto in cedula:
                resultado.append(c)
        
        self.registros_filtrados = resultado
        self.pagina_actual = 1
        self._render_tabla()

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

        for i, c in enumerate(pagina):
            num = inicio + i + 1
            nombre = "%s %s" % (c.get("nombres", ""), c.get("apellidos", ""))
            finalizada = c.get("finalizada", 0)
            from core.constants import FECHA_FORMAT
            fecha_salida = c.get("fecha_salida", "")
            from datetime import datetime
            hoy = datetime.now().strftime(FECHA_FORMAT)
            
            if finalizada:
                estado_texto = "Finalizada"
                estado_color = ft.Colors.GREEN_700
            elif fecha_salida and fecha_salida > hoy:
                estado_texto = "Por Salir"
                estado_color = ft.Colors.AMBER_700
            else:
                estado_texto = "Activa"
                estado_color = ft.Colors.ORANGE_700
            cid = c.get("id")

            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(num), size=12, color=tc["text_tertiary"])),
                        ft.DataCell(ft.GestureDetector(
                            content=ft.Text(nombre, size=14, color=ft.Colors.CYAN_400, weight=ft.FontWeight.W_500),
                            on_tap=lambda e, _cid=cid: self.on_view_detail(_cid) if self.on_view_detail else None,
                            mouse_cursor=ft.MouseCursor.CLICK,
                        )),
                        ft.DataCell(ft.Container(
                            content=ft.Text(c.get("tipo_comision", ""), size=12, color=ft.Colors.CYAN_400),
                            bgcolor=tc["badge_cyan"], border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )),
                        ft.DataCell(ft.Text(c.get("destino", "—"), size=13, color=tc["table_row_text"])),
                        ft.DataCell(ft.Text(c.get("fecha_salida", ""), size=13, color=tc["table_row_text"])),
                        ft.DataCell(ft.Container(
                            content=ft.Text(estado_texto, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            bgcolor=estado_color, border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )),
                        ft.DataCell(ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400 if not finalizada else tc["text_tertiary"], size=18),
                                padding=6, border_radius=6, ink=True,
                                on_click=lambda e, _cid=cid, _nombre=nombre, _finalizada=finalizada: self._confirmar_finalizar(_cid, _nombre, _finalizada) if self.on_finalizar and not _finalizada else None,
                                tooltip="Finalizar" if not finalizada else "Finalizada",
                            ),
                            ft.Container(
                                content=ft.Icon(ft.Icons.EDIT, color=tc["text_secondary"], size=18),
                                padding=6, border_radius=6, ink=True,
                                on_click=lambda e, _cid=cid: self.on_edit(_cid) if self.on_edit else None,
                                tooltip="Editar",
                            ),
                            ft.Container(
                                content=ft.Icon(ft.Icons.DELETE, color=ft.Colors.RED_400, size=18),
                                padding=6, border_radius=6, ink=True,
                                on_click=lambda e, _cid=cid: self._confirm_delete(_cid),
                                tooltip="Eliminar",
                            ),
                        ], spacing=2)),
                    ],
                    color={ft.ControlState.HOVERED: tc["table_row_hover"]},
                ),
            )

        self.lbl_page_info.value = "Pagina %d de %d" % (self.pagina_actual, total_paginas)
        self.lbl_prev.disabled = self.pagina_actual <= 1
        self.lbl_next.disabled = self.pagina_actual >= total_paginas
        self.tabla_container.visible = total > 0
        self.mensaje_vacio.visible = total == 0
        self.pagination_row.visible = total > 0
        try:
            self.update()
        except RuntimeError:
            pass

    def _cambiar_pagina(self, delta):
        total_paginas = max(1, (len(self.registros_filtrados) + self.registros_por_pagina - 1) // self.registros_por_pagina)
        nueva = self.pagina_actual + delta
        if 1 <= nueva <= total_paginas:
            self.pagina_actual = nueva
            self._render_tabla()

    def _cambiar_registros_pagina(self):
        self.registros_por_pagina = int(self.dropdown_ppp.value)
        self.pagina_actual = 1
        self._render_tabla()

    def _confirm_delete(self, comision_id):
        tc = theme_colors(self.dark_mode)

        def cerrar(e):
            self.page.pop_dialog()

        def eliminar(e):
            self.page.pop_dialog()
            ok, err, msg = self.controller.eliminar(comision_id)
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

    def _confirmar_finalizar(self, comision_id, nombre, ya_finalizada):
        if ya_finalizada:
            return
        
        tc = theme_colors(self.dark_mode)

        def cerrar(e):
            self.page.pop_dialog()

        def finalizar(e):
            self.page.pop_dialog()
            ok, err, msg = self.controller.finalizar(comision_id)
            if ok:
                self.load_data()
                self.page.snack_bar = ft.SnackBar(
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                        ft.Text(msg or "Comisión finalizada correctamente", color=ft.Colors.WHITE),
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
            title=ft.Text("Finalizar Comisión", color=tc["text_primary"]),
            content=ft.Text(f"¿Confirmar que {nombre} ha finalizado su comisión y ha retornado?", color=tc["text_secondary"]),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar),
                ft.ElevatedButton("Confirmar", on_click=finalizar, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700, shape=ft.RoundedRectangleBorder(radius=8))),
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
            self._tipos_comision = self._get_unique_values("tipo_comision")
            self._filter_panel._dropdowns.clear()
            self._filter_panel.add_dropdown("tipo", "Tipo de Comisión", self._tipos_comision)
            opciones_estado = ["Todos", "Por Salir", "Activa", "Finalizada"]
            self._filter_panel.add_dropdown("estado", "Estado", opciones_estado)

    def _actualizar_panel_info(self):
        from core.constants import FECHA_FORMAT
        from datetime import datetime
        total = len(self.todos_los_registros)
        
        hoy = datetime.now().strftime(FECHA_FORMAT)
        por_salir = sum(1 for c in self.todos_los_registros 
                        if not c.get("finalizada", 0) 
                        and c.get("fecha_salida", "") > hoy)
        activas = sum(1 for c in self.todos_los_registros if not c.get("finalizada", 0) and c.get("fecha_salida", "") <= hoy)
        finalizadas = total - por_salir - activas

        self.stats_panel.actualizar({
            "activas": activas,
            "finalizadas": finalizadas,
            "por_salir": por_salir,
        })
        
        self.panel_stats.visible = total > 0
        
    def _show_loading(self, show):
        # For simplicity, we'll overlay the loading indicator
        # In a more complex implementation, we might modify the UI structure
        if show:
            if not hasattr(self, '_loading_overlay') or not self._loading_overlay:
                self._loading_overlay = ft.Container(
                    content=self.loading_indicator,
                    alignment=ft.Alignment(0, 0),
                    bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
                    expand=True,
                )
                # Add to the stack
                if len(self.content.controls) < 3:  # Not already added
                    self.content.controls.append(self._loading_overlay)
            self._loading_overlay.visible = True
        else:
            if hasattr(self, '_loading_overlay') and self._loading_overlay:
                self._loading_overlay.visible = False
        try:
            self.update()
        except RuntimeError:
            pass

    def did_mount(self):
        self.load_data()
        if hasattr(self, '_filter_container'):
            self._filter_container.set_page(self.page)
        async def animate():
            await asyncio.sleep(0.05)
            self.opacity = 1
            try:
                self.update()
            except RuntimeError:
                pass
        asyncio.create_task(animate())