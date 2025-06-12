import os
import sys
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from signal_processing import FS, apply_hanning_window, compute_fft, compute_rms

def test_fft_rms():
    t = np.arange(256) / FS
    sig = np.sin(2 * np.pi * 5 * t)
    freqs, amp = compute_fft(apply_hanning_window(sig), FS)
    idx = np.argmax(amp)
    assert abs(freqs[idx] - 5) < 2
    rms = compute_rms(sig)
    assert np.isclose(rms, 1 / np.sqrt(2), atol=0.1)