"""
Módulo: storage.py

Este archivo contiene tanto las instrucciones detalladas para que Codex entienda
el propósito técnico y funcional, como el código Python definitivo para guardar
datos procesados en archivos CSV. Se encargará de almacenar:

  1) Datos de aceleración cruda (g) si es necesario.
  2) Datos de velocidad (mm/s) resultantes de conversion.py.
  3) Resultados de FFT (frecuencias y amplitudes) de fft_analysis.py.

Cada función debe generar un CSV con encabezado adecuado, para facilitar su
lectura en etapas posteriores o en el dashboard.

--- INSTRUCCIONES PARA CODEX ---
# CONTEXTO:
#   - El proyecto genera tres tipos de datos a lo largo del pipeline:
#       a) Aceleración cruda en g: np.ndarray (N, 3)
#       b) Velocidad en mm/s: np.ndarray (N, 3)
#       c) Resultados de FFT:
#           - freqs: np.ndarray (N_fft,)
#           - amps: np.ndarray (N_fft, 3)
#   - Se desea almacenar cada uno en un archivo CSV distinto, con columnas
#     bien etiquetadas para facilitar posteriores análisis.
#
# OBJETIVO:
#   - Implementar estas funciones principales:
#       1) save_acceleration_csv(accel_array: np.ndarray, fs: int, filename: str) -> None
#       2) save_velocity_csv(vel_array: np.ndarray, fs: int, filename: str) -> None
#       3) save_fft_csv(freqs: np.ndarray, amps: np.ndarray, filename: str) -> None
#   - Cada función debe:
#       * Validar dimensiones de los arrays de entrada.
#       * Crear un encabezado en la primera fila, con nombres de columna:
#           - Para aceleración/velocidad: "time","ax","ay","az" (o vx/vy/vz)
#           - Para FFT: "frequency","amp_x","amp_y","amp_z"
#       * Incluir la columna "time" en aceleración/velocidad si se provee fs:
#           - time[k] = k / fs, donde k es índice de muestra (0 ≤ k < N).
#       * Guardar los datos en CSV usando pandas.DataFrame.to_csv.
#   - No usar librerías de visualización ni sockets.
#   - Usar únicamente: numpy y pandas.
#   - Generar ficheros legibles: valores separados por coma, sin índices de pandas.
#
# REQUISITOS TÉCNICOS Y DE ESTRUCTURA:
#   - Funciones deben tener docstring en español explicando parámetros y estructura
#     del CSV resultante.
#   - Si accel_array o vel_array no tienen forma (N, 3), lanzar ValueError.
#   - Si freqs es 1D y amps tiene forma (N_fft, 3), validar que freqs.shape[0] == amps.shape[0].
#   - Generar CSV con encabezado y con 6 decimales de precisión para floats.
#   - Incluir un bloque opcional bajo `if __name__ == "__main__":` para pruebas:
#       * Generar datos de ejemplo (p.ej., usar simulate_vibration_data + acc_to_velocity +
#         compute_fft).
#       * Llamar a las tres funciones para generar: "raw_acc.csv","velocity.csv","fft.csv"
# -------------------------------------------------------------------------------
#
# FIN DE INSTRUCCIONES PARA CODEX
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def save_acceleration_csv(accel_array: np.ndarray, fs: int, filename: str) -> None:
    """Guardar aceleraciones tri-axiales en un archivo CSV.

    Parameters
    ----------
    accel_array : np.ndarray, shape (N, 3)
        Datos de aceleración en g por eje.
    fs : int
        Frecuencia de muestreo en Hz.
    filename : str
        Ruta del archivo CSV de salida.

    Notas
    -----
    El archivo resultante contiene las columnas:
    "time", "ax", "ay", "az".
    El tiempo se calcula como ``k / fs`` y los valores se guardan con
    seis decimales de precisión.
    """
    if accel_array.ndim != 2 or accel_array.shape[1] != 3:
        raise ValueError("accel_array debe tener forma (N, 3)")

    N = accel_array.shape[0]
    times = np.arange(N) / fs
    df = pd.DataFrame({
        "time": times,
        "ax": accel_array[:, 0],
        "ay": accel_array[:, 1],
        "az": accel_array[:, 2],
    })
    df.to_csv(filename, index=False, float_format="%.6f")


def save_velocity_csv(vel_array: np.ndarray, fs: int, filename: str) -> None:
    """Guardar velocidades tri-axiales en un archivo CSV.

    Parameters
    ----------
    vel_array : np.ndarray, shape (N, 3)
        Velocidades en mm/s por eje.
    fs : int
        Frecuencia de muestreo en Hz.
    filename : str
        Ruta del archivo CSV de salida.

    Notas
    -----
    El archivo resultante contiene las columnas:
    "time", "vx", "vy", "vz". El tiempo se calcula como ``k / fs`` y los
    valores se guardan con seis decimales de precisión.
    """
    if vel_array.ndim != 2 or vel_array.shape[1] != 3:
        raise ValueError("vel_array debe tener forma (N, 3)")

    N = vel_array.shape[0]
    times = np.arange(N) / fs
    df = pd.DataFrame({
        "time": times,
        "vx": vel_array[:, 0],
        "vy": vel_array[:, 1],
        "vz": vel_array[:, 2],
    })
    df.to_csv(filename, index=False, float_format="%.6f")


def save_fft_csv(freqs: np.ndarray, amps: np.ndarray, filename: str) -> None:
    """Guardar resultados de FFT en un archivo CSV.

    Parameters
    ----------
    freqs : np.ndarray, shape (N_fft,)
        Vector de frecuencias positivas en Hz.
    amps : np.ndarray, shape (N_fft, 3)
        Amplitudes normalizadas para cada eje (mm/s).
    filename : str
        Ruta del archivo CSV de salida.

    Notas
    -----
    El archivo resultante contiene las columnas:
    "frequency", "amp_x", "amp_y", "amp_z".
    Se verifica que ``freqs`` y ``amps`` tengan la misma longitud.
    """
    if freqs.ndim != 1:
        raise ValueError("freqs debe ser un vector 1D")
    if amps.ndim != 2 or amps.shape[1] != 3 or amps.shape[0] != freqs.shape[0]:
        raise ValueError("amps debe tener forma (N_fft, 3) y coincidir con freqs")

    df = pd.DataFrame({
        "frequency": freqs,
        "amp_x": amps[:, 0],
        "amp_y": amps[:, 1],
        "amp_z": amps[:, 2],
    })
    df.to_csv(filename, index=False, float_format="%.6f")


if __name__ == "__main__":
    # Prueba rápida del módulo
    #from data_generator import simulate_vibration_data
    from conversion import acc_to_velocity
    from signal_processing import (
        bandpass_filter,
        apply_hanning_window,
        compute_fft,
    )

    duration = 1.0
    fs = 800
    #accel = simulate_vibration_data(duration, fs)
    #save_acceleration_csv(accel, fs, "raw_acc.csv")
    #velocity = acc_to_velocity(accel, fs)
    #save_velocity_csv(velocity, fs, "velocity.csv")

    #filtered = bandpass_filter(velocity, fs)
    #windowed = apply_hanning_window(filtered)
    #freqs, amps = compute_fft(windowed, fs)
    #save_fft_csv(freqs, amps, "fft.csv")

    print("Archivos CSV generados correctamente.")