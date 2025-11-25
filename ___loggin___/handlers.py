import os
import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler

from .config import (
    log_folder,
    log_file,
    log_rotate_daily,
    log_rotate_size,
    log_size_backup,
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
    if not log_file:
        return None

    path = os.path.join(log_folder, f"{area}.log")

    if log_rotate_daily:
        handler = TimedRotatingFileHandler(
            path,
            when="midnight",
            backupCount=log_rotate_daily,
            encoding="utf-8"
        )
    else:
        handler = RotatingFileHandler(
            path,
            maxBytes=log_rotate_size,
            backupCount=log_size_backup,
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
