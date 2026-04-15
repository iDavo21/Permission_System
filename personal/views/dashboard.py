import flet as ft
import asyncio
from core.theme import theme_colors
from core.constants import CEDULA_MIN, CEDULA_MAX, TELEFONO_MIN, TELEFONO_MAX
from core.components.loading import LoadingIndicator
from core.components.stats_panel import StatsPanel
from core.components.filter_panel_base import FilterPanelBase, FilterPanelContainer


class PersonalDashboard(ft.Container):
    def __init__(self, controller, on_navigate_permisos, on_navigate_comisiones, on_add_personal=None, on_edit_personal=None, on_delete_personal=None, lista_permisos=None, lista_comisiones=None, lista_situaciones=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.controller = controller
        self.on_navigate_permisos = on_navigate_permisos
        self.on_navigate_comisiones = on_navigate_comisiones
        self.on_add_personal = on_add_personal
        self.on_edit_personal = on_edit_personal
        self.on_delete_personal = on_delete_personal
        self.lista_permisos = lista_permisos or []
        self.lista_comisiones = lista_comisiones or []
        self.lista_situaciones = lista_situaciones or []
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
            hint_text="Buscar por nombre, cedula o grado...",
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
            on_click=self._on_add,
        )

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("#", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=12)),
                ft.DataColumn(ft.Text("Grado", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=12)),
                ft.DataColumn(ft.Text("Nombre Completo", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=12)),
                ft.DataColumn(ft.Text("Cédula", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=12)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=12)),
                ft.DataColumn(ft.Text("Teléfono", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=12)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=12)),
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
            {"key": "disponibles", "icon": ft.Icons.PEOPLE, "value": "0", "label": "Personal Disponible", "accent": ft.Colors.GREEN_400},
            {"key": "activos", "icon": ft.Icons.BADGE, "value": "0", "label": "Con Cargo Asignado", "accent": ft.Colors.CYAN_400},
            {"key": "grados", "icon": ft.Icons.MILITARY_TECH, "value": "0", "label": "Grados Distintos", "accent": ft.Colors.AMBER_400},
        ]
        
        self.stats_panel = StatsPanel(
            cards_config=self.stats_config,
            dark_mode=self.dark_mode,
            spacing=16,
            margin=ft.margin.only(left=24, right=24)
        )

        self.lbl_prev = ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, icon_color=tc["text_secondary"], on_click=lambda e: self._cambiar_pagina(-1))
        self.lbl_next = ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, icon_color=tc["text_secondary"], on_click=lambda e: self._cambiar_pagina(1))
        self.lbl_page_info = ft.Text("Página 1 de 1", size=13, color=tc["text_secondary"])

        self.content_area = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row([self.lbl_count, ft.Container(expand=True)]),
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
                    content=ft.Row([self.lbl_prev, self.lbl_page_info, self.lbl_next], alignment=ft.MainAxisAlignment.CENTER),
                    margin=ft.margin.only(left=24, right=24, bottom=16),
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        
        self.loading_indicator = LoadingIndicator("Cargando personal...", dark_mode=self.dark_mode)

        self.empty_state = ft.Column(
            controls=[
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=64, color=tc["empty_icon"]),
                            bgcolor=tc["empty_icon_bg"],
                            border_radius=20,
                            padding=24,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(height=16),
                        ft.Text(
                            "No hay personal registrado", 
                            size=20, 
                            color=tc["empty_text"], 
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            "El personal aparecerá aquí cuando se registre", 
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
                                        content=ft.Icon(ft.Icons.MILITARY_TECH, color=ft.Colors.GREEN_400, size=28),
                                        bgcolor=tc["icon_bg"],
                                        border_radius=10,
                                        padding=10,
                                    ),
                                    ft.Column([
                                        ft.Text("Control de Personal", size=20, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                                        ft.Text("Gestiona los miembros de la unidad", size=12, color=tc["text_secondary"]),
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
                        ft.Container(
                            content=self.stats_panel,
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
                self._filter_container,
            ],
            expand=True,
        )

    def _build_filter_panel(self, tc):
        self._tipos_grado = self._get_unique_values("grado_jerarquia")
        self._tipos_cargo = self._get_unique_values("cargo")

        self._filter_panel = FilterPanelBase(
            on_apply=self._on_filter_apply,
            on_close=self._toggle_filtros,
            dark_mode=self.dark_mode,
            show_search=False
        )
        
        self._filter_panel.add_dropdown("grado", "Grado", self._tipos_grado)
        self._filter_panel.add_dropdown("cargo", "Cargo", self._tipos_cargo)
        
        self._filter_container = FilterPanelContainer(
            filter_panel=self._filter_panel,
            dark_mode=self.dark_mode
        )

    def _on_filter_apply(self, filtros):
        texto = filtros.get("texto", "")
        grado = filtros.get("grado", "Todos")
        cargo = filtros.get("cargo", "Todos")

        resultado = []
        for p in self.todos_los_registros:
            # Filtro por texto (nombre o cedula)
            if texto:
                nombres = p.get("nombres", "")
                apellidos = p.get("apellidos", "")
                if isinstance(nombres, tuple):
                    nombres = " ".join(str(n) for n in nombres) if nombres else ""
                if isinstance(apellidos, tuple):
                    apellidos = " ".join(str(a) for a in apellidos) if apellidos else ""
                
                nombre_completo = "%s %s" % (nombres, apellidos)
                nombre_lower = nombre_completo.lower()
                cedula = str(p.get("cedula", "")).lower()
                
                if texto.lower() not in nombre_lower and texto not in cedula:
                    continue

            # Filtros por dropdown (grado y cargo)
            if grado and grado != "Todos":
                if p.get("grado_jerarquia", "") != grado:
                    continue

            if cargo and cargo != "Todos":
                if p.get("cargo", "") != cargo:
                    continue

            resultado.append(p)

        self.registros_filtrados = resultado
        self.pagina_actual = 1
        self._render_table()

    def _get_unique_values(self, field):
        valores = set()
        for p in self.todos_los_registros:
            val = p.get(field, "")
            if val:
                valores.add(val)
        return sorted(valores)

    def _on_fab_hover(self, e):
        if self.page:
            self.fab_tooltip.opacity = 1.0 if e.data == "true" else 0.0
            try:
                self.update()
            except RuntimeError:
                pass

    def _show_empty(self, show):
        self.empty_state.visible = show
        self.content_area.visible = not show
        
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
        self._render_table()
        self._toggle_filtros(None)

    def _on_search(self, e):
        texto = self.search_field.value or ""
        filtros = {"texto": texto}
        
        if hasattr(self, '_filter_panel'):
            filtros_grado = self._filter_panel.get_filtros()
            filtros["grado"] = filtros_grado.get("grado", "Todos")
            filtros["cargo"] = filtros_grado.get("cargo", "Todos")
        
        self._on_filter_apply(filtros)

    def _on_add(self, e):
        if self.on_add_personal:
            self.on_add_personal()

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

        cargos = set()
        grados = set()
        for p in self.todos_los_registros:
            if p.get("cargo"):
                cargos.add(p["cargo"])
            if p.get("grado_jerarquia"):
                grados.add(p["grado_jerarquia"])

        from core.estado_utils import obtener_estado
        permisos_activos_ids = set(p.get("personal_id") for p in self.lista_permisos if obtener_estado(p.get("fecha_hasta", ""))[0] in ("Vigente", "Por Expirar"))
        comisiones_activas_ids = set(c.get("personal_id") for c in self.lista_comisiones if not c.get("finalizada", 0))
        situaciones_activas_ids = set(s.get("personal_id") for s in self.lista_situaciones if s.get("estado", "Activo") == "Activo")
        
        ocupados_ids = permisos_activos_ids | comisiones_activas_ids | situaciones_activas_ids
        
        disponibles = sum(1 for p in self.todos_los_registros if p.get("id") not in ocupados_ids)

        self.stats_panel.actualizar({
            "disponibles": disponibles,
            "activos": len(cargos),
            "grados": len(grados),
        })

        for idx, p in enumerate(pagina, start=inicio + 1):
            nombre_completo = "%s %s" % (p.get("nombres", ""), p.get("apellidos", ""))
            
            from core.validators import obtener_estado_personal
            estado = obtener_estado_personal(
                p.get("id"),
                self.lista_permisos,
                self.lista_comisiones,
                self.lista_situaciones
            )
            
            estado_info = estado.get("info", "")
            estado_badge = ""
            estado_color = ft.Colors.GREEN_700
            estado_icono = ft.Icons.CHECK_CIRCLE
            
            if estado.get("estado") == "permiso":
                estado_badge = "Permiso"
                estado_color = ft.Colors.ORANGE_700
                estado_icono = ft.Icons.BEACH_ACCESS
            elif estado.get("estado") == "comision":
                estado_badge = "Comisión"
                estado_color = ft.Colors.BLUE_700
                estado_icono = ft.Icons.BUSINESS_CENTER
            elif estado.get("estado") == "situacion":
                estado_badge = "Situación"
                estado_color = ft.Colors.RED_700
                estado_icono = ft.Icons.WARNING
            else:
                estado_badge = "Disponible"
                estado_color = ft.Colors.GREEN_700
                estado_icono = ft.Icons.CHECK_CIRCLE
            
            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(idx), size=13, color=tc["table_row_text"])),
                        ft.DataCell(ft.Container(
                            content=ft.Text(p.get("grado_jerarquia", "—"), size=12, color=ft.Colors.AMBER_400),
                            bgcolor=tc["badge_amber"],
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        )),
                        ft.DataCell(ft.Text(nombre_completo, size=13, weight=ft.FontWeight.W_500, color=tc["table_name_text"])),
                        ft.DataCell(ft.Text(p.get("cedula", ""), size=13, color=tc["table_row_text"])),
                        ft.DataCell(ft.Container(
                            content=ft.Row([
                                ft.Icon(estado_icono, size=14, color=estado_color),
                                ft.Text(estado_badge, size=12, color=estado_color),
                            ], spacing=4),
                            bgcolor=ft.Colors.with_opacity(0.15, estado_color),
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )),
                        ft.DataCell(ft.Text(p.get("telefono", "—"), size=13, color=tc["table_row_text"])),
                        ft.DataCell(ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            icon_color=tc["text_secondary"],
                            items=[
                                ft.PopupMenuItem(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.EDIT, size=18, color=tc["text_primary"]),
                                        ft.Text("Editar", color=tc["text_primary"]),
                                    ], spacing=8),
                                    on_click=lambda e, pid=p["id"]: self._on_edit(e, pid),
                                ),
                                ft.PopupMenuItem(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.DELETE, size=18, color=ft.Colors.RED_400),
                                        ft.Text("Eliminar", color=ft.Colors.RED_400),
                                    ], spacing=8),
                                    on_click=lambda e, pid=p["id"]: self._on_delete(e, pid),
                                ),
                            ],
                        )),
                    ],
                    color={ft.ControlState.HOVERED: tc["table_row_hover"]},
                ),
            )

        self.lbl_page_info.value = "Página %d de %d" % (self.pagina_actual, total_paginas)
        self.lbl_prev.disabled = self.pagina_actual <= 1
        self.lbl_next.disabled = self.pagina_actual >= total_paginas

        self._show_empty(total == 0)
        try:
            self.update()
        except RuntimeError:
            pass

    def _cambiar_pagina(self, delta):
        total_paginas = max(1, (len(self.registros_filtrados) + self.registros_por_pagina - 1) // self.registros_por_pagina)
        nueva = self.pagina_actual + delta
        if 1 <= nueva <= total_paginas:
            self.pagina_actual = nueva
            self._render_table()

    def _on_edit(self, e, personal_id):
        if self.on_edit_personal:
            self.on_edit_personal(personal_id)
        else:
            persona = self.controller.obtener_por_id(personal_id)
            if persona:
                dlg = self._build_edit_dialog(persona)
                self.page.show_dialog(dlg)

    def _build_edit_dialog(self, persona):
        tc = theme_colors(self.dark_mode)
        txt_nombres = ft.TextField(label="Nombres", value=persona.get("nombres", ""), expand=True, border_radius=8, filled=True, bgcolor=tc["input_bg"], border_color=tc["input_border"], color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]))
        txt_apellidos = ft.TextField(label="Apellidos", value=persona.get("apellidos", ""), expand=True, border_radius=8, filled=True, bgcolor=tc["input_bg"], border_color=tc["input_border"], color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]))
        txt_cedula = ft.TextField(label="Cedula", value=persona.get("cedula", ""), border_radius=8, filled=True, bgcolor=tc["input_bg"], border_color=tc["input_border"], color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]), max_length=CEDULA_MAX, input_filter="number")
        txt_telefono = ft.TextField(label="Telefono", value=persona.get("telefono", ""), border_radius=8, filled=True, bgcolor=tc["input_bg"], border_color=tc["input_border"], color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]), max_length=TELEFONO_MAX, input_filter="number")
        txt_grado = ft.TextField(label="Grado Jerarquico", value=persona.get("grado_jerarquia", ""), border_radius=8, filled=True, bgcolor=tc["input_bg"], border_color=tc["input_border"], color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]))
        txt_cargo = ft.TextField(label="Cargo", value=persona.get("cargo", ""), expand=True, border_radius=8, filled=True, bgcolor=tc["input_bg"], border_color=tc["input_border"], color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]))
        txt_dir_dom = ft.TextField(label="Dir. Domiciliaria", value=persona.get("dir_domiciliaria", ""), expand=True, border_radius=8, filled=True, bgcolor=tc["input_bg"], border_color=tc["input_border"], color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]))
        txt_dir_eme = ft.TextField(label="Dir. Emergencia", value=persona.get("dir_emergencia", ""), expand=True, border_radius=8, filled=True, bgcolor=tc["input_bg"], border_color=tc["input_border"], color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]))

        lbl_error = ft.Text("", color=ft.Colors.RED_400, size=12, visible=False)

        def save_edit(e):
            lbl_error.visible = False
            lbl_error.update()

            cedula_val = txt_cedula.value or ""
            telefono_val = txt_telefono.value or ""

            if len(cedula_val) < CEDULA_MIN or len(cedula_val) > CEDULA_MAX:
                lbl_error.value = f"La cédula debe tener entre {CEDULA_MIN} y {CEDULA_MAX} dígitos"
                lbl_error.visible = True
                lbl_error.update()
                return

            if telefono_val and (len(telefono_val) < TELEFONO_MIN or len(telefono_val) > TELEFONO_MAX):
                lbl_error.value = f"El teléfono debe tener entre {TELEFONO_MIN} y {TELEFONO_MAX} dígitos"
                lbl_error.visible = True
                lbl_error.update()
                return

            datos = {
                "nombres": txt_nombres.value,
                "apellidos": txt_apellidos.value,
                "cedula": txt_cedula.value,
                "telefono": txt_telefono.value,
                "grado_jerarquia": txt_grado.value,
                "cargo": txt_cargo.value,
                "dir_domiciliaria": txt_dir_dom.value,
                "dir_emergencia": txt_dir_eme.value,
            }
            ok, err = self.controller.actualizar(persona["id"], datos)
            if ok:
                self.page.pop_dialog()
                self.page.snack_bar = ft.SnackBar(
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                        ft.Text("Actualizado correctamente", color=ft.Colors.WHITE),
                    ], spacing=10),
                    bgcolor=ft.Colors.GREEN_700,
                    duration=3000,
                    open=True,
                )
                self.load_data()
                self.page.update()
            else:
                lbl_error.value = err
                lbl_error.visible = True
                lbl_error.update()

        def cerrar_dialogo(e):
            self.page.pop_dialog()

        dlg_ref = [None]
        dlg_ref[0] = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Personal", weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
            content=ft.Container(
                width=550,
                content=ft.Column([
                    ft.Row([txt_nombres, txt_apellidos]),
                    ft.Row([txt_cedula, txt_telefono]),
                    ft.Row([txt_grado, txt_cargo]),
                    ft.Row([txt_dir_dom, txt_dir_eme]),
                    lbl_error,
                ], spacing=12, scroll=ft.ScrollMode.AUTO),
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.ElevatedButton("Guardar", on_click=save_edit, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700, shape=ft.RoundedRectangleBorder(radius=8))),
            ],
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=tc["bg_dialog"],
        )
        return dlg_ref[0]

    def _on_delete(self, e, personal_id):
        if self.on_delete_personal:
            self.on_delete_personal(personal_id)
        else:
            tc = theme_colors(self.dark_mode)

            def cerrar_dialogo(e):
                self.page.pop_dialog()

            def confirm_delete(e):
                self.page.pop_dialog()
                ok, err = self.controller.eliminar(personal_id)
                if ok:
                    self.page.snack_bar = ft.SnackBar(
                        ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                            ft.Text("Eliminado correctamente", color=ft.Colors.WHITE),
                        ], spacing=10),
                        bgcolor=ft.Colors.GREEN_700,
                        duration=3000,
                        open=True,
                    )
                    self.load_data()
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
                title=ft.Text("Confirmar eliminacion", weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                content=ft.Text("Esta seguro de eliminar este registro? Esta accion no se puede deshacer.", color=tc["text_secondary"]),
                actions=[
                    ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                    ft.ElevatedButton("Eliminar", on_click=confirm_delete, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_700, shape=ft.RoundedRectangleBorder(radius=8))),
                ],
                shape=ft.RoundedRectangleBorder(radius=16),
                bgcolor=tc["bg_dialog"],
            )
            self.page.show_dialog(dlg)

    def load_data(self):
        # Show loading state
        self._show_loading(True)
        
        # Simulate async data loading (replace with actual async call if needed)
        import asyncio
        async def load_data_async():
            datos = self.controller.obtener_todos()
            self.todos_los_registros = datos
            self.registros_filtrados = list(datos)
            self._render_table()
            self._show_loading(False)
        
        # For now, we'll do it synchronously but show loading briefly
        # In a real app, this would be truly async
        datos = self.controller.obtener_todos()
        self.todos_los_registros = datos
        self.registros_filtrados = list(datos)
        self._rebuild_filter_panel()
        self._render_table()
        self._show_loading(False)

    def _rebuild_filter_panel(self):
        if hasattr(self, '_filter_panel'):
            self._tipos_grado = self._get_unique_values("grado_jerarquia")
            self._tipos_cargo = self._get_unique_values("cargo")
            self._filter_panel._dropdowns.clear()
            self._filter_panel.add_dropdown("grado", "Grado", self._tipos_grado)
            self._filter_panel.add_dropdown("cargo", "Cargo", self._tipos_cargo)

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