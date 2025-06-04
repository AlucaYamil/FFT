import numpy as np
from scipy.signal import butter, lfilter


def design_hp(fs: float, fc: float = 5.0, order: int = 2):
    return butter(order, fc, fs=fs, btype="high", output="ba")


def apply_hp(x: np.ndarray, fs: float, fc: float = 5.0, order: int = 2) -> np.ndarray:
    b, a = design_hp(fs, fc, order)
    return lfilter(b, a, x, axis=0)