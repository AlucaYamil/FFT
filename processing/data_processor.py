import numpy as np
from processing.kalman_filter import Kalman1D
from processing.integration   import accel_to_velocity
from processing.metrics       import rms, magnitude_mm_s

kf = Kalman1D(q_signal=1e-3, q_bias=1e-5, r_measure=5e-3)

def process_sample(acc_raw: np.ndarray, dt: float) -> tuple[np.ndarray, float, float]:
    s_corr, bias = kf.update(float(acc_raw))
    vel_arr = accel_to_velocity(np.array([s_corr] * 3).reshape(-1, 3), dt)
    vel_mag = np.linalg.norm(vel_arr, axis=1)
    vel_rms = rms(vel_mag)
    vel_mms = magnitude_mm_s(vel_mag)
    return vel_mms, vel_rms, bias