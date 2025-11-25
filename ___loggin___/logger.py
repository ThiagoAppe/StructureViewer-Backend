import logging

from .config import (
    log_level,
    log_console,
    log_file,
    log_json,
    LogArea,
    LogCategory
)

from .formatters import ColorFormatter, JsonFormatter
from .handlers import create_file_handler, create_console_handler


def get_logger(name: str = "app", area: LogArea = LogArea.GENERAL) -> logging.Logger:
    """
    Create and return a configured logger instance.

    Parameters:
        name (str): Name of the logger.
        area (str): Functional area used for file handler routing.

    Returns:
        logging.Logger: A fully configured logger instance.
    """
    level = int(log_level)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:

        normal_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        json_formatter = JsonFormatter()

        file_formatter = json_formatter if log_json else normal_formatter
        console_formatter = (
            ColorFormatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
            if not log_json else json_formatter
        )

        if log_file:
            file_handler = create_file_handler(area.value, file_formatter)
            if file_handler:
                logger.addHandler(file_handler)

        if log_console:
            console_handler = create_console_handler(console_formatter)
            logger.addHandler(console_handler)

    return logger


def get_category_logger(category: LogCategory) -> logging.Logger:
    """
    Return a logger associated with a specific logical category.

    Parameters:
        category (str): Name representing the logging category.

    Returns:
        logging.Logger: Logger configured for the given category.
    """
    return get_logger(name=category.value, area=LogArea.GENERAL)
