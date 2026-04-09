import flet as ft
import asyncio
from datetime import datetime
from core.estado_utils import obtener_estado, fecha_a_datetime, contar_expiracion_proxima
from core.constants import FECHA_FORMAT, TIPOS_COMISION
from core.theme import theme_colors


class ComisionesDashboard(ft.Container):
    def __init__(self, controller, personal_id=None, on_back=None, on_add=None, on_edit=None, on_delete=None, on_view_detail=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.controller = controller
        self.personal_id = personal_id
        self.on_back = on_back
        self.on_add = on_add
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_view_detail = on_view_detail
        self.dark_mode = dark_mode

        self.todos = []
        self.filtrados = []
        self.pagina_actual = 1
        self.registros_por_pagina = 10

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

        self.btn_back = ft.Container(
            content=ft.Icon(ft.Icons.ARROW_BACK, color=tc["text_secondary"], size=22),
            padding=10,
            border_radius=10,
            ink=True,
            on_click=lambda e: self.on_back() if self.on_back else None,
        )

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("#", weight=ft.FontWeight.BOLD, size=12, color=tc["table_header"])),
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD, size=13, color=tc["table_header"])),
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD, size=13, color=tc["table_header"])),
                ft.DataColumn(ft.Text("Destino", weight=ft.FontWeight.BOLD, size=13, color=tc["table_header"])),
                ft.DataColumn(ft.Text("Inicio", weight=ft.FontWeight.BOLD, size=13, color=tc["table_header"])),
                ft.DataColumn(ft.Text("Vencimiento", weight=ft.FontWeight.BOLD, size=13, color=tc["table_header"])),
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
        self.lbl_count = ft.Text("Total: 0", size=13, color=tc["text_secondary"])

        self.mensaje_vacio = ft.Column(
            controls=[
                ft.Container(height=40),
                ft.Container(
                    content=ft.Icon(ft.Icons.BUSINESS_CENTER_OUTLINED, size=72, color=tc["empty_icon"]),
                    bgcolor=tc["empty_icon_bg"],
                    border_radius=20,
                    padding=24,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Text("No hay comisiones registradas.", color=tc["empty_text"], size=16, weight=ft.FontWeight.W_500),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            visible=False,
        )

        self.tabla_container = ft.Container(
            content=self.data_table,
            border_radius=14,
            border=ft.border.all(1, tc["table_border"]),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            bgcolor=tc["bg_card"],
        )

        self.lbl_prev = ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, icon_color=tc["text_secondary"], on_click=lambda e: self._cambiar_pagina(-1))
        self.lbl_next = ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, icon_color=tc["text_secondary"], on_click=lambda e: self._cambiar_pagina(1))
        self.lbl_page_info = ft.Text("Página 1 de 1", size=13, color=tc["text_secondary"])

        pagination_row = ft.Row([
            self.lbl_prev,
            self.lbl_page_info,
            self.lbl_next,
        ], alignment=ft.MainAxisAlignment.CENTER)

        self.content_area = ft.Column(
            controls=[
                ft.Row([self.lbl_count, ft.Container(expand=True)], margin=ft.margin.only(left=24, right=24)),
                ft.Container(content=self.tabla_container, margin=ft.margin.only(left=24, right=24, bottom=12)),
                ft.Container(content=pagination_row, margin=ft.margin.only(left=24, right=24, bottom=16)),
                self.mensaje_vacio,
            ],
            expand=True,
        )

        self.content = ft.Column(
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
                        ft.Container(width=12),
                        self.btn_add,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(horizontal=24, vertical=16),
                    bgcolor=tc["header_bg"],
                    border=ft.border.all(1, tc["header_border"]),
                    border_radius=14,
                    margin=ft.margin.only(left=24, right=24, top=16),
                ),
                ft.Container(height=16),
                ft.Stack([
                    self.content_area,
                    self.mensaje_vacio,
                ], expand=True),
            ],
            expand=True,
        )

    def _on_search(self, e):
        termino = self.search_field.value.strip().lower() if self.search_field.value else ""
        self._aplicar_filtros(termino)

    def _aplicar_filtros(self, termino=""):
        resultado = []
        for c in self.todos:
            if termino:
                nombre = "%s %s" % (c.get("nombres", ""), c.get("apellidos", "")).lower()
                cedula = c.get("cedula", "").lower()
                destino = (c.get("destino", "") or "").lower()
                if termino not in nombre and termino not in cedula and termino not in destino:
                    continue
            resultado.append(c)
        self.filtrados = resultado
        self.pagina_actual = 1
        self._render_tabla()

    def _render_tabla(self):
        tc = theme_colors(self.dark_mode)
        self.data_table.rows.clear()
        total = len(self.filtrados)
        self.lbl_count.value = "Total: %d" % total

        total_paginas = max(1, (total + self.registros_por_pagina - 1) // self.registros_por_pagina)
        self.pagina_actual = max(1, min(self.pagina_actual, total_paginas))

        inicio = (self.pagina_actual - 1) * self.registros_por_pagina
        fin = inicio + self.registros_por_pagina
        pagina = self.filtrados[inicio:fin]

        for i, c in enumerate(pagina):
            num = inicio + i + 1
            nombre = "%s %s" % (c.get("nombres", ""), c.get("apellidos", ""))
            estado_texto, estado_color = obtener_estado(c.get("fecha_hasta", ""))
            cid = c.get("id")

            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(num), size=12, color=tc["text_tertiary"])),
                        ft.DataCell(ft.Text(nombre, size=13, color=tc["table_name_text"], weight=ft.FontWeight.W_500)),
                        ft.DataCell(ft.Container(
                            content=ft.Text(c.get("tipo_comision", ""), size=12, color=ft.Colors.CYAN_400),
                            bgcolor=tc["badge_cyan"], border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )),
                        ft.DataCell(ft.Text(c.get("destino", "—"), size=13, color=tc["table_row_text"])),
                        ft.DataCell(ft.Text(c.get("fecha_desde", ""), size=13, color=tc["table_row_text"])),
                        ft.DataCell(ft.Text(c.get("fecha_hasta", ""), size=13, color=tc["table_row_text"])),
                        ft.DataCell(ft.Container(
                            content=ft.Text(estado_texto, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            bgcolor=estado_color, border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )),
                        ft.DataCell(ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.EDIT, color=tc["text_secondary"], size=18),
                                padding=6, border_radius=6, ink=True,
                                on_click=lambda e, _cid=cid: self.on_edit(_cid) if self.on_edit else None,
                                tooltip="Editar",
                            ),
                            ft.Container(
                                content=ft.Icon(ft.Icons.VISIBILITY, color=ft.Colors.GREEN_400, size=18),
                                padding=6, border_radius=6, ink=True,
                                on_click=lambda e, _cid=cid: self.on_view_detail(_cid) if self.on_view_detail else None,
                                tooltip="Ver",
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

        self.lbl_page_info.value = "Página %d de %d" % (self.pagina_actual, total_paginas)
        self.lbl_prev.disabled = self.pagina_actual <= 1
        self.lbl_next.disabled = self.pagina_actual >= total_paginas
        self.tabla_container.visible = total > 0
        self.mensaje_vacio.visible = total == 0
        self.update()

    def _cambiar_pagina(self, delta):
        total_paginas = max(1, (len(self.filtrados) + self.registros_por_pagina - 1) // self.registros_por_pagina)
        nueva = self.pagina_actual + delta
        if 1 <= nueva <= total_paginas:
            self.pagina_actual = nueva
            self._render_tabla()

    def _confirm_delete(self, comision_id):
        tc = theme_colors(self.dark_mode)

        def cerrar(e):
            self.page.pop_dialog()

        def eliminar(e):
            self.page.pop_dialog()
            ok, err = self.controller.eliminar(comision_id)
            if ok:
                self.load_data()
                self.page.snack_bar = ft.SnackBar(
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                        ft.Text("Eliminado correctamente", color=ft.Colors.WHITE),
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

    def load_data(self):
        if self.personal_id:
            self.todos = self.controller.obtener_por_personal(self.personal_id)
        else:
            self.todos = self.controller.obtener_todos()
        self.filtrados = list(self.todos)
        self._render_tabla()

    def did_mount(self):
        self.load_data()
        async def animate():
            await asyncio.sleep(0.05)
            self.opacity = 1
            self.update()
        asyncio.create_task(animate())
