import os
import json
from datetime import datetime

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'preferencias.json')

DEFAULT_PREFERENCIAS = {
    "notificaciones_activadas": True,
    "dias_anticipacion": 3,
    "theme_oscuro": True,
}


def cargar_preferencias():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_PREFERENCIAS.copy()
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return DEFAULT_PREFERENCIAS.copy()


def guardar_preferencias(preferencias):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(preferencias, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def get_preferencia(clave, default=None):
    prefs = cargar_preferencias()
    return prefs.get(clave, default)


def set_preferencia(clave, valor):
    prefs = cargar_preferencias()
    prefs[clave] = valor
    return guardar_preferencias(prefs)