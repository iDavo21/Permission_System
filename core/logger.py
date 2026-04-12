import logging
import os
import sys

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, 'actividad.log')

logger = logging.getLogger('sistema_vacaciones')
logger.setLevel(logging.DEBUG if os.environ.get('DEBUG') else logging.INFO)

_formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)

_file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
_file_handler.setFormatter(_formatter)
_file_handler.setLevel(logging.INFO)
logger.addHandler(_file_handler)

_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(_formatter)
_console_handler.setLevel(logging.DEBUG if os.environ.get('DEBUG') else logging.WARNING)
logger.addHandler(_console_handler)


class LoggerMixin:
    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(f'sistema_vacaciones.{self.__class__.__name__}')
        return self._logger

    def log_info(self, message, **kwargs):
        extra_info = ' | '.join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ''
        msg = f"{message} | {extra_info}" if extra_info else message
        self.logger.info(msg)

    def log_error(self, message, error=None, **kwargs):
        extra_info = ' | '.join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ''
        msg = f"{message} | {extra_info}" if extra_info else message
        if error:
            msg += f" | Error: {str(error)}"
        self.logger.error(msg)

    def log_warning(self, message, **kwargs):
        extra_info = ' | '.join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ''
        msg = f"{message} | {extra_info}" if extra_info else message
        self.logger.warning(msg)

    def log_debug(self, message, **kwargs):
        extra_info = ' | '.join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ''
        msg = f"{message} | {extra_info}" if extra_info else message
        self.logger.debug(msg)
