import logging
import os
from logging.handlers import RotatingFileHandler

LogFolder = "loggin/History"
os.makedirs(LogFolder, exist_ok=True)

log_file_path = os.path.join(LogFolder, "app.log")

def GetLogger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        file_handler = RotatingFileHandler(
            log_file_path, maxBytes=5_000_000, backupCount=3, encoding='utf-8'
        )

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )

        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
