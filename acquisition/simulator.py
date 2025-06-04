"""Generador de muestras simuladas para desarrollo."""

from __future__ import annotations

import numpy as np

from settings import HW

_SEQ = 0
_BIAS = np.array([20, -10, 5], dtype=np.int16)


def setup_udp(ip: str = "0.0.0.0", port: int = 9000, timeout: float = 0.2) -> None:
    """Mantiene compatibilidad con la API de ``udp_receiver``."""
    return None


def receive_batch(
    _sock: None | object = None, n: int = 128, freq: float = 30.0
) -> tuple[int, np.ndarray]:
    """Genera un lote simulado de muestras ADXL345."""
    global _SEQ
    t = np.arange(n) / HW.SAMPLE_RATE
    amplitude = 128  # ~1 g en cuentas LSB
    signal = amplitude * np.sin(2 * np.pi * freq * t)
    noise = np.random.normal(0, 3, size=(n, 3))
    raw = signal.reshape(n, 1) + _BIAS + noise
    seq = _SEQ
    _SEQ = (_SEQ + 1) % 65536
    return seq, raw.astype(np.int16)