import os
import logging

def ensure_log_directory(filename):
    """Ensures the directory for a log file exists."""
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

class SafeFileHandler(logging.FileHandler):
    """A FileHandler that ensures its directory exists."""
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        ensure_log_directory(filename)
        logging.FileHandler.__init__(self, filename, mode, encoding, delay) 