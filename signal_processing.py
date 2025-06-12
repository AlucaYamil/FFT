"""Procesamiento de señales de vibración.

Este módulo unifica filtrado pasabanda, aplicación de ventana de Hanning,

cálculo de RMS y FFT para señales de velocidad en mm/s. Todas las funciones

comparten una frecuencia de muestreo global FS=800 Hz.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, filtfilt

FS = 800  # Hz
ORDER = 4
DEFAULT_FMIN = 5.0
DEFAULT_FMAX = 400.0


def apply_hanning_window(signal: np.ndarray) -> np.ndarray:
    """Aplicar una ventana de Hanning a una señal 1-D o 2-D."""
    arr = np.asarray(signal, dtype=float)
    if arr.ndim == 1:
        window = np.hanning(arr.size)
        return arr * window
    if arr.ndim == 2:
        window = np.hanning(arr.shape[0])[:, None]
        return arr * window
    raise ValueError("signal debe ser un array de 1 o 2 dimensiones")


def bandpass_filter(
    signal: np.ndarray,
    fs: int,
    fmin: float = DEFAULT_FMIN,
    fmax: float = DEFAULT_FMAX,
) -> np.ndarray:
    """Filtrado Butterworth pasabanda para señal tri-axial."""
    if signal.ndim != 2 or signal.shape[1] != 3:
        raise ValueError("signal debe ser un array de forma (N, 3)")

    nyq = 0.5 * fs
    if fmax >= nyq:
        fmax = nyq * 0.999
    low = fmin / nyq
    high = fmax / nyq
    if not (0 < low < high < 1):
        raise ValueError("Frecuencias de corte no válidas")

    b, a = butter(ORDER, [low, high], btype="bandpass", analog=False)
    filtered = np.zeros_like(signal, dtype=float)
    for axis in range(3):
        filtered[:, axis] = filtfilt(b, a, signal[:, axis])
    return filtered


def compute_rms(signal: np.ndarray) -> np.ndarray:
    """Calcular RMS de una señal 1-D o 2-D."""
    arr = np.asarray(signal, dtype=float)
    return np.sqrt(np.mean(arr ** 2, axis=0))


def compute_fft(signal: np.ndarray, fs: int = FS):
    """Obtener frecuencia y amplitud de la FFT de una señal ya en mm/s."""
    arr = np.asarray(signal, dtype=float)
    if arr.ndim == 1:
        N = arr.size
        freqs = np.fft.rfftfreq(N, 1.0 / fs)
        Y = np.fft.rfft(arr)
        mag = np.abs(Y) * (2.0 / N)
        mag[0] = np.abs(Y[0]) / N
        if N % 2 == 0:
            mag[-1] = np.abs(Y[-1]) / N
        return freqs, mag

    if arr.ndim == 2:
        N = arr.shape[0]
        freqs = np.fft.rfftfreq(N, 1.0 / fs)
        amps = np.zeros((freqs.size, arr.shape[1]), dtype=float)
        for axis in range(arr.shape[1]):
            Y = np.fft.rfft(arr[:, axis])
            mag = np.abs(Y) * (2.0 / N)
            mag[0] = np.abs(Y[0]) / N
            if N % 2 == 0:
                mag[-1] = np.abs(Y[-1]) / N
            amps[:, axis] = mag
        return freqs, amps

    raise ValueError("signal debe ser 1-D o 2-D")