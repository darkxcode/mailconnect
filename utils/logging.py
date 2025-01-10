import os
import logging
from logging.handlers import RotatingFileHandler

class SafeFileHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay) 