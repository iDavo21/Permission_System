import flet as ft
import asyncio
from core.theme import theme_colors


class PersonalDashboard(ft.Container):
    def __init__(self, controller, on_navigate_permisos, on_navigate_comisiones, on_add_personal=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.controller = controller
        self.on_navigate_permisos = on_navigate_permisos
        self.on_navigate_comisiones = on_navigate_comisiones
        self.on_add_personal = on_add_personal
        self.dark_mode = dark_mode

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

        self.btn_add = ft.Container(
            content=ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=24),
            bgcolor=ft.Colors.GREEN_700,
            border_radius=16,
            padding=16,
            shadow=ft.BoxShadow(blur_radius=12, spread_radius=2, color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK)),
            ink=True,
            on_click=self._on_add,
            on_hover=self._on_fab_hover,
        )

        self.fab_tooltip = ft.Container(
            content=ft.Text("Agregar Personal", size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
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

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("#", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=12)),
                ft.DataColumn(ft.Text("Nombre Completo", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=12)),
                ft.DataColumn(ft.Text("Cedula", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=12)),
                ft.DataColumn(ft.Text("Grado", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=12)),
                ft.DataColumn(ft.Text("Cargo", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=12)),
                ft.DataColumn(ft.Text("Telefono", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=12)),
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

        self.lbl_count = ft.Text("Total: 0", size=13, color=tc["text_secondary"])
        self.lbl_status = ft.Text("", size=13, color=ft.Colors.RED_400)

        self.stat_total = self._stat_card(ft.Icons.PEOPLE, "0", "Personal Registrado", ft.Colors.GREEN_400)
        self.stat_activos = self._stat_card(ft.Icons.BADGE, "0", "Con Cargo Asignado", ft.Colors.CYAN_400)
        self.stat_grados = self._stat_card(ft.Icons.MILITARY_TECH, "0", "Grados Distintos", ft.Colors.AMBER_400)

        self.content_area = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row([self.lbl_count, ft.Container(expand=True), self.lbl_status]),
                    margin=ft.margin.only(left=24, right=24, top=8),
                ),
                ft.Container(
                    content=self.data_table,
                    expand=True,
                    border_radius=14,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
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
                            content=ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=64, color=tc["empty_icon"]),
                            bgcolor=tc["empty_icon_bg"],
                            border_radius=20,
                            padding=24,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(height=16),
                        ft.Text("No hay personal registrado", size=18, color=tc["empty_text"], weight=ft.FontWeight.W_500),
                        ft.Text("Haz clic en \"Agregar\" para registrar al primer miembro", size=13, color=tc["empty_subtext"]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(expand=True),
            ],
            expand=True,
            visible=False,
        )

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
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=ft.padding.symmetric(horizontal=24, vertical=16),
                            bgcolor=tc["header_bg"],
                            border=ft.border.all(1, tc["header_border"]),
                            margin=ft.margin.only(left=24, right=24, top=16),
                        ),
                        ft.Container(height=12),
                        ft.Container(
                            content=ft.Row([
                                self.stat_total,
                                self.stat_activos,
                                self.stat_grados,
                            ], spacing=16),
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
                self.fab_wrapper,
            ],
            expand=True,
        )

    def _stat_card(self, icon, value, label, accent):
        tc = theme_colors(self.dark_mode)
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=20, color=accent),
                    ft.Container(expand=True),
                ]),
                ft.Text(value, size=26, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                ft.Text(label, size=11, color=tc["text_secondary"]),
            ], spacing=4),
            bgcolor=tc["stat_bg"],
            border_radius=14,
            padding=ft.padding.symmetric(vertical=20, horizontal=22),
            expand=True,
            border=ft.border.all(1, tc["stat_border"]),
        )

    def _on_fab_hover(self, e):
        self.fab_tooltip.opacity = 1.0 if e.data == "true" else 0.0
        self.update()

    def _show_empty(self, show):
        self.empty_state.visible = show
        self.content_area.visible = not show

    def _on_search(self, e):
        termino = self.search_field.value.strip()
        if termino:
            results = self.controller.buscar(termino)
        else:
            results = self.controller.obtener_todos()
        self._render_table(results)

    def _on_add(self, e):
        if self.on_add_personal:
            self.on_add_personal()

    def _render_table(self, datos):
        tc = theme_colors(self.dark_mode)
        self.data_table.rows.clear()
        total = len(datos)
        self.lbl_count.value = "Total: %d" % total

        cargos = set()
        grados = set()
        for p in datos:
            if p.get("cargo"):
                cargos.add(p["cargo"])
            if p.get("grado_jerarquia"):
                grados.add(p["grado_jerarquia"])

        self.stat_total.content.controls[1].value = str(total)
        self.stat_activos.content.controls[1].value = str(len(cargos))
        self.stat_grados.content.controls[1].value = str(len(grados))

        for idx, p in enumerate(datos, start=1):
            nombre_completo = "%s %s" % (p.get("nombres", ""), p.get("apellidos", ""))
            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(idx), size=13, color=tc["table_row_text"])),
                        ft.DataCell(ft.Text(nombre_completo, size=13, weight=ft.FontWeight.W_500, color=tc["table_name_text"])),
                        ft.DataCell(ft.Text(p.get("cedula", ""), size=13, color=tc["table_row_text"])),
                        ft.DataCell(ft.Container(
                            content=ft.Text(p.get("grado_jerarquia", "—"), size=12, color=ft.Colors.AMBER_400),
                            bgcolor=tc["badge_amber"],
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        )),
                        ft.DataCell(ft.Text(p.get("cargo", "—"), size=13, color=tc["table_row_text"])),
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

        self._show_empty(total == 0)
        self.update()

    def _on_edit(self, e, personal_id):
        persona = self.controller.obtener_por_id(personal_id)
        if persona:
            dlg = self._build_edit_dialog(persona)
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()

    def _build_edit_dialog(self, persona):
        tc = theme_colors(self.dark_mode)
        txt_nombres = ft.TextField(label="Nombres", value=persona.get("nombres", ""), expand=True, border_radius=8, filled=True, bgcolor=tc["input_bg"], border_color=tc["input_border"], color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]))
        txt_apellidos = ft.TextField(label="Apellidos", value=persona.get("apellidos", ""), expand=True, border_radius=8, filled=True, bgcolor=tc["input_bg"], border_color=tc["input_border"], color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]))
        txt_cedula = ft.TextField(label="Cedula", value=persona.get("cedula", ""), border_radius=8, filled=True, bgcolor=tc["input_bg"], border_color=tc["input_border"], color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]))
        txt_telefono = ft.TextField(label="Telefono", value=persona.get("telefono", ""), border_radius=8, filled=True, bgcolor=tc["input_bg"], border_color=tc["input_border"], color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]))
        txt_grado = ft.TextField(label="Grado Jerarquico", value=persona.get("grado_jerarquia", ""), border_radius=8, filled=True, bgcolor=tc["input_bg"], border_color=tc["input_border"], color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]))
        txt_cargo = ft.TextField(label="Cargo", value=persona.get("cargo", ""), expand=True, border_radius=8, filled=True, bgcolor=tc["input_bg"], border_color=tc["input_border"], color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]))
        txt_dir_dom = ft.TextField(label="Dir. Domiciliaria", value=persona.get("dir_domiciliaria", ""), expand=True, border_radius=8, filled=True, bgcolor=tc["input_bg"], border_color=tc["input_border"], color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]))
        txt_dir_eme = ft.TextField(label="Dir. Emergencia", value=persona.get("dir_emergencia", ""), expand=True, border_radius=8, filled=True, bgcolor=tc["input_bg"], border_color=tc["input_border"], color=tc["input_text"], label_style=ft.TextStyle(color=tc["input_label"]))

        def save_edit(e):
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
                self.page.dialog.open = False
                self.page.snack_bar = ft.SnackBar(ft.Text("Actualizado correctamente"), open=True)
                self.load_data()
            else:
                self.lbl_status.value = err
                self.update()

        return ft.AlertDialog(
            title=ft.Text("Editar Personal", weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
            content=ft.Container(
                width=550,
                content=ft.Column([
                    ft.Row([txt_nombres, txt_apellidos]),
                    ft.Row([txt_cedula, txt_telefono]),
                    ft.Row([txt_grado, txt_cargo]),
                    ft.Row([txt_dir_dom, txt_dir_eme]),
                ], spacing=12, scroll=ft.ScrollMode.AUTO),
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(self.page.dialog, "open", False) or self.page.update()),
                ft.ElevatedButton("Guardar", on_click=save_edit, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700, shape=ft.RoundedRectangleBorder(radius=8))),
            ],
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=tc["bg_dialog"],
        )

    def _on_delete(self, e, personal_id):
        tc = theme_colors(self.dark_mode)

        def confirm_delete(e):
            self.page.dialog.open = False
            ok, err = self.controller.eliminar(personal_id)
            if ok:
                self.page.snack_bar = ft.SnackBar(ft.Text("Eliminado correctamente"), open=True)
                self.load_data()
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text(err), open=True)
            self.page.update()

        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminacion", weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
            content=ft.Text("Esta seguro de eliminar este registro? Esta accion no se puede deshacer.", color=tc["text_secondary"]),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(self.page.dialog, "open", False) or self.page.update()),
                ft.ElevatedButton("Eliminar", on_click=confirm_delete, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_700, shape=ft.RoundedRectangleBorder(radius=8))),
            ],
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=tc["bg_dialog"],
        )
        self.page.dialog.open = True
        self.page.update()

    def load_data(self):
        datos = self.controller.obtener_todos()
        self._render_table(datos)

    def did_mount(self):
        self.load_data()
        async def animate():
            await asyncio.sleep(0.05)
            self.opacity = 1
            self.update()
        asyncio.create_task(animate())
