import logging

from ..config import log_level


def create_console_handler(formatter):
    handler = logging.StreamHandler()
    handler.setLevel(int(log_level))
    handler.setFormatter(formatter)
    return handler
