"""Interfaz de adquisición de datos."""

from __future__ import annotations

import logging
from typing import Tuple
import socket

import numpy as np

from config import SIMULATED

logger = logging.getLogger(__name__)

if SIMULATED == 1:
    from . import simulator as backend
else:
    from . import udp_receiver as backend

_sock: socket.socket | None = None


def setup(ip: str = "0.0.0.0", port: int = 9000, timeout: float = 0.2) -> None:
    """Prepara la fuente de datos."""
    global _sock
    if SIMULATED == 0:
        _sock = backend.setup_udp(ip, port, timeout)
    else:
        _sock = None
    logger.debug("acquisition backend=%s", backend.__name__)


def get_samples() -> Tuple[int | None, np.ndarray | None]:
    """Obtiene un lote de muestras."""
    return backend.receive_batch(_sock)


__all__ = ["setup", "get_samples"]