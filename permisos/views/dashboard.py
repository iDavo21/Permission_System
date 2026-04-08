import flet as ft
import asyncio
from datetime import datetime
from core.estado_utils import obtener_estado, fecha_a_datetime, obtener_estado_urgencia, contar_expiracion_proxima
from core.constants import FECHA_FORMAT, TIPOS_PERMISO, DIAS_EXPIRACION_PRONTO
from core.theme import theme_colors
from permisos.views.components import SummaryCards, PermisosTable, PaginationBar


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

        self._summary = SummaryCards(permisos=self.todos_los_permisos, dark_mode=self.dark_mode)

        self._table = PermisosTable(
            permisos=self.permisos_filtrados,
            on_edit=self.on_edit,
            on_delete_confirm=self._confirmar_eliminacion,
            on_view_detail=self.on_view_detail,
            dark_mode=self.dark_mode,
        )

        self._pagination = PaginationBar(
            on_change_page=self.cambiar_pagina,
            on_change_ppp=self.cambiar_registros_pagina,
            dark_mode=self.dark_mode,
        )

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
            content=ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=24),
            bgcolor=ft.Colors.GREEN_700,
            border_radius=16,
            padding=16,
            shadow=ft.BoxShadow(blur_radius=12, spread_radius=2, color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK)),
            ink=True,
            on_click=lambda e: self.on_add_permission() if self.on_add_permission else None,
            on_hover=self._on_fab_hover,
        )

        self.fab_tooltip = ft.Container(
            content=ft.Text("Agregar Permiso", size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=tc["bg_dialog"],
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=14, vertical=8),
            border=ft.border.all(1, ft.Colors.GREY_600),
            opacity=0,
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )

        self.fab_wrapper = ft.Container(
            content=ft.Row([
                self.fab_tooltip,
                ft.Container(width=8),
                self.btn_add,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            right=24,
            bottom=24,
        )

        self.lbl_count = ft.Text("Total: 0", size=13, color=tc["text_secondary"])
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
                        ft.Text("No hay permisos registrados", size=18, color=tc["empty_text"], weight=ft.FontWeight.W_500),
                        ft.Text("Haz clic en \"Agregar\" para registrar el primer permiso", size=13, color=tc["empty_subtext"]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
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
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=ft.padding.symmetric(horizontal=24, vertical=16),
                            bgcolor=tc["header_bg"],
                            border=ft.border.all(1, tc["header_border"]),
                            margin=ft.margin.only(left=24, right=24, top=16),
                        ),
                        ft.Container(height=12),
                        ft.Container(
                            content=self._summary,
                            margin=ft.margin.only(left=24, right=24),
                        ),
                        ft.Container(height=12),
                        ft.Stack([
                            self.content_area,
                            self.empty_state,
                        ], expand=True),
                    ],
                    expand=True,
                ),
                self._filter_panel_container,
                self.fab_wrapper,
            ],
            expand=True,
        )

    def _build_filter_panel(self, tc):
        self.filtro_tipo = ft.Dropdown(
            label="Tipo de Permiso",
            width=180,
            options=[ft.dropdown.Option("Todos")] + [ft.dropdown.Option(t) for t in self._get_tipos()],
            value="Todos",
            border_radius=10,
            filled=True,
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            color=tc["input_text"],
            label_style=ft.TextStyle(color=tc["input_label"]),
        )

        self.filtro_estado = ft.Dropdown(
            label="Estado",
            width=150,
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Activo"),
                ft.dropdown.Option("Por Expirar"),
                ft.dropdown.Option("Expirado"),
            ],
            value="Todos",
            border_radius=10,
            filled=True,
            bgcolor=tc["input_bg"],
            border_color=tc["input_border"],
            color=tc["input_text"],
            label_style=ft.TextStyle(color=tc["input_label"]),
        )

        self.btn_aplicar_filtros = ft.Container(
            content=ft.Text("Aplicar", color=ft.Colors.WHITE, size=13, weight=ft.FontWeight.BOLD),
            bgcolor=ft.Colors.GREEN_700,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ink=True,
            on_click=lambda e: self._aplicar_filtros(),
        )

        self.btn_limpiar_filtros = ft.Container(
            content=ft.Text("Limpiar", color=tc["text_secondary"], size=13),
            border=ft.border.all(1, tc["border_primary"]),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ink=True,
            on_click=lambda e: self._limpiar_filtros(),
        )

        self._filter_panel = ft.Container(
            content=ft.Column([
                ft.Text("Filtros", size=16, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Container(height=12),
                ft.Row([self.filtro_tipo, ft.Container(width=12), self.filtro_estado]),
                ft.Container(height=12),
                ft.Row([self.btn_aplicar_filtros, ft.Container(width=8), self.btn_limpiar_filtros]),
            ], spacing=0),
            bgcolor=tc["bg_dialog"],
            border=ft.border.all(1, tc["border_primary"]),
            border_radius=12,
            padding=16,
            width=400,
            shadow=ft.BoxShadow(blur_radius=20, spread_radius=2, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK)),
        )

        self._filter_panel_container = ft.Container(
            content=ft.Row([
                self._filter_panel,
            ], alignment=ft.MainAxisAlignment.END),
            padding=ft.padding.only(right=24),
            top=145,
            right=0,
            left=0,
            opacity=0,
            visible=False,
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )

    def _get_tipos(self):
        return sorted(set(p.get("tipo_permiso", "") for p in self.todos_los_permisos if p.get("tipo_permiso")) or TIPOS_PERMISO)

    def _on_fab_hover(self, e):
        self.fab_tooltip.opacity = 1.0 if e.data == "true" else 0.0
        self.update()

    def _toggle_filtros(self, e):
        self.filtros_abiertos = not self.filtros_abiertos
        self._filter_panel_container.visible = self.filtros_abiertos
        self._filter_panel_container.opacity = 1.0 if self.filtros_abiertos else 0.0
        self._filter_panel_container.update()

    def _aplicar_filtros(self):
        texto = (self.search_field.value or "").strip().lower()
        tipo = self.filtro_tipo.value
        estado = self.filtro_estado.value

        resultado = []
        for p in self.todos_los_permisos:
            if texto:
                nombre_completo = "%s %s" % (p.get("nombres", ""), p.get("apellidos", "")).lower()
                cedula = p.get("cedula", "").lower()
                if texto not in nombre_completo and texto not in cedula:
                    continue

            if tipo and tipo != "Todos":
                if p.get("tipo_permiso", "") != tipo:
                    continue

            if estado and estado != "Todos":
                estado_texto, _ = obtener_estado(p.get("fecha_hasta", ""))
                if estado_texto != estado:
                    continue

            resultado.append(p)

        self.permisos_filtrados = resultado
        self.pagina_actual = 1
        self.actualizar_tabla(resultado)
        self._toggle_filtros(None)

    def _limpiar_filtros(self):
        self.search_field.value = ""
        self.filtro_tipo.value = "Todos"
        self.filtro_estado.value = "Todos"
        self.permisos_filtrados = list(self.todos_los_permisos)
        self.pagina_actual = 1
        self.actualizar_tabla(self.todos_los_permisos)
        self._toggle_filtros(None)

    def _on_search(self, e):
        texto = self.search_field.value.strip().lower()
        if texto:
            resultado = [p for p in self.todos_los_permisos if 
                        texto in ("%s %s" % (p.get("nombres", ""), p.get("apellidos", ""))).lower() or 
                        texto in p.get("cedula", "").lower()]
        else:
            resultado = list(self.todos_los_permisos)
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

        self.lbl_count.value = "Total: %d" % total
        self._summary.actualizar(self.permisos_filtrados)

        self.tabla_container.visible = total_registros > 0
        self.content_area.visible = total_registros > 0
        self.empty_state.visible = total_registros == 0

        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

    def _confirmar_eliminacion(self, permiso_id):
        tc = theme_colors(self.dark_mode)

        def cerrar_dialogo(e):
            dialogo.open = False
            self.page.update()

        def eliminar_y_cerrar(e):
            if self.on_delete:
                self.on_delete(permiso_id)
            dialogo.open = False
            self.page.update()

        dialogo = ft.AlertDialog(
            title=ft.Text("Confirmar eliminacion", color=tc["text_primary"]),
            content=ft.Text("Esta accion no se puede deshacer.", color=tc["text_secondary"]),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.ElevatedButton("Eliminar", on_click=eliminar_y_cerrar, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_700, shape=ft.RoundedRectangleBorder(radius=8))),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=tc["bg_dialog"],
        )

        self.page.overlay.append(dialogo)
        dialogo.open = True
        self.page.update()

    def load_data(self):
        self.todos_los_permisos = self.todos_los_permisos
        self.permisos_filtrados = list(self.todos_los_permisos)
        self._summary.actualizar(self.todos_los_permisos)
        self.actualizar_tabla(self.todos_los_permisos)

    def did_mount(self):
        self.load_data()
        async def animate():
            await asyncio.sleep(0.05)
            self.opacity = 1
            self.update()
        asyncio.create_task(animate())
