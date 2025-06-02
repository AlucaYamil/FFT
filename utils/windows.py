import numpy as np

def get_window(kind: str, N: int) -> np.ndarray:
    if kind == "hann":
        return 0.5 - 0.5 * np.cos(2*np.pi * np.arange(N) / N)
    return np.ones(N)