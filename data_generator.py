"""Data generator for simulated acceleration signals of a three-phase motor.

This module provides :func:`simulate_vibration_data` which synthesizes vibration
signals for three axes (X, Y, Z) representing a three-phase motor spinning at
1390 RPM (~23.17 Hz). It embeds typical mechanical fault frequencies and white
noise for testing signal-processing pipelines.

Frequencies included in the simulation:
- Mechanical looseness (0.5X): 11.59 Hz, amplitude 0.02 g (Z axis)
- Unbalance (1X): 23.17 Hz, amplitude 0.05 g (X axis)
- Misalignment (2X): 46.34 Hz, amplitude 0.03 g (Y and Z axes)

Each axis also includes white noise of ±0.01 g. The function returns an array of
shape ``(samples, 3)`` containing the synthetic acceleration in g for the
specified duration and sampling rate.
"""

from __future__ import annotations

import numpy as np


# -- INICIO CAMBIO

def simulate_vibration_data(duration: float = 1.0, fs: int = 800) -> np.ndarray:
    """Simulate tri-axial vibration data for a motor with mechanical faults.

    Parameters
    ----------
    duration : float, optional
        Length of the signal in seconds. Default is 1 second.
    fs : int, optional
        Sampling frequency in Hz. Default is 800 Hz.

    Returns
    -------
    np.ndarray
        Array of shape ``(duration*fs, 3)`` containing acceleration values in g
        for axes X, Y and Z.
    """
    samples = int(duration * fs)
    t = np.linspace(0, duration, samples, endpoint=False)

    # Fault frequencies in Hz
    looseness_freq = 11.59  # 0.5X
    unbalance_freq = 23.17  # 1X
    misalignment_freq = 46.34  # 2X

    # Amplitudes in g
    amp_looseness = 0.02
    amp_unbalance = 0.05
    amp_misalignment = 0.03

    # Generate individual fault components
    x_signal = amp_unbalance * np.sin(2 * np.pi * unbalance_freq * t)
    y_signal = amp_misalignment * np.sin(2 * np.pi * misalignment_freq * t)
    z_signal = (
        amp_looseness * np.sin(2 * np.pi * looseness_freq * t)
        + amp_misalignment * np.sin(2 * np.pi * misalignment_freq * t)
    )

    # Add white noise to each axis
    noise_level = 0.01
    rng = np.random.default_rng()
    x_signal += noise_level * rng.standard_normal(samples)
    y_signal += noise_level * rng.standard_normal(samples)
    z_signal += noise_level * rng.standard_normal(samples)

    data = np.column_stack((x_signal, y_signal, z_signal))
    return data

# -- FIN CAMBIO

__all__ = ["simulate_vibration_data"]