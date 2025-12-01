# utils/logger.py
import logging
import os
from typing import Optional

def setup_logger(name: str = "ura", log_file: Optional[str] = None, level: str = "INFO"):
    """
    Configure and return a logger used throughout the application.
    If log_file is provided, logs are also written to that file (rotating not configured for simplicity).
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)

    # avoid adding multiple handlers if called multiple times (e.g., during hot reload)
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    if log_file:
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
