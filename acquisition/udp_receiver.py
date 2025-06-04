import logging
import socket
import struct

import numpy as np

from settings import HW
from processing.integration import accel_to_vel_rms

logger = logging.getLogger(__name__)
FS_HZ = HW.SAMPLE_RATE


def setup_udp(ip: str, port: int, timeout: float = 0.2):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip, port))
    sock.settimeout(timeout)
    logger.debug("[listener_udp] escuchando en puerto %s…", port)
    return sock


def receive_batch(sock):
    """
    Recibe un paquete UDP:
      - 4 bytes Seq (uint32 LE)
      - N muestras de int16 LE en tramas [x,y,z]
    """
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
        raw = np.frombuffer(data, dtype="<i2", offset=4)
        raw = raw.reshape(n, 3)

        vel_rms = accel_to_vel_rms(raw, fs=FS_HZ)
        logger.debug("[receive_batch] seq=%d  n=%d  rms=%.3f mm/s", seq, n, vel_rms)
        seq = struct.unpack_from("<I", data, 0)[0]
        payload = data[4:]
        if len(payload) % 6 != 0:
            logger.debug(
                "[receive_batch] payload len %d no es múltiplo de 6",
                len(payload),
            )
            return seq, None
        count = len(payload) // 2
        vals = struct.unpack("<" + "h" * count, payload)
        raw = np.array(vals, dtype=np.int16).reshape(-1, 3)
        logger.debug("[receive_batch] parsed raw.shape = %s", raw.shape)
        return seq, raw
    except socket.timeout:
        return None, None
    except Exception as e:
        logger.debug("[receive_batch] excepción: %s", e)
        return None, None