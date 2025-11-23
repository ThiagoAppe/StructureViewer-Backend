import os
import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler

from .config import (
    LogFolder,
    LOG_FILE,
    LOG_ROTATE_DAILY,
    LOG_ROTATE_SIZE,
    LOG_DAILY_BACKUP,
    LOG_SIZE_BACKUP,
)


def create_file_handler(area: str, formatter):
    """
    Create a file handler with optional rotation settings.

    Parameters:
        area (str): Log category used to name the log file.
        formatter: Formatter assigned to the handler.

    Returns:
        logging.Handler | None: Configured handler or None if file logging is disabled.
    """
    if not LOG_FILE:
        return None

    path = os.path.join(LogFolder, f"{area}.log")

    if LOG_ROTATE_DAILY:
        handler = TimedRotatingFileHandler(
            path,
            when="midnight",
            backupCount=LOG_DAILY_BACKUP,
            encoding="utf-8"
        )
    else:
        handler = RotatingFileHandler(
            path,
            maxBytes=LOG_ROTATE_SIZE,
            backupCount=LOG_SIZE_BACKUP,
            encoding="utf-8"
        )

    handler.setFormatter(formatter)
    return handler


def create_console_handler(formatter):
    """
    Create a console handler with the provided formatter.

    Parameters:
        formatter: Formatter assigned to the console output.

    Returns:
        logging.Handler: Configured console handler.
    """
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    return console
