import flet as ft
from utils.constants import EXPORT_TEMPLATES
from utils.estado_utils import obtener_estado


class ExportDialog(ft.AlertDialog):
    def __init__(self, permisos=None, on_export=None, usuario=None):
        super().__init__()
        self.modal = True
        self.title = ft.Row([
            ft.Icon(ft.Icons.DOWNLOAD_OUTLINED, color=ft.Colors.GREEN_700, size=24),
            ft.Text("Exportar Permisos", size=20, weight=ft.FontWeight.BOLD),
        ], spacing=10)

        self.permisos = permisos or []
        self.on_export = on_export
        self.usuario = usuario
        self.template_actual = "resumen"

        self._preview_container = ft.Container(
            content=ft.Text("Cargando vista previa...", size=12, color=ft.Colors.GREY_500),
            padding=10,
        )

        self._lbl_total = ft.Text("", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)

        self.content = ft.Column([
            ft.Text("Se exportaran los datos principales de los permisos filtrados:", size=13, color=ft.Colors.GREY_700),
            ft.Divider(height=10),
            ft.Text("Vista previa (primeros 10 registros):", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
            self._preview_container,
            ft.Divider(height=10),
            self._lbl_total,
        ], tight=True, spacing=8)

        self.actions = [
            ft.TextButton("Cancelar", on_click=self._cancelar),
            ft.ElevatedButton(
                "Exportar",
                icon=ft.Icons.DOWNLOAD,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.GREEN_700,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                on_click=self._exportar,
            ),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

        self._actualizar_preview()

    def _actualizar_preview(self):
        template = EXPORT_TEMPLATES.get(self.template_actual)
        if not template:
            return

        columnas = template["columnas"]
        datos_preview = self.permisos[:10]

        if not datos_preview:
            self._preview_container.content = ft.Text(
                "No hay datos para mostrar",
                size=12,
                color=ft.Colors.GREY_500,
            )
            self._lbl_total.value = ""
            try:
                self._preview_container.update()
            except RuntimeError:
                pass
            return

        cols = [ft.DataColumn(ft.Text(titulo, size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)) for _, titulo in columnas]

        filas = []
        for p in datos_preview:
            celdas = []
            for campo, _ in columnas:
                valor = p.get(campo, "") or ""
                celdas.append(ft.DataCell(ft.Text(str(valor), size=10)))
            filas.append(ft.DataRow(cells=celdas))

        tabla = ft.DataTable(
            columns=cols,
            rows=filas,
            column_spacing=12,
            heading_row_color=ft.Colors.GREEN_700,
            heading_row_height=32,
            data_row_min_height=28,
            data_row_max_height=36,
            divider_thickness=0.5,
            border_radius=6,
        )

        self._preview_container.content = ft.Container(
            content=tabla,
            border=ft.border.all(1, ft.Colors.GREEN_200),
            border_radius=6,
        )

        total = len(self.permisos)
        self._lbl_total.value = "Total de registros a exportar: %d" % total

        try:
            self._preview_container.update()
            self._lbl_total.update()
        except RuntimeError:
            pass

    def _cancelar(self, e):
        self.open = False
        if self.page:
            self.page.update()

    def _exportar(self, e):
        if not self.permisos:
            snack = ft.SnackBar(
                ft.Text("No hay datos para exportar"),
                bgcolor=ft.Colors.RED_700,
                duration=3000,
            )
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()
            return

        self.open = False
        if self.page:
            self.page.update()

        if self.on_export:
            self.on_export(self.template_actual)
