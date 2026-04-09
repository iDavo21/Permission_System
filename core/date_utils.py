from datetime import datetime, timedelta
from core.constants import FECHA_FORMAT


def parse_fecha(fecha_str: str, formato: str = FECHA_FORMAT) -> datetime:
    return datetime.strptime(fecha_str, formato)


def format_fecha(fecha: datetime, formato: str = FECHA_FORMAT) -> str:
    return fecha.strftime(formato)


def fecha_actual(formato: str = FECHA_FORMAT) -> str:
    return datetime.now().strftime(formato)


def calcular_dias(fecha_desde: str, fecha_hasta: str, formato: str = FECHA_FORMAT) -> int:
    desde = parse_fecha(fecha_desde, formato)
    hasta = parse_fecha(fecha_hasta, formato)
    return (hasta - desde).days + 1


def fecha_vencimiento(dias: int) -> str:
    return (datetime.now() + timedelta(days=dias)).strftime(FECHA_FORMAT)


def dias_hasta(fecha_str: str, formato: str = FECHA_FORMAT) -> int:
    fecha = parse_fecha(fecha_str, formato)
    return (fecha.date() - datetime.now().date()).days


def is_vencido(fecha_str: str, formato: str = FECHA_FORMAT) -> bool:
    return dias_hasta(fecha_str, formato) < 0


def is_proximo_vencer(fecha_str: str, dias_alerta: int = 3, formato: str = FECHA_FORMAT) -> bool:
    dias = dias_hasta(fecha_str, formato)
    return 0 <= dias <= dias_alerta


def rango_fechas_mes(año: int = None, mes: int = None) -> tuple:
    if año is None:
        año = datetime.now().year
    if mes is None:
        mes = datetime.now().month
    
    desde = datetime(año, mes, 1)
    if mes == 12:
        hasta = datetime(año + 1, 1, 1) - timedelta(days=1)
    else:
        hasta = datetime(año, mes + 1, 1) - timedelta(days=1)
    
    return format_fecha(desde), format_fecha(hasta)