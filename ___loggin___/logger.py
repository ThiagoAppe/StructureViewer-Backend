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
from .handlers.file import create_file_handler
from .handlers.console import create_console_handler


def get_logger(area: LogArea, category: LogCategory) -> logging.Logger:
    """
    Create and return a configured logger bound to a specific area and category.

    Parameters:
        area (LogArea): Functional/logical area of the application.
        category (LogCategory): Business or domain category.

    Returns:
        logging.Logger: A fully configured logger instance.

    Raises:
        TypeError: If area or category are not valid enum instances.
    """
    if not isinstance(area, LogArea):
        raise TypeError("area must be an instance of LogArea enum")

    if not isinstance(category, LogCategory):
        raise TypeError("category must be an instance of LogCategory enum")

    level = int(log_level)

    logger_name = f"{area.value}.{category.value}"
    logger = logging.getLogger(logger_name)
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
