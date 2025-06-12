"""\
================================================================================
Módulo: fft_analysis.py

Este archivo contiene tanto las instrucciones detalladas para que Codex entienda
el propósito físico y técnico, como el código Python definitivo para calcular la
Transformada Rápida de Fourier (FFT) de una señal tri-axial (en mm/s). El objetivo
es extraer el espectro de frecuencias (positivas) y sus amplitudes para cada eje.

--- INSTRUCCIONES PARA CODEX ---
# CONTEXTO:
#   - Se dispone de un array de señal tri-axial en mm/s, previamente procesada
#     con filtros y ventana de Hanning. Ejemplo: salida de signal_processing.py.
#   - Frecuencia de muestreo: fs (por ejemplo, 800 Hz).
#   - La señal está en el dominio del tiempo; queremos obtener el espectro
#     de frecuencias (magnitud) para diagnóstico de vibraciones.
#
# OBJETIVO:
#   - Implementar la función principal `compute_fft(signal: np.ndarray, fs: int) -> tuple[np.ndarray, np.ndarray]`
#     que reciba:
#       * signal: array NumPy de forma (N, 3) con la señal en mm/s para ejes X, Y, Z.
#       * fs: frecuencia de muestreo en Hz (por ejemplo, 800).
#     y devuelva:
#       * freqs: array de frecuencias positivas (longitud N_fft = N//2 + 1).
#       * amps: array de amplitudes correspondientes, forma (N_fft, 3).
#
# CONSIDERACIONES FÍSICAS Y TÉCNICAS:
#   1. Usar numpy.fft.rfft para señales reales, que devuelve N//2+1 puntos.
#   2. La frecuencia de resolución es Δf = fs / N.
#   3. El vector de frecuencias positivas se obtiene con numpy.fft.rfftfreq(N, 1/fs).
#   4. Para cada eje (columna), calcular:
#        Y = rfft(signal[:, axis])
#        mag = np.abs(Y) * (2 / N)
#      * El factor (2/N) normaliza la amplitud para obtener magnitud real.
#      * Excluir el factor 2 para DC y, si N es par, para la frecuencia Nyquist:
#         - mag[0] = np.abs(Y[0]) / N
#         - Si N par, mag[N//2] = np.abs(Y[N//2]) / N
#   5. La salida `amps` debe contener la magnitud de cada frecuencia positiva para
#      los tres ejes, de forma que amps[:, 0] sean amplitudes eje X, etc.
#
# REQUISITOS TÉCNICOS Y DE ESTRUCTURA:
#   - No usar sockets, UDP ni comunicación serial.
#   - No usar librerías de visualización.
#   - Usar únicamente: numpy.
#   - Validar que `signal` tenga dimensión 2 y shape[1] == 3; en caso contrario,
#     lanzar ValueError.
#   - La variable N (número de muestras) se extrae como signal.shape[0].
#   - Incluir docstring en español, explicando parámetros, retornos y notas sobre
#     normalización de amplitud.
#   - Incluir un bloque opcional bajo `if __name__ == "__main__":` para pruebas:
#       * Generar señal de prueba en mm/s (por ejemplo, senoidal a 23.17 Hz con ruido).
#       * Llamar a compute_fft y mostrar las frecuencias dominantes de cada eje.
#
# ESTRUCTURA FINAL DEL ARCHIVO:
# -------------------------------------------------------------------------------
# (1) Comentario general (como este bloque) con instrucciones para Codex.
# (2) Importar numpy.
# (3) Definir la función compute_fft(signal: np.ndarray, fs: int) -> tuple[np.ndarray, np.ndarray]:
#       - Validar dimensiones.
#       - Obtener N = signal.shape[0].
#       - Calcular freqs = np.fft.rfftfreq(N, 1/fs).
#       - Inicializar amps = np.zeros((len(freqs), 3)).
#       - Para cada eje:
#           * Y = np.fft.rfft(signal[:, axis])
#           * mag = np.abs(Y) * 2 / N
#           * Ajustar mag[0] = np.abs(Y[0]) / N
#           * Si N es par, mag[N//2] = np.abs(Y[N//2]) / N
#           * Asignar amps[:, axis] = mag
#       - Devolver freqs, amps.
# (4) Bloque opcional de prueba:
#       if __name__ == "__main__":
#           * Generar señal test = combinación de senoidales con ruido en mm/s.
#           * Llamar a compute_fft(test, fs).
#           * Encontrar índice de pico máximo en cada eje:
#               idx = np.argmax(amps[:, axis])
#               print(f"Eje X: frecuencia dominante = {freqs[idx]:.2f} Hz, amplitud = {amps[idx,0]:.4f} mm/s")
# -------------------------------------------------------------------------------
#
# FIN DE INSTRUCCIONES PARA CODEX
================================================================================
"""

import numpy as np
from signal_processing import compute_fft


if __name__ == "__main__":
    duration = 1.0
    fs = 800
    N = int(duration * fs)
    t = np.linspace(0, duration, N, endpoint=False)

    test_signal = np.zeros((N, 3))
    test_signal[:, 0] = 5.0 * np.sin(2 * np.pi * 23.17 * t) + 0.5 * np.random.standard_normal(N)
    test_signal[:, 1] = 3.0 * np.sin(2 * np.pi * 46.34 * t) + 0.5 * np.random.standard_normal(N)
    test_signal[:, 2] = 2.0 * np.sin(2 * np.pi * 11.59 * t) + 0.5 * np.random.standard_normal(N)

    freqs, amps = compute_fft(test_signal, fs)

    for axis, label in enumerate(("X", "Y", "Z")):
        idx_peak = np.argmax(amps[:, axis])
        print(
            f"Eje {label}: frecuencia dominante = {freqs[idx_peak]:.2f} Hz, "
            f"amplitud = {amps[idx_peak, axis]:.4f} mm/s"
        )
    print("FFT completada con éxito.")