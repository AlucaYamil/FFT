"""Archivo principal del pipeline de vibraciones.

Este script ejecuta la simulación completa de datos de vibración y su posterior
procesamiento. Las etapas son:

1. Generación de aceleraciones en g con ``simulate_vibration_data``.
2. Conversión de aceleración a velocidad en mm/s mediante ``acc_to_velocity``.
3. Filtrado pasabanda y aplicación de ventana de Hanning.
4. Cálculo de la FFT para obtener el espectro de frecuencias.
5. Almacenamiento de todos los resultados en archivos CSV.

Cada paso informa en consola su progreso y muestra la frecuencia dominante por
cada eje.
"""

from __future__ import annotations

import numpy as np

from conversion import acc_to_velocity
from signal_processing import (
    bandpass_filter,
    apply_hanning_window,
    compute_fft,
)
from storage import (
    save_acceleration_csv,
    save_velocity_csv,
    save_fft_csv,
)

# Parámetros globales
duration = 1.0  # segundos
fs = 800        # Hz


def main() -> None:
    """Ejecutar el pipeline completo de análisis de vibraciones."""
    # Datos de aceleración de entrada (reemplazar con captura real)
    accel = np.zeros((int(duration * fs), 3))
    print(f"[1] Datos de aceleración generados: {accel.shape[0]} muestras")
    save_acceleration_csv(accel, fs, "raw_acc.csv")
    print("    • raw_acc.csv guardado")

    # Convertir a velocidad
    vel = acc_to_velocity(accel, fs)
    print("[2] Conversión a velocidad completada")
    save_velocity_csv(vel, fs, "velocity.csv")
    print("    • velocity.csv guardado")