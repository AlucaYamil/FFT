import numpy as np
from settings import HW    # NEW ⟶ acceso a SAMPLE_RATE, LSB_TO_G, etc.

def accel_to_velocity(a_ms2: np.ndarray, dt: float) -> np.ndarray:
    """Integración trapezoidal acumulada → velocidad (m/s)."""
    vel = np.cumsum((a_ms2[1:] + a_ms2[:-1]) * 0.5 * dt, axis=0)
    return np.vstack([np.zeros((1, 3)), vel])

# ───────────────────────── NEW WRAPPER ───────────────────────────
def accel_to_vel_rms(raw_int16: np.ndarray, fs: int = HW.SAMPLE_RATE) -> float:
    """
    Convierte datos crudos ADXL345 (int16) a velocidad RMS en mm/s.
    - raw_int16: ndarray (N,3) con datos ±4 g en cuentas LSB.
    - fs: frecuencia de muestreo en Hz.
    """
    # 1) cuentas → g
    a_g = raw_int16 * HW.LSB_TO_G                           # g
    # 2) g → m/s²
    a_ms2 = a_g * HW.G_TO_MS2                               # m/s² //Aqui integramos aceleracion en velocidad
    # 3) integración a velocidad (m/s)
    dt = 1.0 / fs
    v_ms = accel_to_velocity(a_ms2, dt)
    # 4) magnitud vectorial
    v_mag = np.linalg.norm(v_ms, axis=1)                    # m/s
    # 5) RMS y m/s → mm/s
    vel_rms_mm_s = np.sqrt(np.mean(v_mag**2)) * 1000.0
    return vel_rms_mm_s
# ────────────────────────────────────────────────────────────────
