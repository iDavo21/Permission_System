import flet as ft
import asyncio
from core.theme import theme_colors
from core.components.pagination import PaginationControl
from core.components.loading import LoadingIndicator
from core.components.filter_panel_base import FilterPanelBase, FilterPanelContainer
from core.components.stats_panel import StatsPanel


class DashboardBase(ft.Container):
    def __init__(self, controller=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.controller = controller
        self.dark_mode = dark_mode
        
        self.todos_los_registros = []
        self.registros_filtrados = []
        self.pagina_actual = 1
        self.registros_por_pagina = 10
        
        self.filtros_activos = {"texto": "", "tipo": "Todos", "estado": "Todos"}
        
        self.filtros_abiertos = False
        self._filter_panel = None
        
        self.loading_indicator = LoadingIndicator("Cargando...", dark_mode=self.dark_mode)
        self._loading_overlay = None
        
        self._build_base_ui()
    
    def _build_base_ui(self):
        tc = theme_colors(self.dark_mode)
        
        self.search_field = ft.TextField(
            hint_text="Buscar...",
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
        
        self.btn_add = self._create_add_button(tc)
        
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
        
        self.data_table = self._create_data_table(tc)
        
        self.tabla_container = ft.Container(
            content=self.data_table,
            border_radius=14,
            border=ft.border.all(1, tc["table_border"]),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            bgcolor=tc["bg_card"],
        )
        
        self._pagination = PaginationControl(
            on_change_page=self._cambiar_pagina,
            on_change_ppp=self._cambiar_registros_pagina,
            dark_mode=self.dark_mode,
        )
        
        self.content_area = ft.Column(
            controls=[],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        
        self.empty_state = self._create_empty_state(tc)
        
        self._filter_container = FilterPanelContainer(dark_mode=self.dark_mode)
    
    def _create_add_button(self, tc):
        return ft.Container(
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
            on_click=lambda e: self._on_add() if hasattr(self, '_on_add_callback') else None,
        )
    
    def _create_data_table(self, tc):
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("#", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=12)),
            ],
            rows=[],
            column_spacing=16,
            data_row_min_height=52,
            heading_row_color=tc["table_header_bg"],
            heading_row_height=44,
            border_radius=14,
            border=ft.border.all(1, tc["table_border"]),
        )
    
    def _create_empty_state(self, tc):
        return ft.Column(
            controls=[
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(ft.Icons.INBOX, size=64, color=tc["empty_icon"]),
                            bgcolor=tc["empty_icon_bg"],
                            border_radius=20,
                            padding=24,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(height=16),
                        ft.Text("No hay registros", size=20, color=tc["empty_text"], weight=ft.FontWeight.BOLD),
                        ft.Text("Los registros aparecerán aquí", size=14, color=tc["empty_subtext"]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(expand=True),
            ],
            expand=True,
            visible=False,
        )
    
    def set_add_callback(self, callback):
        self._on_add_callback = callback
    
    def set_filter_panel(self, fp):
        self._filter_panel = fp
        self._filter_container.set_filter_panel(fp)
    
    def get_filter_panel(self):
        return self._filter_panel
    
    def _toggle_filtros(self, e):
        self.filtros_abiertos = not self.filtros_abiertos
        if self.filtros_abiertos:
            self._filter_container.show()
        else:
            self._filter_container.hide()
    
    def _on_search(self, e):
        filtros = self.get_filter_panel().get_filtros() if self.get_filter_panel() else {}
        filtros["texto"] = self.search_field.value or ""
        self._aplicar_filtros(filtros)
    
    def _aplicar_filtros(self, filtros):
        self.filtros_activos = filtros
        self.registros_filtrados = self._filtrar_registros(filtros)
        self.pagina_actual = 1
        self._render_table()
    
    def _filtrar_registros(self, filtros):
        texto = filtros.get("texto", "").lower()
        tipo = filtros.get("tipo", "Todos")
        estado = filtros.get("estado", "Todos")
        
        resultado = []
        for r in self.todos_los_registros:
            if not self._match_texto(r, texto):
                continue
            if not self._match_tipo(r, tipo):
                continue
            if not self._match_estado(r, estado):
                continue
            resultado.append(r)
        return resultado
    
    def _match_texto(self, registro, texto):
        if not texto:
            return True
        nombres = registro.get("nombres", "")
        apellidos = registro.get("apellidos", "")
        if isinstance(nombres, tuple):
            nombres = " ".join(str(n) for n in nombres) if nombres else ""
        if isinstance(apellidos, tuple):
            apellidos = " ".join(str(a) for a in apellidos) if apellidos else ""
        nombre = "%s %s" % (nombres, apellidos)
        cedula = str(registro.get("cedula", "")).lower()
        return texto in nombre.lower() or texto in cedula
    
    def _match_tipo(self, registro, tipo):
        return True
    
    def _match_estado(self, registro, estado):
        return True
    
    def _cambiar_pagina(self, delta):
        total_paginas = max(1, (len(self.registros_filtrados) + self.registros_por_pagina - 1) // self.registros_por_pagina)
        nueva = self.pagina_actual + delta
        if 1 <= nueva <= total_paginas:
            self.pagina_actual = nueva
            self._render_table()
    
    def _cambiar_registros_pagina(self):
        self.registros_por_pagina = self._pagination.get_ppp()
        self.pagina_actual = 1
        self._render_table()
    
    def _render_table(self):
        tc = theme_colors(self.dark_mode)
        self.data_table.rows.clear()
        
        total = len(self.registros_filtrados)
        self.lbl_count.content.controls[1].value = str(total)
        
        total_paginas = max(1, (total + self.registros_por_pagina - 1) // self.registros_por_pagina)
        self.pagina_actual = max(1, min(self.pagina_actual, total_paginas))
        
        inicio = (self.pagina_actual - 1) * self.registros_por_pagina
        fin = inicio + self.registros_por_pagina
        pagina = self.registros_filtrados[inicio:fin]
        
        self._render_filas(pagina, inicio)
        
        self._pagination.actualizar(self.pagina_actual, total_paginas, total)
        
        self._actualizar_vistas(total)
    
    def _render_filas(self, pagina, inicio):
        pass
    
    def _actualizar_vistas(self, total):
        self.tabla_container.visible = total > 0
        self.content_area.visible = total > 0
        self.empty_state.visible = total == 0
        self._pagination.visible = total > 0
        try:
            self.update()
        except RuntimeError:
            pass
    
    def load_data(self):
        if self.controller:
            self.todos_los_registros = self.controller.obtener_todos()
        self.registros_filtrados = list(self.todos_los_registros)
        self._actualizar_stats()
        self._render_table()
    
    def _actualizar_stats(self):
        pass
    
    def _on_add(self, e):
        if hasattr(self, '_on_add_callback'):
            self._on_add_callback()
    
    def _show_loading(self, show):
        if show:
            if not self._loading_overlay:
                self._loading_overlay = ft.Container(
                    content=self.loading_indicator,
                    alignment=ft.Alignment(0, 0),
                    bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
                    expand=True,
                )
                if hasattr(self, 'content') and isinstance(self.content, ft.Stack):
                    self.content.controls.append(self._loading_overlay)
            self._loading_overlay.visible = True
        else:
            if self._loading_overlay:
                self._loading_overlay.visible = False
        try:
            self.update()
        except RuntimeError:
            pass
    
    def rebuild(self, dark_mode):
        self.dark_mode = dark_mode
        tc = theme_colors(dark_mode)
        
        self.search_field.bgcolor = tc["input_bg"]
        self.search_field.border_color = tc["input_border"]
        self.search_field.color = tc["input_text"]
        self.search_field.label_style = ft.TextStyle(color=tc["input_label"])
        
        if hasattr(self, 'btn_filter'):
            self.btn_filter.content.color = tc["text_secondary"]
        
        if self._filter_container:
            self._filter_container.dark_mode = dark_mode
        
        try:
            self.update()
        except RuntimeError:
            pass
    
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