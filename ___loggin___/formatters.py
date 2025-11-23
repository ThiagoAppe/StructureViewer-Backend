import logging
import json


class LogColors:
    """
    ANSI color codes used to colorize console log output.
    """
    RESET = "\033[0m"
    GREY = "\033[90m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD_RED = "\033[91;1m"


class ColorFormatter(logging.Formatter):
    """
    Formatter that applies ANSI color codes based on log level.
    """
    COLORS = {
        logging.DEBUG: LogColors.GREY,
        logging.INFO: LogColors.GREEN,
        logging.WARNING: LogColors.YELLOW,
        logging.ERROR: LogColors.RED,
        logging.CRITICAL: LogColors.BOLD_RED,
    }

    def format(self, record):
        """
        Apply color formatting to the log message.

        Parameters:
            record (LogRecord): Log record containing event information.

        Returns:
            str: Colorized formatted message.
        """
        color = self.COLORS.get(record.levelno, LogColors.RESET)
        message = super().format(record)
        return f"{color}{message}{LogColors.RESET}"


class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs logs in structured JSON format.
    """

    def format(self, record):
        """
        Convert the log record into a JSON string.

        Parameters:
            record (LogRecord): Log record containing event information.

        Returns:
            str: JSON-formatted log entry.
        """
        entry = {
            "time": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage()
        }
        return json.dumps(entry, ensure_ascii=False)
