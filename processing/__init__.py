import logging
from typing import Any, Dict

import numpy as np

from settings import HW
from .integration import accel_to_velocity
from .metrics import rms, magnitude_mm_s

logger = logging.getLogger(__name__)


def signal_pipeline(raw: np.ndarray) -> Dict[str, Any]:
    """Convierte muestras crudas en métricas de velocidad."""
    acc = raw * HW.LSB_TO_G * HW.G_TO_MS2
    vel = accel_to_velocity(acc, HW.DT)
    vel_mag = np.linalg.norm(vel, axis=1)
    vel_mm_s = magnitude_mm_s(vel_mag)
    return {
        "acc_ms2": acc,
        "vel_ms": vel,
        "vel_mm_s": vel_mm_s,
        "rms": rms(vel_mm_s),
    }