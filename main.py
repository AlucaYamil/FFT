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

from data_generator import simulate_vibration_data
from conversion import acc_to_velocity
from signal_processing import bandpass_filter, apply_hanning_window
from fft_analysis import compute_fft
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
    # Generar aceleración simulada
    accel = simulate_vibration_data(duration=duration, fs=fs)
    print(f"[1] Datos de aceleración generados: {accel.shape[0]} muestras")
    save_acceleration_csv(accel, fs, "raw_acc.csv")
    print("    • raw_acc.csv guardado")

    # Convertir a velocidad
    vel = acc_to_velocity(accel, fs)
    print("[2] Conversión a velocidad completada")
    save_velocity_csv(vel, fs, "velocity.csv")
    print("    • velocity.csv guardado")

    # Procesamiento de señal: filtrado + ventana
    filtered = bandpass_filter(vel, fs)
    windowed = apply_hanning_window(filtered)
    print("[3] Filtrado pasabanda y ventana aplicados")

    # Calcular FFT
    freqs, amps = compute_fft(windowed, fs)
    print("[4] FFT calculada")

    # Mostrar frecuencia dominante por eje
    for eje, etiqueta in enumerate(("X", "Y", "Z")):
        idx = np.argmax(amps[:, eje])
        print(
            f"      → Eje {etiqueta}: {freqs[idx]:.2f} Hz, "
            f"amplitud {amps[idx, eje]:.4f} mm/s"
        )

    save_fft_csv(freqs, amps, "fft_result.csv")
    print("    • fft_result.csv guardado")
    print("Proceso completo finalizado")


if __name__ == "__main__":
    main()