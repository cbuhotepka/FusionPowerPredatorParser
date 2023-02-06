from loguru import logger
from .engine_modul.engine import Engine
from .sender import sender_new as sender


@logger.catch()
def start_parsing(auto_parse, full_auto, error_mode, daemon):
    engine = Engine(auto_parse, full_auto, error_mode, daemon)
    engine.start()


__all__ = ['start_parsing', 'sender']