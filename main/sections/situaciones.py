import flet as ft
from situaciones_irregulares.views.dashboard import SituacionesDashboard


def build(app: 'MainApp'):
    dashboard = SituacionesDashboard(
        controller=app.situaciones_ctrl,
        personal_id=None,
        on_back=app._go_to_personal,
        on_add=app.mostrar_form_situacion,
        on_edit=app.mostrar_form_edicion_situacion,
        on_delete=lambda sid: app.situaciones_ctrl.eliminar(sid),
        on_view_detail=app.mostrar_detalle_situacion,
        on_resolver=app.situaciones_ctrl.resolver,
        dark_mode=app.dark_mode,
    )
    app._situaciones_dashboard = dashboard
    return dashboard