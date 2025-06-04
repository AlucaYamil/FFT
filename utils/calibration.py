import numpy as np
from processing.metrics import rms


def calc_velocity_bias(window: np.ndarray) -> dict:
    mean_off = float(np.mean(window))
    rms_off = float(rms(window - mean_off))
    return {"mean": mean_off, "rms": rms_off}


def apply_velocity_bias(signal: np.ndarray, bias: dict) -> np.ndarray:
    return signal - bias.get("mean", 0.0)