import flet as ft
from personal.views.form import PersonalForm


def mostrar_form_personal(app, personal_id=None):
    persona = None
    if personal_id:
        persona = app.personal_ctrl.obtener_por_id(personal_id)
    
    def builder():
        form = PersonalForm(
            controller=app.personal_ctrl,
            on_save=lambda pid: _on_personal_saved(app, pid),
            on_cancel=app._go_to_personal,
            personal_id=personal_id,
            datos_iniciales=persona,
            dark_mode=app.dark_mode,
        )
        app.content_area.content = form
        app.page.update()
    builder()


def mostrar_detalle_permiso(app, permiso_id):
    permiso = app.permisos_ctrl.obtener_por_id(permiso_id)
    if permiso:
        from permisos.views.detail_view import DetailView
        def builder():
            detail = DetailView(
                datos=permiso,
                on_back=app._go_to_permisos,
                on_edit=app.mostrar_form_edicion_permiso,
                dark_mode=app.dark_mode,
            )
            app.content_area.content = detail
            app.page.update()
        builder()


def mostrar_detalle_comision(app, comision_id):
    comision = app.comisiones_ctrl.obtener_por_id(comision_id)
    if comision:
        from comisiones.views.detail_view import ComisionDetailView
        def builder():
            detail = ComisionDetailView(
                datos=comision,
                on_back=app._go_to_comisiones,
                on_edit=app.mostrar_form_edicion_comision,
                on_finalizar=app.comisiones_ctrl.finalizar,
                dark_mode=app.dark_mode,
            )
            app.content_area.content = detail
            app.page.update()
        builder()


def mostrar_form_permiso(app, personal_id=None, permiso_id=None):
    from permisos.views.form import PermissionView
    
    permisos = app.permisos_ctrl.obtener_todos()
    comisiones = app.comisiones_ctrl.obtener_todos()
    situaciones = app.situaciones_irregulares_ctrl.obtener_todos() if hasattr(app, 'situaciones_irregulares_ctrl') else []
    
    def builder():
        form = PermissionView(
            on_back=app._go_to_permisos,
            on_save=app.guardar_permiso,
            personal_id=personal_id,
            permiso_id=permiso_id,
            lista_permisos=permisos,
            lista_comisiones=comisiones,
            lista_situaciones=situaciones,
            dark_mode=app.dark_mode,
        )
        app.content_area.content = form
        app.page.update()
    builder()


def mostrar_form_comision(app, personal_id=None, comision_id=None):
    from comisiones.views.form import ComisionForm
    
    permisos = app.permisos_ctrl.obtener_todos()
    comisiones = app.comisiones_ctrl.obtener_todos()
    situaciones = app.situaciones_irregulares_ctrl.obtener_todos() if hasattr(app, 'situaciones_irregulares_ctrl') else []
    
    def builder():
        form = ComisionForm(
            controller=app.comisiones_ctrl,
            on_save=lambda cid=None: _on_comision_saved(app, cid),
            on_back=app._go_to_comisiones,
            personal_id=personal_id,
            comision_id=comision_id,
            lista_permisos=permisos,
            lista_comisiones=comisiones,
            lista_situaciones=situaciones,
            dark_mode=app.dark_mode,
        )
        app.content_area.content = form
        app.page.update()
    builder()


def _on_personal_saved(app, personal_id):
    if hasattr(app, '_personal_dashboard'):
        app._personal_dashboard.load_data()
    app._go_to_personal()


def _on_comision_saved(app, comision_id=None):
    if hasattr(app, '_comisiones_dashboard'):
        app._comisiones_dashboard.load_data()
    app._go_to_comisiones()
    app.page.update()


def mostrar_dialogo_cambiar_password(app):
    from core.theme import theme_colors
    tc = theme_colors(app.dark_mode)
    
    txt_password_actual = ft.TextField(
        label="Password Actual", password=True,
        border_radius=10, filled=True, bgcolor=tc["input_bg"],
        border_color=tc["input_border"], color=tc["input_text"],
        label_style=ft.TextStyle(color=tc["input_label"]),
    )
    txt_password_nuevo = ft.TextField(
        label="Nuevo Password", password=True,
        border_radius=10, filled=True, bgcolor=tc["input_bg"],
        border_color=tc["input_border"], color=tc["input_text"],
        label_style=ft.TextStyle(color=tc["input_label"]),
    )
    txt_password_confirmar = ft.TextField(
        label="Confirmar Password", password=True,
        border_radius=10, filled=True, bgcolor=tc["input_bg"],
        border_color=tc["input_border"], color=tc["input_text"],
        label_style=ft.TextStyle(color=tc["input_label"]),
    )
    lbl_error = ft.Text("", color=ft.Colors.RED_400, size=12, visible=False)
    
    def guardar_password(e):
        lbl_error.visible = False
        actual = txt_password_actual.value or ""
        nuevo = txt_password_nuevo.value or ""
        confirmar = txt_password_confirmar.value or ""
        
        if not actual or not nuevo or not confirmar:
            lbl_error.value = "Todos los campos son requeridos"
            lbl_error.visible = True
            lbl_error.update()
            return
        
        if nuevo != confirmar:
            lbl_error.value = "Los passwords no coinciden"
            lbl_error.visible = True
            lbl_error.update()
            return
        
        if len(nuevo) < 6:
            lbl_error.value = "El password debe tener al menos 6 caracteres"
            lbl_error.visible = True
            lbl_error.update()
            return
        
        user = app.usuario_actual
        if not user:
            lbl_error.value = "Sesión no válida"
            lbl_error.visible = True
            lbl_error.update()
            return
        
        from auth.models.user_model import UserModel
        UserModel.cambiar_password(user.get("id"), nuevo)
        
        app.page.pop_dialog()
        app.page.snack_bar = ft.SnackBar(
            ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                ft.Text("Password actualizado correctamente", color=ft.Colors.WHITE)], spacing=10),
            bgcolor=ft.Colors.GREEN_700, duration=3000, open=True,
        )
        app.page.update()
    
    def cancelar(e):
        app.page.pop_dialog()
        app.page.update()
    
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Row([ft.Icon(ft.Icons.LOCK, color=ft.Colors.GREEN_400, size=24),
            ft.Text("Cambiar Password", size=18, weight=ft.FontWeight.BOLD, color=tc["text_primary"])], spacing=10),
        content=ft.Column([txt_password_actual, txt_password_nuevo, txt_password_confirmar, lbl_error], spacing=12),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar),
            ft.ElevatedButton("Guardar", on_click=guardar_password,
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700,
                    shape=ft.RoundedRectangleBorder(radius=8))),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=tc["bg_dialog"],
        shape=ft.RoundedRectangleBorder(radius=16),
    )
    app.page.show_dialog(dlg)


def mostrar_form_situacion(app, personal_id=None, situacion_id=None):
    from situaciones_irregulares.views.form import SituacionFormView
    
    permisos = app.permisos_ctrl.obtener_todos()
    comisiones = app.comisiones_ctrl.obtener_todos()
    situaciones = app.situaciones_ctrl.obtener_todos()
    
    def builder():
        form = SituacionFormView(
            controller=app.situaciones_ctrl,
            on_save=lambda sid=None: _on_situacion_saved(app, sid),
            on_back=app._go_to_situaciones,
            personal_id=personal_id,
            situacion_id=situacion_id,
            lista_permisos=permisos,
            lista_comisiones=comisiones,
            lista_situaciones=situaciones,
            dark_mode=app.dark_mode,
        )
        app.content_area.content = form
        app.page.update()
    builder()


def mostrar_detalle_situacion(app, situacion_id):
    situacion = app.situaciones_ctrl.obtener_por_id(situacion_id)
    if situacion:
        from situaciones_irregulares.views.detail_view import SituacionDetailView
        def builder():
            detail = SituacionDetailView(
                datos=situacion,
                on_back=app._go_to_situaciones,
                on_edit=app.mostrar_form_edicion_situacion,
                on_resolver=app.situaciones_ctrl.resolver,
                dark_mode=app.dark_mode,
            )
            app.content_area.content = detail
            app.page.update()
        builder()


def _on_situacion_saved(app, situacion_id=None):
    if hasattr(app, '_situaciones_dashboard'):
        app._situaciones_dashboard.load_data()
    app._go_to_situaciones()
    app.page.update()


def mostrar_form_edicion_situacion(app, situacion_id):
    mostrar_form_situacion(app, situacion_id=situacion_id)