import flet as ft
from comisiones.views.dashboard import ComisionesDashboard


def build(app: 'MainApp'):
    dashboard = ComisionesDashboard(
        controller=app.comisiones_ctrl,
        personal_id=None,
        on_back=app._go_to_personal,
        on_add=app.mostrar_form_comision,
        on_edit=app.mostrar_form_edicion_comision,
        on_delete=app.eliminar_comision,
        on_view_detail=app.mostrar_detalle_comision,
        dark_mode=app.dark_mode,
    )
    app._comisiones_dashboard = dashboard
    return dashboard