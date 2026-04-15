import flet as ft
import asyncio
from datetime import datetime
from core.theme import theme_colors


class SituacionDetailView(ft.Container):
    def __init__(self, datos, on_back=None, on_edit=None, on_resolver=None, dark_mode=True):
        super().__init__()
        self.expand = True
        self.alignment = ft.Alignment.CENTER
        self.on_back = on_back
        self.on_edit = on_edit
        self.on_resolver = on_resolver
        self.datos = datos
        self.situacion_id = datos.get("id")
        self.dark_mode = dark_mode
        tc = theme_colors(self.dark_mode)

        W_FULL = 440

        estado = datos.get("estado", "Activo")
        if estado == "Resuelto":
            estado_texto = "RESUELTO"
            estado_color = ft.Colors.GREEN_700
        else:
            estado_texto = "ACTIVO"
            estado_color = ft.Colors.RED_700

        badge_estado = ft.Container(
            content=ft.Text(estado_texto, size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            bgcolor=estado_color, border_radius=6,
            padding=ft.padding.symmetric(horizontal=12, vertical=4),
        )

        def campo_ro(label, valor, icono=None, expand=False, width=None):
            kw = {
                "label": label,
                "value": valor or "—",
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
                content=ft.Row([ft.Icon(icono, color=ft.Colors.ORANGE_400, size=18),
                                ft.Text(texto, size=13, weight=ft.FontWeight.BOLD, color=tc["text_secondary"])],
                               spacing=8),
                padding=ft.padding.only(top=12, bottom=2),
            )

        fecha_inicio = datos.get("fecha_inicio", "")
        fecha_resolucion = datos.get("fecha_resolucion", "")

        btn_editar = ft.ElevatedButton(
            "Editar Situación", icon=ft.Icons.EDIT_OUTLINED,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.ORANGE_700,
                                 shape=ft.RoundedRectangleBorder(radius=8), padding=15),
            width=W_FULL,
            on_click=lambda e: self.on_edit(self.situacion_id) if self.on_edit else None,
        )

        btn_resolver = ft.ElevatedButton(
            "Marcar como Resuelto", icon=ft.Icons.CHECK_CIRCLE,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700,
                                 shape=ft.RoundedRectangleBorder(radius=8), padding=15),
            width=W_FULL,
            on_click=self._confirmar_resolver,
            visible=estado != "Resuelto",
        )

        btn_volver = ft.TextButton("Volver", icon=ft.Icons.ARROW_BACK, icon_color=tc["text_secondary"],
                                   on_click=lambda e: self.on_back() if self.on_back else None)

        formulario = ft.Column(
            controls=[
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=48, color=ft.Colors.ORANGE_400),
                ft.Text("Detalle de Situación", size=24, weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
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
                seccion_titulo("Detalles de la Situación", ft.Icons.WARNING),
                campo_ro("Tipo de Situación", datos.get("tipo_situacion"), ft.Icons.CATEGORY, width=W_FULL),
                campo_ro("Fecha de Inicio", fecha_inicio, ft.Icons.EVENT, width=W_FULL),
                campo_ro("Fecha de Resolución", fecha_resolucion if fecha_resolucion else "Pendiente", ft.Icons.CHECK_CIRCLE, width=W_FULL),
                seccion_titulo("Observaciones", ft.Icons.NOTES),
                campo_ro("Observaciones", datos.get("observaciones"), ft.Icons.NOTES, width=W_FULL),
                ft.Divider(color=tc["divider"]),
                btn_resolver,
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
                content=formulario, height=650,
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

    def _confirmar_resolver(self, e):
        if not self.on_resolver:
            return
        
        tc = theme_colors(self.dark_mode)
        nombre = "%s %s" % (self.datos.get("nombres", ""), self.datos.get("apellidos", ""))

        def cerrar(e):
            self.page.pop_dialog()

        def resolver(e):
            self.page.pop_dialog()
            from core.constants import FECHA_FORMAT
            fecha_resolucion = datetime.now().strftime(FECHA_FORMAT)
            ok, err, msg = self.on_resolver(self.situacion_id, fecha_resolucion)
            if ok:
                self.page.snack_bar = ft.SnackBar(
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                        ft.Text(msg or "Situación resuelta correctamente", color=ft.Colors.WHITE),
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
            title=ft.Text("Resolver Situación", color=tc["text_primary"]),
            content=ft.Text(f"¿Confirmar que la situación de {nombre} ha sido resuelta?", color=tc["text_secondary"]),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar),
                ft.ElevatedButton("Confirmar", on_click=resolver, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700, shape=ft.RoundedRectangleBorder(radius=8))),
            ],
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=tc["bg_dialog"],
        )
        self.page.show_dialog(dlg)