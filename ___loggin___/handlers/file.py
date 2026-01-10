import os

from .file_rotation import (
    area_rotating_file_handler,
    area_timed_rotating_file_handler
)

from ..config import (
    log_file,
    log_folder,
    log_history_folder,
    log_rotate_daily,
    log_rotate_size,
    log_daily_backup,
    log_size_backup
)


def create_file_handler(area: str, formatter):
    if not log_file:
        return None

    path = os.path.join(log_folder, f"{area}.log")

    if log_rotate_daily:
        handler = area_timed_rotating_file_handler(
            area=area,
            history_root=log_history_folder,
            filename=path,
            when="midnight",
            backupCount=log_daily_backup,
            encoding="utf-8"
        )
    else:
        handler = area_rotating_file_handler(
            area=area,
            history_root=log_history_folder,
            filename=path,
            maxBytes=log_rotate_size,
            backupCount=log_size_backup,
            encoding="utf-8"
        )

    handler.setFormatter(formatter)
    return handler
