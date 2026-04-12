import flet as ft
from personal.views.dashboard import PersonalDashboard


def build(app: 'MainApp'):
    dashboard = PersonalDashboard(
        controller=app.personal_ctrl,
        on_navigate_permisos=lambda pid=None: app._load_section_content("permisos"),
        on_navigate_comisiones=lambda pid=None: app._load_section_content("comisiones"),
        on_add_personal=app.mostrar_form_personal,
        on_edit_personal=app.mostrar_form_edicion_personal,
        on_delete_personal=app.eliminar_personal,
        dark_mode=app.dark_mode,
    )
    app._personal_dashboard = dashboard
    return dashboard