import flet as ft
from personal.views.dashboard import PersonalDashboard


def build(app: 'MainApp'):
    permisos = app.permisos_ctrl.obtener_todos()
    comisiones = app.comisiones_ctrl.obtener_todos()
    situaciones = app.situaciones_irregulares_ctrl.obtener_todos() if hasattr(app, 'situaciones_irregulares_ctrl') else []
    dashboard = PersonalDashboard(
        controller=app.personal_ctrl,
        on_navigate_permisos=lambda pid=None: app._load_section_content("permisos"),
        on_navigate_comisiones=lambda pid=None: app._load_section_content("comisiones"),
        on_add_personal=app.mostrar_form_personal,
        on_edit_personal=app.mostrar_form_edicion_personal,
        on_delete_personal=app.eliminar_personal,
        lista_permisos=permisos,
        lista_comisiones=comisiones,
        lista_situaciones=situaciones,
        dark_mode=app.dark_mode,
    )
    app._personal_dashboard = dashboard
    return dashboard