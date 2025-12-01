# utils/network_utils.py
import socket
from typing import Tuple

def check_internet(host: str = "8.8.8.8", port: int = 53, timeout: float = 1.5) -> bool:
    """
    Quick TCP check to determine if the host has network connectivity.
    Not perfect, but good for deciding whether to attempt real API calls.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False
