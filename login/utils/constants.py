DIAS_EXPIRACION_PRONTO = 3

CEDULA_MIN = 7
CEDULA_MAX = 10
TELEFONO_MIN = 10
TELEFONO_MAX = 11

FECHA_FORMAT = "%d/%m/%Y"

TIPOS_PERMISO = [
    "Extraordinario",
    "Vacacional",
    "Pre Maternal",
    "Post Maternal",
    "Paternal",
    "Operacional",
    "Reposo",
]

EXPORT_TEMPLATES = {
    "resumen": {
        "nombre": "Resumen",
        "columnas": [
            ("nombres", "Nombres"),
            ("apellidos", "Apellidos"),
            ("cedula", "Cedula"),
            ("tipo_permiso", "Tipo Permiso"),
            ("fecha_desde", "Fecha Inicio"),
            ("fecha_hasta", "Fecha Vencimiento"),
        ]
    },
}
