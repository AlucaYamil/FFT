import numpy as np

def accel_to_velocity(a_ms2: np.ndarray, dt: float) -> np.ndarray:
    vel = np.cumsum((a_ms2[1:] + a_ms2[:-1]) * 0.5 * dt, axis=0)
    return np.vstack([np.zeros((1,3)), vel])
