import flet as ft
import asyncio
from datetime import datetime
from core.estado_utils import obtener_estado
from core.constants import FECHA_FORMAT
from core.theme import theme_colors


class ComisionDetailView(ft.Container):
    def __init__(self, datos, on_back=None, on_edit=None, on_finalizar=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.alignment = ft.Alignment.CENTER
        self.on_back = on_back
        self.on_edit = on_edit
        self.on_finalizar = on_finalizar
        self.datos = datos
        self.comision_id = datos.get("id")
        self.dark_mode = dark_mode
        tc = theme_colors(self.dark_mode)

        W_FULL = 440

        finalizada = datos.get("finalizada", 0)
        if finalizada:
            estado_texto = "FINALIZADA"
            estado_color = ft.Colors.GREEN_700
        else:
            estado_texto = "ACTIVA"
            estado_color = ft.Colors.ORANGE_700

        badge_estado = ft.Container(
            content=ft.Text(estado_texto, size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            bgcolor=estado_color, border_radius=6,
            padding=ft.padding.symmetric(horizontal=12, vertical=4),
        )

        def campo_ro(label, valor, icono=None, expand=False, width=None):
            kw = {
                "label": label,
                "value": valor or "\u2014",
                "read_only": True,
                "icon": icono,
                "text_size": 13,
                "filled": True,
                "bgcolor": tc["input_bg"],
                "border_color": tc["input_border"],
                "color": tc["input_text"],
                "label_style": ft.TextStyle(color=tc["input_label"]),
            }
            if expand:
                kw["expand"] = True
            if width:
                kw["width"] = width
            return ft.TextField(**kw)

        def seccion_titulo(texto, icono):
            return ft.Container(
                content=ft.Row([ft.Icon(icono, color=ft.Colors.GREEN_400, size=18),
                                ft.Text(texto, size=13, weight=ft.FontWeight.BOLD, color=tc["text_secondary"])],
                               spacing=8),
                padding=ft.padding.only(top=12, bottom=2),
            )

        fecha_salida_str = datos.get("fecha_salida", "")

        btn_editar = ft.ElevatedButton(
            "Editar Comisión", icon=ft.Icons.EDIT_OUTLINED,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700,
                                 shape=ft.RoundedRectangleBorder(radius=8), padding=15),
            width=W_FULL,
            on_click=lambda e: self.on_edit(self.comision_id) if self.on_edit else None,
        )

        btn_finalizar = ft.ElevatedButton(
            "Finalizar Comisión", icon=ft.Icons.CHECK_CIRCLE,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.ORANGE_700,
                                 shape=ft.RoundedRectangleBorder(radius=8), padding=15),
            width=W_FULL,
            on_click=self._confirmar_finalizar,
            visible=not finalizada,
        )

        btn_volver = ft.TextButton("Volver", icon=ft.Icons.ARROW_BACK, icon_color=tc["text_secondary"],
                                   on_click=lambda e: self.on_back() if self.on_back else None)

        formulario = ft.Column(
            controls=[
                ft.Icon(ft.Icons.BUSINESS_CENTER_OUTLINED, size=48, color=ft.Colors.GREEN_400),
                ft.Text("Detalle de la Comisión", size=24, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
                badge_estado,
                ft.Divider(color=tc["divider"]),
                seccion_titulo("Datos Personales", ft.Icons.PERSON),
                ft.Row([campo_ro("Nombre", "%s %s" % (datos.get("nombres", ""), datos.get("apellidos", "")),
                                 ft.Icons.PERSON, expand=True),
                        campo_ro("Cédula", datos.get("cedula"), ft.Icons.BADGE, expand=True)],
                       spacing=15, width=W_FULL),
                ft.Row([campo_ro("Grado", datos.get("grado_jerarquia"), ft.Icons.MILITARY_TECH, expand=True),
                        campo_ro("Cargo", datos.get("cargo"), ft.Icons.WORK_OUTLINED, expand=True)],
                       spacing=15, width=W_FULL),
                seccion_titulo("Detalles de la Comisión", ft.Icons.BUSINESS_CENTER),
                campo_ro("Tipo de Comisión", datos.get("tipo_comision"), ft.Icons.CATEGORY, width=W_FULL),
                campo_ro("Destino", datos.get("destino"), ft.Icons.LOCATION_ON, width=W_FULL),
                campo_ro("Fecha de Elaboración", datos.get("fecha_elaboracion"), ft.Icons.EDIT_DOCUMENT, width=W_FULL),
                campo_ro("Fecha de Salida", fecha_salida_str, ft.Icons.FLIGHT_TAKEOFF, width=W_FULL),
                seccion_titulo("Observaciones", ft.Icons.NOTES),
                campo_ro("Observaciones", datos.get("observaciones"), ft.Icons.NOTES, width=W_FULL),
                ft.Divider(color=tc["divider"]),
                btn_finalizar,
                btn_editar,
                btn_volver,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True, scroll=ft.ScrollMode.AUTO, spacing=8,
        )

        card = ft.Card(
            elevation=8, shape=ft.RoundedRectangleBorder(radius=15),
            content=ft.Container(
                padding=ft.padding.only(top=30, bottom=30, left=35, right=35),
                content=formulario, height=600,
            ),
        )

        self._card_wrapper = ft.Container(
            content=card, opacity=0, offset=ft.Offset(0, 0.15),
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN),
            animate_offset=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
        )
        self.content = self._card_wrapper

    def did_mount(self):
        async def animate():
            await asyncio.sleep(0.05)
            self._card_wrapper.opacity = 1
            self._card_wrapper.offset = ft.Offset(0, 0)
            try:
                self.update()
            except RuntimeError:
                pass
        asyncio.create_task(animate())

    def _confirmar_finalizar(self, e):
        if not self.on_finalizar:
            return
        
        tc = theme_colors(self.dark_mode)
        nombre = "%s %s" % (self.datos.get("nombres", ""), self.datos.get("apellidos", ""))

        def cerrar(e):
            self.page.pop_dialog()

        def finalizar(e):
            self.page.pop_dialog()
            ok, err, msg = self.on_finalizar(self.comision_id)
            if ok:
                self.page.snack_bar = ft.SnackBar(
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                        ft.Text(msg or "Comisión finalizada correctamente", color=ft.Colors.WHITE),
                    ], spacing=10),
                    bgcolor=ft.Colors.GREEN_700,
                    duration=3000,
                    open=True,
                )
                if self.on_back:
                    self.on_back()
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
