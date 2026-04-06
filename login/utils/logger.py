import logging
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, 'actividad.log')

logger = logging.getLogger('sistema_vacaciones')
logger.setLevel(logging.INFO)

_formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

_file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
_file_handler.setFormatter(_formatter)
logger.addHandler(_file_handler)

_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(_formatter)
logger.addHandler(_stream_handler)
