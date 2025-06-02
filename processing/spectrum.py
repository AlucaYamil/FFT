import numpy as np
from numpy.fft import rfft, rfftfreq
from utils.windows import get_window

def fft_mag(signal: np.ndarray, fs: float, window: str = "hann") -> tuple[np.ndarray,np.ndarray]:
    win   = get_window(window, len(signal))
    spec  = rfft(signal * win)
    mag   = (2/len(signal)) * np.abs(spec)
    freqs = rfftfreq(len(signal), 1/fs)
    return freqs, mag
