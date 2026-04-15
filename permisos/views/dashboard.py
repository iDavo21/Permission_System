import flet as ft
import asyncio
from datetime import datetime
from core.estado_utils import obtener_estado, fecha_a_datetime, obtener_estado_urgencia, contar_expiracion_proxima
from core.constants import FECHA_FORMAT, TIPOS_PERMISO, DIAS_EXPIRACION_PRONTO
from core.theme import theme_colors
from core.components.pagination import PaginationControl
from core.components.loading import LoadingIndicator
from permisos.views.components import PermisosTable
from core.components.filter_panel_base import FilterPanelBase, FilterPanelContainer
from core.components.stats_panel import StatsPanel


class AdminView(ft.Container):
    def __init__(self, on_add_permission=None, lista_permisos=None, on_edit=None, on_delete=None, on_view_detail=None, on_export=None, on_backup=None, personal_id=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.personal_id = personal_id
        self.dark_mode = dark_mode

        self.on_add_permission = on_add_permission
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_view_detail = on_view_detail
        self._on_export = on_export
        self._on_backup = on_backup

        self.todos_los_permisos = lista_permisos or []
        self.permisos_filtrados = list(self.todos_los_permisos)

        self.pagina_actual = 1
        self.registros_por_pagina = 10

        self.filtros_abiertos = False

        tipos = sorted(set(p.get("tipo_permiso", "") for p in self.todos_los_permisos if p.get("tipo_permiso")) or TIPOS_PERMISO)

        self.stats_config = [
            {"key": "vigentes", "icon": ft.Icons.CHECK_CIRCLE, "value": "0", "label": "Permisos Vigentes", "accent": ft.Colors.GREEN_400},
            {"key": "por_expirar", "icon": ft.Icons.WARNING_AMBER_ROUNDED, "value": "0", "label": "Por Expirar", "accent": ft.Colors.AMBER_400},
            {"key": "expirados", "icon": ft.Icons.CANCEL_OUTLINED, "value": "0", "label": "Expirados", "accent": ft.Colors.RED_400},
        ]
        
        self.stats_panel = StatsPanel(
            cards_config=self.stats_config,
            dark_mode=self.dark_mode,
            spacing=16,
            margin=ft.margin.only(left=24, right=24)
        )

        self._table = PermisosTable(
            permisos=self.permisos_filtrados,
            on_edit=self.on_edit,
            on_delete_confirm=self._confirmar_eliminacion,
            on_view_detail=self.on_view_detail,
            dark_mode=self.dark_mode,
        )

        self._pagination = PaginationControl(
            on_change_page=self.cambiar_pagina,
            on_change_ppp=self.cambiar_registros_pagina,
            dark_mode=self.dark_mode,
        )

        self.panel_stats = self.stats_panel
        
        self.loading_indicator = LoadingIndicator("Cargando permisos...", dark_mode=self.dark_mode)

        self._build_ui()

        self.actualizar_tabla(self.permisos_filtrados)

    def _build_ui(self):
        tc = theme_colors(self.dark_mode)

        titulo_texto = "Permisos Registrados"
        if self.personal_id:
            for p in self.todos_los_permisos:
                nombre = "%s %s" % (p.get("nombres", ""), p.get("apellidos", ""))
                if nombre.strip():
                    titulo_texto = "Permisos de %s" % nombre
                    break

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
            on_click=lambda e: self.on_add_permission() if self.on_add_permission else None,
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
        self.lbl_status = ft.Text("", size=13, color=ft.Colors.RED_400)

        self.tabla_container = ft.Container(
            content=self._table,
            border_radius=14,
            border=ft.border.all(1, tc["table_border"]),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            bgcolor=tc["bg_card"],
        )

        self.content_area = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row([self.lbl_count, ft.Container(expand=True), self.lbl_status]),
                    margin=ft.margin.only(left=24, right=24, top=8),
                ),
                ft.Container(
                    content=self.tabla_container,
                    expand=True,
                    border_radius=14,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    margin=ft.margin.only(left=24, right=24, bottom=12),
                ),
                ft.Container(
                    content=self._pagination,
                    margin=ft.margin.only(left=24, right=24, bottom=16),
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        
        self.loading_indicator = LoadingIndicator("Cargando permisos...", dark_mode=self.dark_mode)

        self.empty_state = ft.Column(
            controls=[
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(ft.Icons.EVENT_NOTE_OUTLINED, size=64, color=tc["empty_icon"]),
                            bgcolor=tc["empty_icon_bg"],
                            border_radius=20,
                            padding=24,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(height=16),
                        ft.Text(
                            "No hay permisos registrados", 
                            size=20, 
                            color=tc["empty_text"], 
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            "Los permisos aparecerán aquí cuando se registren", 
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

        self._build_filter_panel(tc)

        self.content = ft.Stack(
            controls=[
                ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Row([
                                ft.Row([
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.EVENT_NOTE, color=ft.Colors.GREEN_400, size=28),
                                        bgcolor=tc["icon_bg"],
                                        border_radius=10,
                                        padding=10,
                                    ),
                                    ft.Column([
                                        ft.Text(titulo_texto, size=20, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                                        ft.Text("Gestiona los permisos del personal", size=12, color=tc["text_secondary"]),
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
                        self.panel_stats,
                        ft.Container(height=12),
                        ft.Stack([
                            self.content_area,
                            self.empty_state,
                        ], expand=True),
                    ],
                    expand=True,
                ),
                self._filter_container,
            ],
            expand=True,
        )

    def _build_filter_panel(self, tc):
        self._tipos_permiso = self._get_tipos()

        self._filter_panel = FilterPanelBase(
            on_apply=self._on_filter_apply,
            on_close=self._toggle_filtros,
            dark_mode=self.dark_mode,
            show_search=False,
            page_ref=None
        )
        
        self._filter_panel.add_dropdown("tipo", "Tipo de Permiso", self._tipos_permiso)
        
        opciones_estado = ["Todos", "Vigente", "Por Expirar", "Expirado"]
        self._filter_panel.add_dropdown("estado", "Estado", opciones_estado)
        
        self._filter_panel.add_date_field("fecha_desde", "Desde", page=None)
        self._filter_panel.add_date_field("fecha_hasta", "Hasta", page=None)
        
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
        for p in self.todos_los_permisos:
            if tipo and tipo != "Todos":
                if p.get("tipo_permiso", "") != tipo:
                    continue

            if estado and estado != "Todos":
                estado_texto, _ = obtener_estado(p.get("fecha_hasta", ""))
                if estado_texto != estado:
                    continue
            
            if fecha_desde or fecha_hasta:
                fecha_permiso = p.get("fecha_desde", "")
                if fecha_permiso:
                    if fecha_desde and fecha_permiso < fecha_desde:
                        continue
                    if fecha_hasta and fecha_permiso > fecha_hasta:
                        continue

            resultado.append(p)

        self.permisos_filtrados = resultado
        self.pagina_actual = 1
        self.actualizar_tabla(resultado)

    def _limpiar_filtros(self):
        self._filter_panel._limpiar()
        self.permisos_filtrados = list(self.todos_los_permisos)
        self.pagina_actual = 1
        self.actualizar_tabla(self.todos_los_permisos)

    def _get_tipos(self):
        return sorted(set(p.get("tipo_permiso", "") for p in self.todos_los_permisos if p.get("tipo_permiso")) or TIPOS_PERMISO)

    def _on_fab_hover(self, e):
        if self.page:
            self.fab_tooltip.opacity = 1.0 if e.data == "true" else 0.0
            try:
                self.update()
            except RuntimeError:
                pass

    def _toggle_filtros(self, e=None):
        self.filtros_abiertos = not self.filtros_abiertos
        if self.filtros_abiertos:
            self._filter_container.show()
        else:
            self._filter_container.hide()

    def _on_search(self, e):
        filtros = self._filter_panel.get_filtros() if self._filter_panel else {}
        filtros["texto"] = self.search_field.value or ""
        
        fecha_desde = filtros.get("fecha_desde", "").strip()
        fecha_hasta = filtros.get("fecha_hasta", "").strip()
        
        texto = self.search_field.value.strip().lower()
        tipo = filtros.get("tipo", "Todos")
        estado = filtros.get("estado", "Todos")
        
        resultado = []
        for p in self.todos_los_permisos:
            if texto:
                nombres = p.get("nombres", "")
                apellidos = p.get("apellidos", "")
                if isinstance(nombres, tuple):
                    nombres = " ".join(str(n) for n in nombres) if nombres else ""
                if isinstance(apellidos, tuple):
                    apellidos = " ".join(str(a) for a in apellidos) if apellidos else ""
                nombre_completo = ("%s %s" % (nombres, apellidos)).lower()
                cedula = str(p.get("cedula", "")).lower()
                if texto not in nombre_completo and texto not in cedula:
                    continue
            
            if tipo and tipo != "Todos":
                if p.get("tipo_permiso", "") != tipo:
                    continue

            if estado and estado != "Todos":
                estado_texto, _ = obtener_estado(p.get("fecha_hasta", ""))
                if estado_texto != estado:
                    continue
            
            if fecha_desde or fecha_hasta:
                fecha_permiso = p.get("fecha_desde", "")
                if fecha_permiso:
                    if fecha_desde and fecha_permiso < fecha_desde:
                        continue
                    if fecha_hasta and fecha_permiso > fecha_hasta:
                        continue
            
            resultado.append(p)
        
        self.permisos_filtrados = resultado
        self.pagina_actual = 1
        self.actualizar_tabla(resultado)

    def cambiar_pagina(self, delta):
        total_registros = len(self.permisos_filtrados)
        total_paginas = max(1, (total_registros + self.registros_por_pagina - 1) // self.registros_por_pagina)
        nueva_pagina = self.pagina_actual + delta
        if 1 <= nueva_pagina <= total_paginas:
            self.pagina_actual = nueva_pagina
        self.actualizar_tabla(self.permisos_filtrados)

    def cambiar_registros_pagina(self):
        self.registros_por_pagina = self._pagination.get_ppp()
        self.pagina_actual = 1
        self.actualizar_tabla(self.permisos_filtrados)

    def actualizar_tabla(self, permisos):
        total_registros = len(permisos)
        total_paginas = max(1, (total_registros + self.registros_por_pagina - 1) // self.registros_por_pagina)
        self.pagina_actual = max(1, min(self.pagina_actual, total_paginas))

        inicio = (self.pagina_actual - 1) * self.registros_por_pagina
        fin = inicio + self.registros_por_pagina
        pagina_permisos = permisos[inicio:fin]

        permisos_ordenados = self._table.get_sorted(pagina_permisos)
        filas = self._table.render_filas(permisos_ordenados, inicio)
        self._table.tabla.rows = filas

        self._pagination.actualizar(self.pagina_actual, total_paginas, total_registros)

        total = len(self.todos_los_permisos)

        self.lbl_count.content.controls[1].value = str(total)
        self._actualizar_stats()

        self.tabla_container.visible = total_registros > 0
        self.content_area.visible = total_registros > 0
        self.empty_state.visible = total_registros == 0

        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass
            
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

    def _confirmar_eliminacion(self, permiso_id):
        if self.on_delete:
            self.on_delete(permiso_id)

    def load_data(self):
        self.todos_los_permisos = self.todos_los_permisos
        self.permisos_filtrados = list(self.todos_los_permisos)
        self._rebuild_filter_panel()
        self._actualizar_stats()
        self.actualizar_tabla(self.todos_los_permisos)

    def _rebuild_filter_panel(self):
        if hasattr(self, 'filtro_tipo'):
            self.filtro_tipo.options = [ft.dropdown.Option("Todos")] + [ft.dropdown.Option(t) for t in self._get_tipos()]
            self.filtro_tipo.value = "Todos"
            self.filtro_estado.value = "Todos"
            self.filtro_tipo.update()
            self.filtro_estado.update()

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

    def _actualizar_stats(self):
        from core.estado_utils import obtener_estado
        vigentes = 0
        por_expirar = 0
        expirados = 0
        
        for p in self.todos_los_permisos:
            estado_texto, _ = obtener_estado(p.get("fecha_hasta", ""))
            if estado_texto == "Vigente":
                vigentes += 1
            elif estado_texto == "Por Expirar":
                por_expirar += 1
            elif estado_texto == "Expirado":
                expirados += 1
        
        self.stats_panel.actualizar({
            "vigentes": vigentes,
            "por_expirar": por_expirar,
            "expirados": expirados,
        })

    def _rebuild_filter_panel(self):
        if hasattr(self, '_filter_panel'):
            self._tipos_permiso = self._get_tipos()
            self._filter_panel._dropdowns.clear()
            self._filter_panel.add_dropdown("tipo", "Tipo de Permiso", self._tipos_permiso)
            opciones_estado = ["Todos", "Vigente", "Por Expirar", "Expirado"]
            self._filter_panel.add_dropdown("estado", "Estado", opciones_estado)
