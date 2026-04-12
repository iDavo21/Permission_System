import flet as ft
from permisos.views.dashboard import AdminView


def build(app: 'MainApp'):
    permisos = app.permisos_ctrl.obtener_todos()
    admin_view = AdminView(
        on_add_permission=app.mostrar_form_permiso,
        lista_permisos=permisos,
        on_edit=app.mostrar_form_edicion_permiso,
        on_delete=app.eliminar_permiso,
        on_view_detail=app.mostrar_detalle_permiso,
        personal_id=None,
        dark_mode=app.dark_mode,
    )
    app._permisos_dashboard = admin_view
    return admin_view