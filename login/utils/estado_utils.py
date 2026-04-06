from datetime import datetime
from utils.constants import DIAS_EXPIRACION_PRONTO, FECHA_FORMAT


_ESTADO_COLORES = {
    "Expirado": "RED",
    "Expira hoy": "ORANGE",
    "Por Expirar": "AMBER",
    "Vigente": "GREEN",
    "Sin fecha": "GREY",
}


def obtener_estado(fecha_hasta_str):
    if not fecha_hasta_str:
        return "Sin fecha", _ESTADO_COLORES["Sin fecha"]
    try:
        hoy = datetime.now().date()
        fecha_hasta = datetime.strptime(fecha_hasta_str, FECHA_FORMAT).date()
        diff = (fecha_hasta - hoy).days
        if diff < 0:
            return "Expirado", _ESTADO_COLORES["Expirado"]
        elif diff == 0:
            return "Expira hoy", _ESTADO_COLORES["Expira hoy"]
        elif diff <= DIAS_EXPIRACION_PRONTO:
            return "Por Expirar", _ESTADO_COLORES["Por Expirar"]
        else:
            return "Vigente", _ESTADO_COLORES["Vigente"]
    except ValueError:
        return "\u2014", _ESTADO_COLORES["Sin fecha"]


def obtener_estado_urgencia(fecha_hasta_str):
    if not fecha_hasta_str:
        return 9999
    try:
        hoy = datetime.now().date()
        fecha_hasta = datetime.strptime(fecha_hasta_str, FECHA_FORMAT).date()
        return (fecha_hasta - hoy).days
    except ValueError:
        return 9999


def calcular_dias_permiso(fecha_desde_str, fecha_hasta_str):
    try:
        fd = datetime.strptime(fecha_desde_str, FECHA_FORMAT)
        fh = datetime.strptime(fecha_hasta_str, FECHA_FORMAT)
        diff = (fh - fd).days
        return diff if diff >= 0 else None
    except (ValueError, TypeError):
        return None


def fecha_a_datetime(fecha_str):
    try:
        return datetime.strptime(fecha_str, FECHA_FORMAT).date()
    except (ValueError, TypeError):
        return None


def contar_expiracion_proxima(permisos, dias=None):
    if dias is None:
        from utils.constants import DIAS_EXPIRACION_PRONTO
        dias = DIAS_EXPIRACION_PRONTO
    hoy = datetime.now().date()
    count = 0
    for p in permisos:
        fh = fecha_a_datetime(p.get("fecha_hasta", ""))
        if fh and 0 <= (fh - hoy).days <= dias:
            count += 1
    return count


def clasificar_notificaciones(permisos):
    hoy = datetime.now().date()
    vence_hoy = []
    vence_manana = []
    vence_proximos = []
    for p in permisos:
        fh = fecha_a_datetime(p.get("fecha_hasta", ""))
        if fh:
            diff = (fh - hoy).days
            if diff == 0:
                vence_hoy.append({**p, "_dias_restantes": diff})
            elif diff == 1:
                vence_manana.append({**p, "_dias_restantes": diff})
            elif 2 <= diff <= 3:
                vence_proximos.append({**p, "_dias_restantes": diff})
    return vence_hoy, vence_manana, vence_proximos


def nombre_completo(datos):
    return ("%s %s" % (datos.get("nombres", ""), datos.get("apellidos", ""))).strip()
