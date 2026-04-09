import re
from core.constants import CEDULA_MIN, CEDULA_MAX, TELEFONO_MIN, TELEFONO_MAX


def validar_cedula(cedula: str) -> tuple:
    if not cedula:
        return False, "La cédula es obligatoria"
    if not cedula.isdigit():
        return False, "La cédula debe contener solo números"
    if len(cedula) < CEDULA_MIN or len(cedula) > CEDULA_MAX:
        return False, f"La cédula debe tener entre {CEDULA_MIN} y {CEDULA_MAX} dígitos"
    return True, None


def validar_telefono(telefono: str, opcional: bool = False) -> tuple:
    if not telefono:
        if opcional:
            return True, None
        return False, "El teléfono es obligatorio"
    if not telefono.isdigit():
        return False, "El teléfono debe contener solo números"
    if len(telefono) < TELEFONO_MIN or len(telefono) > TELEFONO_MAX:
        return False, f"El teléfono debe tener entre {TELEFONO_MIN} y {TELEFONO_MAX} dígitos"
    return True, None


def validar_texto(texto: str, min_length: int = 1, max_length: int = 255, campo: str = "Campo") -> tuple:
    if not texto or not texto.strip():
        return False, f"{campo} es obligatorio"
    if len(texto.strip()) < min_length:
        return False, f"{campo} debe tener al menos {min_length} caracteres"
    if len(texto) > max_length:
        return False, f"{campo} no puede exceder {max_length} caracteres"
    return True, None


def validar_fechas(fecha_desde: str, fecha_hasta: str, formato: str = "%d/%m/%Y") -> tuple:
    from datetime import datetime
    try:
        desde = datetime.strptime(fecha_desde, formato)
        hasta = datetime.strptime(fecha_hasta, formato)
        if desde > hasta:
            return False, "La fecha de inicio no puede ser posterior a la fecha de fin"
        return True, None
    except ValueError as e:
        return False, f"Formato de fecha inválido: {str(e)}"


def validar_email(email: str) -> tuple:
    if not email:
        return True, None
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(patron, email):
        return False, "El correo electrónico no es válido"
    return True, None


def sanitizar_texto(texto: str, max_length: int = None) -> str:
    if not texto:
        return ""
    texto = texto.strip()
    texto = re.sub(r'\s+', ' ', texto)
    if max_length:
        texto = texto[:max_length]
    return texto