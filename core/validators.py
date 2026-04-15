import re
from datetime import datetime
from core.constants import (
    CEDULA_MIN, CEDULA_MAX, TELEFONO_MIN, TELEFONO_MAX,
    FECHA_FORMAT, TIPOS_PERMISO, TIPOS_COMISION, TIPOS_SITUACION
)
from core.estado_utils import obtener_estado


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


def validar_fechas(fecha_desde: str, fecha_hasta: str, formato: str = FECHA_FORMAT) -> tuple:
    try:
        desde = datetime.strptime(fecha_desde, formato)
        hasta = datetime.strptime(fecha_hasta, formato)
        if desde > hasta:
            return False, "La fecha de inicio no puede ser posterior a la fecha de fin"
        return True, None
    except ValueError as e:
        return False, f"Formato de fecha inválido: {str(e)}"


def validar_fecha(fecha: str, formato: str = FECHA_FORMAT, campo: str = "Fecha") -> tuple:
    if not fecha:
        return False, f"{campo} es obligatoria"
    try:
        datetime.strptime(fecha, formato)
        return True, None
    except ValueError:
        return False, f"Formato de {campo} inválido. Use DD/MM/AAAA"


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


def validar_opcion(valor: str, opciones: list, campo: str = "Campo") -> tuple:
    if not valor:
        return False, f"{campo} es obligatorio"
    if valor not in opciones:
        return False, f"{campo} debe ser uno de: {', '.join(opciones)}"
    return True, None


def validar_personal(datos: dict) -> tuple:
    """
    Valida datos completos de personal.
    Retorna (es_valido, mensaje_error, errores_dict)
    """
    errores = {}
    
    ok, err = validar_texto(datos.get("nombres", ""), min_length=1, max_length=100, campo="Nombres")
    if not ok:
        errores["nombres"] = err
    
    ok, err = validar_texto(datos.get("apellidos", ""), min_length=1, max_length=100, campo="Apellidos")
    if not ok:
        errores["apellidos"] = err
    
    ok, err = validar_cedula(datos.get("cedula", ""))
    if not ok:
        errores["cedula"] = err
    
    ok, err = validar_telefono(datos.get("telefono", ""))
    if not ok:
        errores["telefono"] = err
    
    if datos.get("grado_jerarquia"):
        ok, err = validar_texto(datos.get("grado_jerarquia"), max_length=50, campo="Grado")
        if not ok:
            errores["grado_jerarquia"] = err
    
    if datos.get("cargo"):
        ok, err = validar_texto(datos.get("cargo"), max_length=100, campo="Cargo")
        if not ok:
            errores["cargo"] = err
    
    if datos.get("dir_domiciliaria"):
        ok, err = validar_texto(datos.get("dir_domiciliaria"), max_length=255, campo="Dirección")
        if not ok:
            errores["dir_domiciliaria"] = err
    
    if datos.get("dir_emergencia"):
        ok, err = validar_texto(datos.get("dir_emergencia"), max_length=255, campo="Emergencia")
        if not ok:
            errores["dir_emergencia"] = err
    
    if errores:
        primer_error = list(errores.values())[0]
        return False, primer_error, errores
    
    return True, None, None


def validar_permiso(datos: dict) -> tuple:
    """
    Valida datos completos de un permiso.
    """
    errores = {}
    
    if not datos.get("personal_id"):
        errores["personal_id"] = "Debe seleccionar un miembro del personal"
    
    ok, err = validar_opcion(
        datos.get("tipo_permiso", ""),
        TIPOS_PERMISO,
        "Tipo de permiso"
    )
    if not ok:
        errores["tipo_permiso"] = err
    
    ok, err = validar_fecha(datos.get("fecha_desde", ""), campo="Fecha desde")
    if not ok:
        errores["fecha_desde"] = err
    
    ok, err = validar_fecha(datos.get("fecha_hasta", ""), campo="Fecha hasta")
    if not ok:
        errores["fecha_hasta"] = err
    
    if datos.get("fecha_desde") and datos.get("fecha_hasta"):
        ok, err = validar_fechas(datos.get("fecha_desde"), datos.get("fecha_hasta"))
        if not ok:
            errores["fecha_hasta"] = err
    
    if datos.get("observaciones"):
        ok, err = validar_texto(datos.get("observaciones"), max_length=500, campo="Observaciones")
        if not ok:
            errores["observaciones"] = err
    
    if errores:
        primer_error = list(errores.values())[0]
        return False, primer_error, errores
    
    return True, None, None


def validar_comision(datos: dict) -> tuple:
    """
    Valida datos completos de una comisión.
    """
    errores = {}
    
    if not datos.get("personal_id"):
        errores["personal_id"] = "Debe seleccionar un miembro del personal"
    
    ok, err = validar_opcion(
        datos.get("tipo_comision", ""),
        TIPOS_COMISION,
        "Tipo de comisión"
    )
    if not ok:
        errores["tipo_comision"] = err
    
    ok, err = validar_texto(datos.get("destino", ""), min_length=1, max_length=200, campo="Destino")
    if not ok:
        errores["destino"] = err
    
    ok, err = validar_fecha(datos.get("fecha_salida", ""), campo="Fecha de salida")
    if not ok:
        errores["fecha_salida"] = err
    
    ok, err = validar_fecha(datos.get("fecha_retorno", ""), campo="Fecha de retorno")
    if not ok:
        errores["fecha_retorno"] = err
    
    if datos.get("fecha_salida") and datos.get("fecha_retorno"):
        ok, err = validar_fechas(datos.get("fecha_salida"), datos.get("fecha_retorno"))
        if not ok:
            errores["fecha_retorno"] = err
    
    if datos.get("observaciones"):
        ok, err = validar_texto(datos.get("observaciones"), max_length=500, campo="Observaciones")
        if not ok:
            errores["observaciones"] = err
    
    if errores:
        primer_error = list(errores.values())[0]
        return False, primer_error, errores
    
    return True, None, None


def validar_situacion(datos: dict) -> tuple:
    """
    Valida datos completos de una situación irregular.
    """
    errores = {}
    
    if not datos.get("personal_id"):
        errores["personal_id"] = "Debe seleccionar un miembro del personal"
    
    ok, err = validar_opcion(
        datos.get("tipo_situacion", ""),
        TIPOS_SITUACION,
        "Tipo de situación"
    )
    if not ok:
        errores["tipo_situacion"] = err
    
    ok, err = validar_fecha(datos.get("fecha_inicio", ""), campo="Fecha de inicio")
    if not ok:
        errores["fecha_inicio"] = err
    
    ok, err = validar_texto(datos.get("descripcion", ""), min_length=1, max_length=500, campo="Descripción")
    if not ok:
        errores["descripcion"] = err
    
    if errores:
        primer_error = list(errores.values())[0]
        return False, primer_error, errores
    
    return True, None, None


def verificar_estado_personal(personal_id, modulo_actual, lista_permisos, lista_comisiones, lista_situaciones):
    """
    Verifica si un personal ya está activo en otro módulo.
    
    Args:
        personal_id: ID del personal a verificar
        modulo_actual: Nombre del módulo donde se está guardando ('permisos', 'comisiones', 'situaciones')
        lista_permisos: Lista de permisos
        lista_comisiones: Lista de comisiones
        lista_situaciones: Lista de situaciones irregulares
    
    Returns:
        None si está disponible, o mensaje de conflicto si no lo está
    """
    if not personal_id:
        return None
    
    permisos_activos = []
    comisiones_activas = []
    situaciones_activas = []
    
    for p in lista_permisos:
        if p.get("personal_id") == personal_id:
            estado, _ = obtener_estado(p.get("fecha_hasta", ""))
            if estado in ("Vigente", "Por Expirar"):
                permisos_activos.append(p)
    
    for c in lista_comisiones:
        if c.get("personal_id") == personal_id and not c.get("finalizada", 0):
            comisiones_activas.append(c)
    
    for s in lista_situaciones:
        if s.get("personal_id") == personal_id and s.get("estado", "Activo") == "Activo":
            situaciones_activas.append(s)
    
    conflictos = []
    
    if modulo_actual != "permisos" and permisos_activos:
        nombres = "%s %s" % (permisos_activos[0].get("nombres", ""), permisos_activos[0].get("apellidos", ""))
        conflictos.append(f"un permiso activo para {nombres}")
    
    if modulo_actual != "comisiones" and comisiones_activas:
        nombres = "%s %s" % (comisiones_activas[0].get("nombres", ""), comisiones_activas[0].get("apellidos", ""))
        conflictos.append(f"una comisión activa para {nombres}")
    
    if modulo_actual != "situaciones" and situaciones_activas:
        nombres = "%s %s" % (situaciones_activas[0].get("nombres", ""), situaciones_activas[0].get("apellidos", ""))
        conflictos.append(f"una situación activa para {nombres}")
    
    if conflictos:
        return "Esta persona ya tiene: %s" % ", ".join(conflictos)
    
    return None


def obtener_estado_personal(personal_id, lista_permisos, lista_comisiones, lista_situaciones):
    """
    Obtiene el estado actual del personal para mostrar en la UI.
    
    Returns:
        dict con 'estado' (disponible/permiso/comision/situacion) y 'info' (detalle)
    """
    if not personal_id:
        return {"estado": "desconocido", "info": ""}
    
    for p in lista_permisos:
        if p.get("personal_id") == personal_id:
            estado, _ = obtener_estado(p.get("fecha_hasta", ""))
            if estado in ("Vigente", "Por Expirar"):
                return {"estado": "permiso", "info": p.get("tipo_permiso", "Permiso")}
    
    for c in lista_comisiones:
        if c.get("personal_id") == personal_id and not c.get("finalizada", 0):
            return {"estado": "comision", "info": c.get("tipo_comision", "Comisión")}
    
    for s in lista_situaciones:
        if s.get("personal_id") == personal_id and s.get("estado", "Activo") == "Activo":
            return {"estado": "situacion", "info": s.get("tipo_situacion", "Situación")}
    
    return {"estado": "disponible", "info": ""}