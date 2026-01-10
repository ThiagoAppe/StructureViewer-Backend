import os
import shutil
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class area_rotating_file_handler(RotatingFileHandler):
    def __init__(self, area: str, history_root: str, *args, **kwargs):
        self.area = area
        self.history_root = history_root
        super().__init__(*args, **kwargs)

    def doRollover(self):
        super().doRollover()

        area_history_path = os.path.join(self.history_root, self.area)
        os.makedirs(area_history_path, exist_ok=True)

        base_name = os.path.basename(self.baseFilename)
        log_dir = os.path.dirname(self.baseFilename)

        for filename in os.listdir(log_dir):
            if filename.startswith(base_name + "."):
                src = os.path.join(log_dir, filename)
                dst = os.path.join(area_history_path, filename)
                if not os.path.exists(dst):
                    shutil.move(src, dst)


class area_timed_rotating_file_handler(TimedRotatingFileHandler):
    def __init__(self, area: str, history_root: str, *args, **kwargs):
        self.area = area
        self.history_root = history_root
        super().__init__(*args, **kwargs)

    def doRollover(self):
        super().doRollover()

        area_history_path = os.path.join(self.history_root, self.area)
        os.makedirs(area_history_path, exist_ok=True)

        base_name = os.path.basename(self.baseFilename)
        log_dir = os.path.dirname(self.baseFilename)

        for filename in os.listdir(log_dir):
            if filename.startswith(base_name + "."):
                src = os.path.join(log_dir, filename)
                dst = os.path.join(area_history_path, filename)
                if not os.path.exists(dst):
                    shutil.move(src, dst)
