"""Módulo: conversion.py

Este archivo contiene tanto las instrucciones detalladas para que Codex entienda
el propósito físico y técnico, como el código Python definitivo para convertir
una señal de aceleración tri-axial (en g) a velocidad tri-axial (en mm/s) usando
integración trapezoidal.

--- INSTRUCCIONES PARA CODEX ---
# CONTEXTO:
#   - Se dispone de un array de aceleración en g, generado por data_generator.py.
#   - La señal simula un motor trifásico de 1390 RPM (~23.17 Hz), con fallas mecánicas.
#   - Cada muestra representa aceleración en g para los ejes X, Y y Z.
#   - Frecuencia de muestreo: 800 Hz.
#
# OBJETIVO:
#   - Crear la función principal `acc_to_velocity(accel_array: np.ndarray, fs: int) -> np.ndarray`
#     que reciba:
#       * accel_array: array NumPy de forma (N, 3), con valores de aceleración en g.
#       * fs: frecuencia de muestreo en Hz (e.g., 800).
#     y devuelva:
#       * velocity_array: array NumPy de forma (N, 3), con velocidad en mm/s para cada eje.
#
# CONSIDERACIONES FÍSICAS:
#   1. Conversión g → m/s²: 1 g = 9.80665 m/s².
#   2. Integración de la aceleración (m/s²) para obtener velocidad (m/s):
#        v[n] = v[n-1] + 0.5 * (a[n] + a[n-1]) * dt,  con dt = 1/fs.
#      Asumir v[0] = 0 (sin velocidad inicial).
#   3. Conversión m/s → mm/s: multiplicar por 1000.
#   4. No corregir deriva de manera explícita; dado que la señal simulada parte con valor medio cero,
#      asumimos deriva despreciable. Si en el futuro aparece deriva, bastaría restar la media o aplicar
#      un filtro de paso alto muy bajo.
#
# REQUISITOS TÉCNICOS Y DE ESTRUCTURA:
#   - No utilizar sockets, UDP ni comunicación serial.
#   - No usar librerías de visualización (matplotlib, plotly, etc.).
#   - Usar únicamente: numpy.
#   - Validar que accel_array tenga dimensión 2 y shape[1] == 3; en caso contrario, lanzar ValueError.
#   - Todas las constantes físicas deben definirse con nombres claros:
#       * G_TO_M_S2 = 9.80665
#       * M_S_TO_MM_S = 1000.0
#   - Incluir un bloque opcional bajo `if __name__ == "__main__":` para pruebas rápidas:
#       * Generar una señal senoidal de prueba (p.ej., 0.01 g a 23.17 Hz en eje X).
#       * Llamar a acc_to_velocity y mostrar en consola las primeras 10 muestras de velocidad.
#   - La función debe incluir docstring en español, explicando parámetros, retornos y notas sobre deriva.
#
# ESTRUCTURA FINAL DEL ARCHIVO:
# ---------------------------------------------------------------------------------------------------
# (1) Comentario general (como este bloque) con instrucciones para Codex.
# (2) Importar numpy.
# (3) Definir constantes de conversión:
#       G_TO_M_S2 = 9.80665
#       M_S_TO_MM_S = 1000.0
# (4) Definir la función acc_to_velocity(accel_array: np.ndarray, fs: int) -> np.ndarray:
#       - Validar dimensiones.
#       - Inicializar vel_array con ceros (N, 3).
#       - Para cada eje:
#           * Convertir accel (g) → accel_ms2.
#           * Integrar con trapezoidal → axis_vel (m/s).
#           * axis_vel_mm_s = axis_vel * M_S_TO_MM_S.
#           * Guardar en vel_array[:, eje].
#       - Devolver vel_array.
# (5) Bloque opcional de prueba:
#       if __name__ == "__main__":
#           * Generar accel_test = senoidal en g (eje X) a 23.17 Hz.
#           * Llamar a acc_to_velocity para ver output.
#           * Imprimir primeras 10 muestras de vel en mm/s.
# ---------------------------------------------------------------------------------------------------
#
# FIN DE INSTRUCCIONES PARA CODEX
"""

import numpy as np

# Constantes de conversión
G_TO_M_S2 = 9.80665  # 1 g = 9.80665 m/s²
M_S_TO_MM_S = 1000.0  # 1 m/s = 1000 mm/s


def acc_to_velocity(accel_array: np.ndarray, fs: int) -> np.ndarray:
    """Convierte un array de aceleraciones en g a velocidades en mm/s por eje.

    Parameters
    ----------
    accel_array : np.ndarray
        Array de forma ``(N, 3)`` con aceleraciones en g.
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    np.ndarray
        Array de forma ``(N, 3)`` con velocidades en mm/s.

    Notes
    -----
    Se asume velocidad inicial cero. La integración se realiza con el
    método trapezoidal y no se aplica ninguna corrección de deriva.
    """
    # Validar dimensiones de entrada
    if accel_array.ndim != 2 or accel_array.shape[1] != 3:
        raise ValueError("accel_array debe ser un array de forma (N, 3)")

    samples = accel_array.shape[0]
    dt = 1.0 / fs

    vel_array = np.zeros((samples, 3), dtype=float)

    for axis in range(3):
        # Convertir g a m/s²
        accel_ms2 = accel_array[:, axis] * G_TO_M_S2

        # Integración trapezoidal
        vel_ms = np.zeros(samples, dtype=float)
        for n in range(1, samples):
            vel_ms[n] = vel_ms[n - 1] + 0.5 * (
                accel_ms2[n] + accel_ms2[n - 1]
            ) * dt

        # Convertir a mm/s
        vel_array[:, axis] = vel_ms * M_S_TO_MM_S

    return vel_array


if __name__ == "__main__":
    # Prueba rápida con una senoidal de 0.01 g a 23.17 Hz en eje X
    dur = 1.0
    fs = 800
    t = np.linspace(0, dur, int(dur * fs), endpoint=False)

    accel_test = np.zeros((t.size, 3))
    accel_test[:, 0] = 0.01 * np.sin(2 * np.pi * 23.17 * t)

    vel_test = acc_to_velocity(accel_test, fs)

    print("Primeras 10 muestras de velocidad (mm/s):")
    for i in range(10):
        print(f"{i:2d}: {vel_test[i, 0]:.4f} mm/s")