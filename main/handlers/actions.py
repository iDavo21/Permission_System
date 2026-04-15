import flet as ft
import os
import json
from datetime import datetime
from core.logger import logger
from core.backup import crear_backup as _crear_backup
from core.estado_utils import obtener_estado


def crear_backup(app):
    try:
        nombre = _crear_backup()
        logger.info(f"Backup creado: {nombre}")
        
        snack = ft.SnackBar(
            content=ft.Text(f"✓ Backup creado: {nombre}"),
            bgcolor=ft.Colors.GREEN_700,
            duration=3000,
        )
        app.page.controls.append(snack)
        snack.open = True
        app._load_section_content("configuracion")
        app.page.update()
    except Exception as e:
        logger.error(f"Error al crear backup: {str(e)}")
        
        snack = ft.SnackBar(
            content=ft.Text(f"Error: {str(e)}"),
            bgcolor=ft.Colors.RED_700,
            duration=4000,
        )
        app.page.controls.append(snack)
        snack.open = True
        app.page.update()


def eliminar_personal(app, personal_id):
    from core.theme import theme_colors
    tc = theme_colors(app.dark_mode)
    
    def confirmar(e):
        app.page.pop_dialog()
        
        from permisos.controller import PermisosController
        from comisiones.controller import ComisionesController
        from situaciones_irregulares.controller import SituacionesController
        permisos_ctrl = PermisosController()
        comisiones_ctrl = ComisionesController()
        situaciones_ctrl = SituacionesController()
        
        permisos_ctrl.eliminar_por_personal(personal_id)
        comisiones_ctrl.eliminar_por_personal(personal_id)
        situaciones_ctrl.eliminar_por_personal(personal_id)
        
        ok, err, msg = app.personal_ctrl.eliminar(personal_id)
        
        if ok:
            snack = ft.SnackBar(
                content=ft.Text(msg or "Personal eliminado correctamente"),
                bgcolor=ft.Colors.GREEN_700,
                duration=3000,
            )
            app.page.controls.append(snack)
            snack.open = True
            if hasattr(app, '_personal_dashboard'):
                app._personal_dashboard.load_data()
        else:
            snack = ft.SnackBar(
                content=ft.Text(err or "Error al eliminar"),
                bgcolor=ft.Colors.RED_700,
                duration=4000,
            )
            app.page.controls.append(snack)
            snack.open = True
        app.page.update()
    
    def cancelar(e):
        app.page.pop_dialog()
        app.page.update()
    
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar eliminación", weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
        content=ft.Text("¿Estás seguro de eliminar este registro? Se eliminarán también sus permisos, comisiones y situaciones irregulares.", color=tc["text_secondary"]),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar),
            ft.ElevatedButton("Eliminar", on_click=confirmar,
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_700,
                    shape=ft.RoundedRectangleBorder(radius=8))),
        ],
        shape=ft.RoundedRectangleBorder(radius=16),
        bgcolor=tc["bg_dialog"],
    )
    app.page.show_dialog(dlg)


def eliminar_permiso(app, permiso_id):
    from core.theme import theme_colors
    tc = theme_colors(app.dark_mode)
    
    def confirmar(e):
        app.page.pop_dialog()
        ok, err, msg = app.permisos_ctrl.eliminar(permiso_id)
        if ok:
            snack = ft.SnackBar(
                content=ft.Text(msg or "Permiso eliminado correctamente"),
                bgcolor=ft.Colors.GREEN_700,
                duration=3000,
            )
            app.page.controls.append(snack)
            snack.open = True
            app._go_to_permisos()
        else:
            snack = ft.SnackBar(
                content=ft.Text(err or "Error al eliminar"),
                bgcolor=ft.Colors.RED_700,
                duration=4000,
            )
            app.page.controls.append(snack)
            snack.open = True
        app.page.update()
    
    def cancelar(e):
        app.page.pop_dialog()
        app.page.update()
    
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar eliminación", weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
        content=ft.Text("¿Estás seguro de eliminar este permiso?", color=tc["text_secondary"]),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar),
            ft.ElevatedButton("Eliminar", on_click=confirmar,
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_700,
                    shape=ft.RoundedRectangleBorder(radius=8))),
        ],
        shape=ft.RoundedRectangleBorder(radius=16),
        bgcolor=tc["bg_dialog"],
    )
    app.page.show_dialog(dlg)


def eliminar_comision(app, comision_id):
    from core.theme import theme_colors
    tc = theme_colors(app.dark_mode)
    
    def confirmar(e):
        app.page.pop_dialog()
        ok, err, msg = app.comisiones_ctrl.eliminar(comision_id)
        if ok:
            snack = ft.SnackBar(
                content=ft.Text(msg or "Comisión eliminada correctamente"),
                bgcolor=ft.Colors.GREEN_700,
                duration=3000,
            )
            app.page.controls.append(snack)
            snack.open = True
            app._go_to_comisiones()
        else:
            snack = ft.SnackBar(
                content=ft.Text(err or "Error al eliminar"),
                bgcolor=ft.Colors.RED_700,
                duration=4000,
            )
            app.page.controls.append(snack)
            snack.open = True
        app.page.update()
    
    def cancelar(e):
        app.page.pop_dialog()
        app.page.update()
    
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar eliminación", weight=ft.FontWeight.BOLD, color=tc["text_primary"]),
        content=ft.Text("¿Estás seguro de eliminar esta comisión?", color=tc["text_secondary"]),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar),
            ft.ElevatedButton("Eliminar", on_click=confirmar,
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_700,
                    shape=ft.RoundedRectangleBorder(radius=8))),
        ],
        shape=ft.RoundedRectangleBorder(radius=16),
        bgcolor=tc["bg_dialog"],
    )
    app.page.show_dialog(dlg)


def mostrar_dialogo_limpiar_permisos(app):
    from core.theme import theme_colors
    tc = theme_colors(app.dark_mode)
    
    def confirmar(e):
        app.page.pop_dialog()
        from datetime import datetime
        from core.estado_utils import fecha_a_datetime
        
        permisos = app.permisos_ctrl.obtener_todos()
        eliminados = 0
        
        for p in permisos:
            fecha_hasta = p.get("fecha_hasta", "")
            if fecha_hasta:
                fecha = fecha_a_datetime(fecha_hasta)
                if fecha and fecha < datetime.now().date():
                    app.permisos_ctrl.eliminar(p.get("id"))
                    eliminados += 1
        
        snack = ft.SnackBar(
            content=ft.Text(f"✓ Se eliminaron {eliminados} permisos expirados"),
            bgcolor=ft.Colors.GREEN_700,
            duration=3000,
        )
        app.page.controls.append(snack)
        snack.open = True
        app._load_section_content("configuracion")
        app.page.update()
    
    def cancelar(e):
        app.page.pop_dialog()
        app.page.update()
    
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Row([ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE_400, size=24),
            ft.Text("Limpiar Permisos Expirados", size=18, weight=ft.FontWeight.BOLD, color=tc["text_primary"])], spacing=10),
        content=ft.Text("¿Estás seguro de eliminar todos los permisos expirados?\nEsta acción no se puede deshacer.", color=tc["text_secondary"]),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar),
            ft.ElevatedButton("Eliminar", on_click=confirmar,
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_700,
                    shape=ft.RoundedRectangleBorder(radius=8))),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=tc["bg_dialog"],
        shape=ft.RoundedRectangleBorder(radius=16),
    )
    app.page.show_dialog(dlg)


def eliminar_situacion(app, situacion_id):
    from core.theme import theme_colors
    tc = theme_colors(app.dark_mode)
    
    def confirmar(e):
        app.page.pop_dialog()
        ok, err, msg = app.situaciones_ctrl.eliminar(situacion_id)
        if ok:
            snack = ft.SnackBar(
                content=ft.Text(msg or "Situación eliminada correctamente"),
                bgcolor=ft.Colors.GREEN_700,
                duration=3000,
            )
            app.page.controls.append(snack)
            snack.open = True
            app._go_to_situaciones()
        else:
            snack = ft.SnackBar(
                content=ft.Text(err or "Error al eliminar"),
                bgcolor=ft.Colors.RED_700,
                duration=4000,
            )
            app.page.controls.append(snack)
            snack.open = True
        app.page.update()

    def cancelar(e):
        app.page.pop_dialog()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Row([ft.Icon(ft.Icons.WARNING, color=ft.Colors.RED_400, size=24),
            ft.Text("Eliminar Situación Irregular", size=18, weight=ft.FontWeight.BOLD, color=tc["text_primary"])], spacing=10),
        content=ft.Text("¿Estás seguro de eliminar esta situación irregular?\nEsta acción no se puede deshacer.", color=tc["text_secondary"]),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar),
            ft.ElevatedButton("Eliminar", on_click=confirmar,
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_700,
                    shape=ft.RoundedRectangleBorder(radius=8))),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=tc["bg_dialog"],
        shape=ft.RoundedRectangleBorder(radius=16),
    )
    app.page.show_dialog(dlg)