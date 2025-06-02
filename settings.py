from dataclasses import dataclass

@dataclass(frozen=True)
class HW:
    SAMPLE_RATE: int = 800          # Hz
    LSB_TO_G: float = 0.0078        # ADXL345 ±4g
    G_TO_MS2: float = 9.80665       # 1 g = 9.80665 m/s²
    DT: float = 1.0 / SAMPLE_RATE   # s

@dataclass(frozen=True)
class UI:
    WINDOW_FFT: int = 1024          # puntos para FFT
    WINDOW_RMS: int = 1024          # puntos para RMS
    ISO_GROUP: str = "G1"           # grupo ISO por defecto
