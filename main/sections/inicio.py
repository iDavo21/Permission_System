import flet as ft
from dashboard.views.dashboard_view import DashboardView


def build(app: 'MainApp'):
    dashboard = DashboardView(
        personal_ctrl=app.personal_ctrl,
        permisos_ctrl=app.permisos_ctrl,
        comisiones_ctrl=app.comisiones_ctrl,
        situaciones_ctrl=app.situaciones_ctrl,
        on_navigate_personal=app._go_to_personal,
        on_navigate_permisos=app._go_to_permisos,
        on_navigate_comisiones=app._go_to_comisiones,
        on_navigate_situaciones=app._go_to_situaciones,
        dark_mode=app.dark_mode,
    )
    app._inicio_dashboard = dashboard
    return dashboard