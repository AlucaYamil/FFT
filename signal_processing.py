"""
Módulo: signal_processing.py

Este archivo contiene tanto las instrucciones detalladas para que Codex entienda
el propósito físico y técnico, como el código Python definitivo para aplicar
procesamiento de señal a un array de velocidad tri-axial (en mm/s). El objetivo
es "limpiar" la señal (filtrado bandpass y ventana de Hanning) antes de
calcular la FFT en el siguiente módulo.

--- INSTRUCCIONES PARA CODEX ---
# CONTEXTO:
#   - Se dispone de un array de velocidad en mm/s, generado por conversion.py.
#   - La señal corresponde a vibraciones simuladas a 800 Hz de muestreo.
#   - Se debe preparar la señal para análisis de FFT: eliminar componentes de
#     baja frecuencia (<5 Hz), de alta frecuencia (>400 Hz) y suavizar con
#     ventana de Hanning.
#
# OBJETIVO:
#   - Implementar dos funciones principales:
#     1) apply_hanning_window(signal: np.ndarray) -> np.ndarray
#     2) bandpass_filter(signal: np.ndarray, fs: int, fmin: float, fmax: float) -> np.ndarray
#   - Ambas deben aceptar un array NumPy 2D de forma (N, 3) (ejes X, Y, Z).
#   - El filtrado bandpass se realizará con filtro Butterworth de 4º orden,
#     usando scipy.signal.butter y scipy.signal.filtfilt para minimizar fase.
#
# CONSIDERACIONES FÍSICAS Y TÉCNICAS:
#   1. Sample rate: fs (ej. 800 Hz).
#   2. Filtro pasabanda:
#       - Frecuencia mínima (fmin): 5 Hz (elimina DC y deriva lenta).
#       - Frecuencia máxima (fmax): 400 Hz (criterio de Nyquist).
#       - Orden del filtro: 4 (suficiente para separar bandas sin distorsionar excesivamente).
#   3. Ventana de Hanning:
#       - Se aplica multiplicando la señal completa por la ventana np.hanning(N),
#         donde N = número de muestras.
#       - Para cada eje por separado.
#
# REQUISITOS TÉCNICOS Y DE ESTRUCTURA:
#   - No usar sockets, UDP ni comunicación serial.
#   - No usar librerías de visualización.
#   - Usar únicamente: numpy, scipy.signal.
#   - Validar que la señal tenga dimensión 2 y shape[1] == 3; en caso contrario,
#     lanzar ValueError.
#   - Las constantes del filtro deben definirse con nombres claros:
#       * ORDER = 4
#       * DEFAULT_FMIN = 5.0
#       * DEFAULT_FMAX = 400.0
#   - Cada función debe incluir docstring en español, explicando parámetros,
#     retornos y notas sobre diseño de filtro/ventana.
#   - Incluir un bloque opcional bajo `if __name__ == "__main__":` para pruebas:
#       * Generar señal de prueba (por ejemplo, una suma de senoidales en mm/s).
#       * Aplicar bandpass y ventana.
#       * Imprimir rango de valores antes y después del procesamiento.
#
# ESTRUCTURA FINAL DEL ARCHIVO:
# -------------------------------------------------------------------------------
# (1) Comentario general (como este bloque) con instrucciones para Codex.
# (2) Importar numpy y scipy.signal.
# (3) Definir constantes del filtro:
#       ORDER = 4
#       DEFAULT_FMIN = 5.0
#       DEFAULT_FMAX = 400.0
# (4) Definir la función apply_hanning_window(signal: np.ndarray) -> np.ndarray:
#       - Validar dimensiones.
#       - Crear ventana de Hanning de longitud N.
#       - Multiplicar cada columna (eje) por la ventana.
#       - Devolver señal suavizada (misma forma).
# (5) Definir la función bandpass_filter(signal: np.ndarray, fs: int,
#       fmin: float = DEFAULT_FMIN, fmax: float = DEFAULT_FMAX) -> np.ndarray:
#       - Validar dimensiones.
#       - Calcular frecuencia de Nyquist: nyq = 0.5 * fs.
#       - Si fmax ≥ nyq, ajustarlo a 0.999*nyq.
#       - Normalizar fmin_n = fmin / nyq, fmax_n = fmax / nyq.
#       - Validar que 0 < low < high < 1.
#       - Usar butter(ORDER, [low, high], btype='bandpass', analog=False).
#       - Aplicar filtfilt a cada eje por separado.
#       - Devolver señal filtrada (misma forma).
# (6) Bloque opcional de prueba:
#       if __name__ == "__main__":
#           * Generar señal de prueba de dos senoidales (p.ej., 20 Hz y 300 Hz).
#           * Mostrar min/max antes y después de filtrar y ventana.
# -------------------------------------------------------------------------------
#
# FIN DE INSTRUCCIONES PARA CODEX
"""

import numpy as np
from scipy.signal import butter, filtfilt

# Constantes de configuración del filtro
ORDER = 4
DEFAULT_FMIN = 5.0    # Hz
DEFAULT_FMAX = 400.0  # Hz


def apply_hanning_window(signal: np.ndarray) -> np.ndarray:
    """
    Aplica una ventana de Hanning a una señal tri-axial.

    Parameters
    ----------
    signal : np.ndarray, shape (N, 3)
        Array con la señal en mm/s para los ejes X, Y, Z.

    Returns
    -------
    np.ndarray, shape (N, 3)
        Señal suavizada con la misma forma que la entrada.

    Notes
    -----
    - Se valida que signal.ndim == 2 y signal.shape[1] == 3.
    - Se calcula window = np.hanning(N), donde N = número de muestras.
    - Se multiplica cada columna de la señal por la ventana.
    """
    if signal.ndim != 2 or signal.shape[1] != 3:
        raise ValueError("signal debe ser un array de forma (N, 3)")

    n_samples = signal.shape[0]
    window = np.hanning(n_samples)

    windowed = np.zeros_like(signal, dtype=float)
    for axis in range(3):
        windowed[:, axis] = signal[:, axis] * window

    return windowed


def bandpass_filter(
    signal: np.ndarray,
    fs: int,
    fmin: float = DEFAULT_FMIN,
    fmax: float = DEFAULT_FMAX,
) -> np.ndarray:
    """
    Aplica un filtro Butterworth pasabanda a la señal tri-axial.

    Parameters
    ----------
    signal : np.ndarray, shape (N, 3)
        Array de entrada en mm/s para ejes X, Y, Z.
    fs : int
        Frecuencia de muestreo en Hz (ej. 800).
    fmin : float, optional
        Frecuencia mínima de corte en Hz. Por defecto DEFAULT_FMIN (5 Hz).
    fmax : float, optional
        Frecuencia máxima de corte en Hz. Por defecto DEFAULT_FMAX (400 Hz).

    Returns
    -------
    np.ndarray, shape (N, 3)
        Señal filtrada en mm/s para cada eje.

    Notes
    -----
    - Se calcula la frecuencia de Nyquist: nyq = 0.5 * fs.
    - Si fmax >= nyq, se ajusta a 0.999 * nyq (para que butter acepte high < 1).
    - Se normaliza: low = fmin / nyq, high = fmax / nyq.
    - Se valida que 0 < low < high < 1; en caso contrario, se lanza ValueError.
    - Se diseña un filtro Butterworth de orden ORDER con butter(...).
    - Se aplica filtfilt a cada eje para evitar distorsión de fase.
    """
    # 1) Validar dimensión de entrada
    if signal.ndim != 2 or signal.shape[1] != 3:
        raise ValueError("signal debe ser un array de forma (N, 3)")

    # 2) Calcular frecuencia de Nyquist
    nyq = 0.5 * fs

    # 3) Ajustar fmax si coincide o supera Nyquist
    if fmax >= nyq:
        fmax = nyq * 0.999  # por ejemplo, 399.6 Hz si fs=800

    # 4) Normalizar frecuencias
    low = fmin / nyq
    high = fmax / nyq

    # 5) Validar rango de frecuencias normalizadas
    if not (0 < low < high < 1):
        raise ValueError(
            f"Frecuencias de corte no válidas: fmin={fmin}, fmax={fmax}, nyquist={nyq}"
        )

    # 6) Diseñar filtro Butterworth pasabanda
    b, a = butter(ORDER, [low, high], btype="bandpass", analog=False)

    # 7) Aplicar filtfilt a cada eje
    filtered = np.zeros_like(signal, dtype=float)
    for axis in range(3):
        filtered[:, axis] = filtfilt(b, a, signal[:, axis])

    return filtered


if __name__ == "__main__":
    # Ejemplo de uso rápido para verificar el filtrado y la ventana

    duration = 1.0   # segundos
    fs = 800         # Hz
    samples = int(duration * fs)
    t = np.linspace(0, duration, samples, endpoint=False)

    # Señal de prueba: combinación de 20 Hz y 300 Hz en eje X, ruido en Y y Z
    test_signal = np.zeros((samples, 3))
    test_signal[:, 0] = 1.5 * np.sin(2 * np.pi * 20.0 * t) + 0.5 * np.sin(2 * np.pi * 300.0 * t)
    test_signal[:, 1] = 0.1 * np.random.standard_normal(samples)
    test_signal[:, 2] = 0.1 * np.random.standard_normal(samples)

    print("Rango antes de filtrar (eje X):", test_signal[:, 0].min(), test_signal[:, 0].max())

    # Aplicar filtro pasabanda con fmin=5 Hz, fmax=400 Hz (ajustado internamente)
    filtered_signal = bandpass_filter(test_signal, fs, fmin=5.0, fmax=400.0)
    # Aplicar ventana de Hanning
    windowed_signal = apply_hanning_window(filtered_signal)

    print("Rango después de filtrar y ventana (eje X):", windowed_signal[:, 0].min(), windowed_signal[:, 0].max())
    print("Procesamiento completado")
