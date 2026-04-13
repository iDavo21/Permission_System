import flet as ft
from core.estado_utils import obtener_estado, fecha_a_datetime, obtener_estado_urgencia
from core.theme import theme_colors
from datetime import datetime


class PermisosTable(ft.Container):
    def __init__(self, permisos=None, on_edit=None, on_delete_confirm=None, on_view_detail=None, dark_mode=True):
        super().__init__()
        self.dark_mode = dark_mode
        self.border_radius = 14
        self.border = ft.border.all(1, theme_colors(self.dark_mode)["table_border"])
        self.clip_behavior = ft.ClipBehavior.ANTI_ALIAS

        self.on_edit = on_edit
        self.on_delete_confirm = on_delete_confirm
        self.on_view_detail = on_view_detail

        self._sort_column = None
        self._sort_ascending = True

        tc = theme_colors(self.dark_mode)
        self.tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("#", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=12), on_sort=lambda e: self._ordenar("id")),
                ft.DataColumn(ft.Text("Nombre Completo", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=13), on_sort=lambda e: self._ordenar("nombre")),
                ft.DataColumn(ft.Text("Jerarquia", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=13), on_sort=lambda e: self._ordenar("jerarquia")),
                ft.DataColumn(ft.Text("Tipo de Permiso", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=13), on_sort=lambda e: self._ordenar("tipo")),
                ft.DataColumn(ft.Text("Desde", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=13), on_sort=lambda e: self._ordenar("desde")),
                ft.DataColumn(ft.Text("Hasta", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=13), on_sort=lambda e: self._ordenar("hasta")),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=13), on_sort=lambda e: self._ordenar("estado")),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, color=tc["table_header"], size=13)),
            ],
            rows=[],
            border_radius=12,
            column_spacing=18,
            heading_row_color=tc["table_header_bg"],
            heading_row_height=48,
            data_row_min_height=48,
            data_row_max_height=60,
            divider_thickness=0.5,
        )

        self.content = self.tabla

    def _ordenar(self, columna):
        if self._sort_column == columna:
            self._sort_ascending = not self._sort_ascending
        else:
            self._sort_column = columna
            self._sort_ascending = True

    def get_sorted(self, permisos):
        if not self._sort_column:
            return permisos

        def clave(p):
            col = self._sort_column
            if col == "id":
                return p.get("id", 0) or 0
            elif col == "nombre":
                return "%s %s" % (p.get("nombres", ""), p.get("apellidos", "")).lower()
            elif col == "jerarquia":
                return (p.get("grado_jerarquia", "") or "").lower()
            elif col == "tipo":
                return (p.get("tipo_permiso", "") or "").lower()
            elif col == "desde":
                return fecha_a_datetime(p.get("fecha_desde", "")) or datetime.min.date()
            elif col == "hasta":
                return fecha_a_datetime(p.get("fecha_hasta", "")) or datetime.min.date()
            elif col == "estado":
                return obtener_estado_urgencia(p.get("fecha_hasta", ""))
            return ""

        try:
            return sorted(permisos, key=clave, reverse=not self._sort_ascending)
        except TypeError:
            return permisos

    def render_filas(self, permisos_pagina, inicio):
        tc = theme_colors(self.dark_mode)
        filas = []
        for i, p in enumerate(permisos_pagina):
            num_fila = inicio + i + 1
            estado_texto, estado_color = obtener_estado(p.get("fecha_hasta", ""))
            pid = p.get("id")

            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(num_fila), size=12, color=tc["text_tertiary"])),
                        ft.DataCell(ft.GestureDetector(
                            content=ft.Text(
                                "%s %s" % (p.get("nombres", ""), p.get("apellidos", "")),
                                size=14, color=ft.Colors.CYAN_400, weight=ft.FontWeight.W_500,
                            ),
                            on_tap=lambda e, _pid=pid: self.on_view_detail(_pid) if self.on_view_detail else None,
                            mouse_cursor=ft.MouseCursor.CLICK,
                        )),
                        ft.DataCell(ft.Text(p.get("grado_jerarquia", ""), size=13, color=tc["table_row_text"])),
                        ft.DataCell(ft.Container(
                            content=ft.Text(p.get("tipo_permiso", ""), size=12, color=ft.Colors.CYAN_400),
                            bgcolor=tc["badge_cyan"],
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )),
                        ft.DataCell(ft.Container(
                            content=ft.Text(p.get("fecha_desde", ""), size=13, color=ft.Colors.GREEN_400),
                            bgcolor=tc["badge_green"],
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )),
                        ft.DataCell(ft.Container(
                            content=ft.Text(p.get("fecha_hasta", ""), size=13, color=ft.Colors.RED_400),
                            bgcolor=tc["badge_red"],
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )),
                        ft.DataCell(ft.Container(
                            content=ft.Text(estado_texto, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            bgcolor=estado_color,
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )),
                        ft.DataCell(
                            ft.PopupMenuButton(
                                icon=ft.Icons.MORE_VERT,
                                icon_color=tc["text_secondary"],
                                icon_size=20,
                                tooltip="Acciones",
                                items=[
                                    ft.PopupMenuItem(
                                        content=ft.Text("Editar", color=tc["text_primary"]),
                                        icon=ft.Icons.EDIT_OUTLINED,
                                        on_click=lambda e, _pid=pid: self.on_edit(_pid) if self.on_edit else None,
                                    ),
                                    ft.PopupMenuItem(
                                        content=ft.Text("Eliminar", color=ft.Colors.RED_400),
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        on_click=lambda e, _pid=pid: self.on_delete_confirm(_pid) if self.on_delete_confirm else None,
                                    ),
                                ],
                            )
                        ),
                    ],
                    color={ft.ControlState.HOVERED: tc["table_row_hover"]}
                )
            )
        return filas
