"""Receptor UDP para adquisición de datos reales."""

from __future__ import annotations

import logging
import socket
import struct
from typing import Tuple

import numpy as np

from settings import HW
from processing.integration import accel_to_vel_rms

logger = logging.getLogger(__name__)
FS_HZ = HW.SAMPLE_RATE


def setup_udp(ip: str, port: int, timeout: float = 0.2) -> socket.socket:
    """Configura el socket UDP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip, port))
    sock.settimeout(timeout)
    logger.debug("[listener_udp] escuchando en puerto %s…", port)
    return sock


def receive_batch(sock: socket.socket) -> Tuple[int | None, np.ndarray | None]:
    """Recibe un paquete de datos."""
    try:
        data, addr = sock.recvfrom(4096)
        logger.debug("[receive_batch] %d bytes from %s", len(data), addr)
        if len(data) < 4:
            logger.debug("[receive_batch] paquete muy corto")
            return None, None
        seq, n = struct.unpack_from("<HH", data, 0)
        expected_bytes = 4 + n * 6
        if len(data) != expected_bytes:
            logger.debug(
                "[receive_batch] ⚠️ tamaño incoherente: esperado %d bytes, llegó %d",
                expected_bytes,
                len(data),
            )
            return None, None
        raw = np.frombuffer(data, dtype="<i2", offset=4).reshape(n, 3)
        vel_rms = accel_to_vel_rms(raw, fs=FS_HZ)
        logger.debug("[receive_batch] seq=%d  n=%d  rms=%.3f mm/s", seq, n, vel_rms)
        return seq, raw
    except socket.timeout:
        return None, None
    except Exception as e:
        logger.debug("[receive_batch] excepción: %s", e)
        return None, None