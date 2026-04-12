import flet as ft
from dashboard.views.dashboard_view import DashboardView


def build(app: 'MainApp'):
    dashboard = DashboardView(
        personal_ctrl=app.personal_ctrl,
        permisos_ctrl=app.permisos_ctrl,
        comisiones_ctrl=app.comisiones_ctrl,
        dark_mode=app.dark_mode,
    )
    app._inicio_dashboard = dashboard
    return dashboard