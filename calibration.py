import numpy as np

FS = 800  # Hz

class Calibration:
    """Gestiona el cálculo de un offset promedio de velocidad."""

    def __init__(self, duration_s: float = 2.0):
        self.samples_required = int(duration_s * FS)
        self.offset = np.zeros(3, dtype=float)
        self._data: list[np.ndarray] = []
        self.capturing = False

    def start_capture(self) -> None:
        """Iniciar la captura de datos para calibrar."""
        self._data.clear()
        self.capturing = True

    def add_sample(self, sample: np.ndarray) -> None:
        """Agregar una nueva muestra de velocidad."""
        if self.capturing:
            self._data.append(sample)
            if len(self._data) >= self.samples_required:
                self.capturing = False

    def is_complete(self) -> bool:
        """Comprobar si ya se reunieron los datos suficientes."""
        return not self.capturing and len(self._data) >= self.samples_required

    def compute_offset(self) -> np.ndarray:
        """Calcular y almacenar el offset medio."""
        if not self.is_complete():
            raise RuntimeError("Calibración incompleta")
        arr = np.vstack(self._data)
        self.offset = np.mean(arr, axis=0)
        self._data.clear()
        return self.offset


calibration = Calibration()