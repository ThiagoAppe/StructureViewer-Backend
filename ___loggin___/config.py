import os
from dotenv import load_dotenv

load_dotenv()


def _ensure_log_folder(path: str) -> str:
    """
    Ensure that the log folder exists. Create it if missing.

    Parameters:
        path (str): Directory path for storing log files.

    Returns:
        str: Validated directory path.
    """
    os.makedirs(path, exist_ok=True)
    return path


log_folder = _ensure_log_folder(os.getenv("LOG_FOLDER", "loggin/history"))

log_level = os.getenv("LOG_LEVEL", "10")
log_console = os.getenv("LOG_CONSOLE", "true").lower() == "true"
log_file = os.getenv("LOG_FILE", "true").lower() == "true"
log_json = os.getenv("LOG_JSON", "false").lower() == "true"
log_rotate_daily = os.getenv("LOG_ROTATE_DAILY", "false").lower() == "true"
log_rotate_size = int(os.getenv("LOG_ROTATE_SIZE", 5_000_000))
log_daily_backup = int(os.getenv("LOG_DAILY_BACKUP", 7))
log_size_backup = int(os.getenv("LOG_SIZE_BACKUP", 5))
log_encrypt = os.getenv("LOG_ENCRYPT", "false").lower() == "true"
