import datetime
import os

# Logging functionality
class Logger:
    """Handles logging to files"""
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        # make sure log directory exists
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def get_log_path(self, resource_name: str) -> str:
        return os.path.join(self.log_dir, f"{resource_name}.log")

    def log(self, resource_name: str, message: str):
        """Write a log entry"""
        timestamp = datetime.datetime.now().strftime("%I:%M %p")
        log_entry = f"[{timestamp}] {message}"

        with open(self.get_log_path(resource_name), "a") as f:
            f.write(log_entry + "\n")