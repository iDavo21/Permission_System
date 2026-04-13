DIAS_EXPIRACION_PRONTO = 3

CEDULA_MIN = 7
CEDULA_MAX = 10
TELEFONO_MIN = 10
TELEFONO_MAX = 11

FECHA_FORMAT = "%d/%m/%Y"

SNACKBAR_DURATION_SUCCESS = 3000
SNACKBAR_DURATION_ERROR = 4000

TIPOS_PERMISO = [
    "Extraordinario",
    "Vacacional",
    "Pre Maternal",
    "Post Maternal",
    "Paternal",
    "Operacional",
    "Reposo",
]

TIPOS_COMISION = [
    "Interna",
    "Externa",
    "Temporal",
    "Permanente",
]

TIPOS_SITUACION = [
    "Privado de libertad",
    "Presunto desertor",
    "Suspendido",
    "Baja temporal",
    "En investigación",
]

EXPORT_TEMPLATES = {
    "resumen": {
        "nombre": "Resumen",
        "columnas": [
            ("nombres", "Nombres"),
            ("apellidos", "Apellidos"),
            ("cedula", "Cedula"),
            ("tipo_permiso", "Tipo Permiso"),
            ("fecha_desde", "Fecha Desde"),
            ("fecha_hasta", "Fecha Hasta"),
        ]
    },
    "comisiones": {
        "nombre": "Comisiones",
        "columnas": [
            ("nombres", "Nombres"),
            ("apellidos", "Apellidos"),
            ("cedula", "Cedula"),
            ("tipo_comision", "Tipo Comision"),
            ("destino", "Destino"),
            ("fecha_desde", "Fecha Desde"),
            ("fecha_hasta", "Fecha Hasta"),
        ]
    },
}


def create_snack_success(message: str) -> ft.SnackBar:
    return ft.SnackBar(
        ft.Row([
            ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
            ft.Text(message, color=ft.Colors.WHITE),
        ], spacing=10),
        bgcolor=ft.Colors.GREEN_700,
        duration=SNACKBAR_DURATION_SUCCESS,
        open=True,
    )


def create_snack_error(message: str, duration: int = None) -> ft.SnackBar:
    return ft.SnackBar(
        ft.Row([
            ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE, size=20),
            ft.Text(message, color=ft.Colors.WHITE),
        ], spacing=10),
        bgcolor=ft.Colors.RED_700,
        duration=duration or SNACKBAR_DURATION_ERROR,
        open=True,
    )


def create_snack_warning(message: str) -> ft.SnackBar:
    return ft.SnackBar(
        ft.Row([
            ft.Icon(ft.Icons.WARNING, color=ft.Colors.WHITE, size=20),
            ft.Text(message, color=ft.Colors.WHITE),
        ], spacing=10),
        bgcolor=ft.Colors.RED_700,
        duration=SNACKBAR_DURATION_ERROR,
        open=True,
    )


def show_snack(page: ft.Page, message: str, is_error: bool = False, is_warning: bool = False):
    if is_error:
        page.snack_bar = create_snack_error(message)
    elif is_warning:
        page.snack_bar = create_snack_warning(message)
    else:
        page.snack_bar = create_snack_success(message)
    page.update()
