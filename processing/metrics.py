import numpy as np

def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(x))))

def magnitude_mm_s(v_ms: np.ndarray) -> np.ndarray:
    return v_ms * 1_000.0
