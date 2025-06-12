"""
Archivo: real_time.py

Este script simula un flujo de datos “en tiempo real”:
- Cada segundo (800 muestras a 800 Hz) genera un bloque de datos nuevos con 
  simulate_vibration_data.
- Convierte ese bloque de aceleraciones a velocidades.
- Aplica filtrado pasabanda + ventana de Hanning sobre ese bloque.
- Calcula la FFT de ese bloque.
- Sobreescribe los archivos velocity.csv y fft_result.csv para que el dashboard
  los lea y actualice sus gráficos.

Para ejecutar en paralelo al dashboard:
    python real_time.py

Requisitos:
- numpy, pandas, scipy, y que 
  y fft_analysis.py estén en la misma carpeta.
"""

import time
import pandas as pd
import numpy as np

from conversion           import acc_to_velocity
from signal_processing    import (
    bandpass_filter,
    apply_hanning_window,
    compute_fft,
)
from storage              import save_velocity_csv, save_fft_csv

# Parámetros de “streaming”
FS = 800             # Hz
DURATION = 1.0       # segundos por bloque (800 muestras)
SLEEP_TIME = 1.0     # segundos entre bloques (puedes ajustar)

def main():
    """
    Bucle infinito que cada SLEEP_TIME segundos genera y procesa un nuevo bloque
    de datos de 1 segundo (800 muestras), y sobreescribe los CSVs usados por el dashboard.
    """
    bloque_id = 0
    while True:
        # 1) Obtener bloque de aceleración (reemplazar con captura real)
        accel = np.zeros((int(DURATION * FS), 3))

        # 2) Convertir a velocidad (mm/s)
        vel = acc_to_velocity(accel, FS)

        # 3) Filtrar y ventana para el bloque completo
        filtered = bandpass_filter(vel, FS)
        windowed = apply_hanning_window(filtered)

        # 4) FFT del bloque
        freqs, amps = compute_fft(windowed, FS)

        # 5) Guardar “velocity.csv” y “fft_result.csv” (sobrescribe cada vez)
        #    Usamos el mismo nombre de archivo cada iteración para que el dashboard lo re-lea.
        try:
            save_velocity_csv(vel, FS, "velocity.csv")
            save_fft_csv(freqs, amps, "fft_result.csv")
        except Exception as e:
            print(f"[ERROR al guardar CSVs] {e}")

        # 6) Mensaje en consola para confirmar que el bloque salió
        print(f"[{time.strftime('%H:%M:%S')}] Bloque #{bloque_id:03d} generado y guardado.")
        bloque_id += 1

        # 7) Dormir antes de la siguiente iteración
        time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    main()