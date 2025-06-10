"""
UDPReceiver: recibe paquetes UDP de 100 bytes enviados por el ESP32-ADXL345
Formato: <seq:uint16><cnt:uint16><16*(x:int16,y:int16,z:int16)>
Exponemos:
    - Clase UDPReceiver (igual que antes, ahora con get_next)
    - Función get_packet(timeout=0.05) para consumo directo del dashboard
"""

from __future__ import annotations

import os
import socket
import struct
import time
import threading
import pandas as pd
import numpy as np   # ← nuevo para devolver ndarray

# ──── 1. CONFIGURACIÓN ─────────────────────────────────────────────

UDP_IP   = "0.0.0.0"   # escucha en todas las interfaces
UDP_PORT = 5005       # mismo puerto configurado en el ESP32

BATCH_SIZE   = 16
HEADER_FMT   = "<HH"                         # seq, count
SAMPLE_FMT   = "<" + "hhh" * BATCH_SIZE      # 16 tríadas int16
HEADER_SIZE  = struct.calcsize(HEADER_FMT)   # 4
PACKET_SIZE  = HEADER_SIZE + struct.calcsize("hhh") * BATCH_SIZE  # 100 bytes

OUTPUT_CSV            = None                # None = no guardar CSV
TIMEOUT_THRESHOLD     = 2.0
HEALTH_CHECK_INTERVAL = 1.0

# ──── 2. CLASE UDPReceiver ─────────────────────────────────────────

class UDPReceiver:
    """
    - Recibe paquetes UDP y valida tamaño / formato
    - Desempaqueta las 16 muestras (X,Y,Z) en ndarray int16 shape (16,3)
    - Guarda CSV opcional
    - Expone get_next(timeout) para obtener la última trama recibida
    """

    def __init__(self, ip: str, port: int, output_csv: str | None = OUTPUT_CSV):
        self.ip           = ip
        self.port         = port
        self.output_csv   = output_csv
        self.sock         = None
        self.running      = False

        self.last_seq            = None
        self.last_received_time  = None
        self.alerted             = False

        # Datos para get_next()
        self._last_arr: np.ndarray | None = None
        self._last_seq: int | None        = None
        self._lock = threading.Lock()

        if self.output_csv and not os.path.exists(self.output_csv):
            pd.DataFrame(columns=["timestamp", "seq", "sample_idx", "x", "y", "z"])\
              .to_csv(self.output_csv, index=False)

    # ── API pública ────────────────────────────────────────────────
    def start(self):
        self.running = True
        threading.Thread(target=self._run,           daemon=True).start()
        threading.Thread(target=self._health_monitor, daemon=True).start()
        print(f"[UDPReceiver] Escuchando en {self.ip}:{self.port}")

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
            print("[UDPReceiver] Socket cerrado.")

    def get_next(self, timeout: float = 0.05):
        """
        Bloquea hasta 'timeout' s máx. Devuelve (seq:int, ndarray 16×3).
        Lanza socket.timeout si no llega nada.
        """
        start = time.time()
        while True:
            with self._lock:
                if self._last_arr is not None:
                    return self._last_seq, self._last_arr.copy()
            if time.time() - start > timeout:
                raise socket.timeout
            time.sleep(0.002)

    # ── Hilos internos ────────────────────────────────────────────
    def _run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.ip, self.port))
            while self.running:
                packet, _ = self.sock.recvfrom(1024)

                if len(packet) != PACKET_SIZE:
                    print(f"[WARN] Tamaño {len(packet)} ≠ {PACKET_SIZE}. Ignorado.")
                    continue

                seq, count = struct.unpack_from(HEADER_FMT, packet, 0)
                if count != BATCH_SIZE:
                    print(f"[WARN] 'count' {count} ≠ {BATCH_SIZE}")

                samples = struct.unpack_from(SAMPLE_FMT, packet, HEADER_SIZE)
                arr = np.array(samples, dtype=np.int16).reshape(BATCH_SIZE, 3)

                # actualizar marca temporal y cache para get_next()
                with self._lock:
                    self._last_arr  = arr
                    self._last_seq  = seq
                self.last_received_time = time.time()

                # CSV opcional
                if self.output_csv:
                    base_ts = int(self.last_received_time * 1000)
                    df = pd.DataFrame([{
                        "timestamp":  base_ts,
                        "seq":        int(seq),
                        "sample_idx": i,
                        "x": int(arr[i,0]), "y": int(arr[i,1]), "z": int(arr[i,2])
                    } for i in range(BATCH_SIZE)])
                    df.to_csv(self.output_csv, mode="a", header=False, index=False)

        except Exception as e:
            print(f"[ERROR] UDPReceiver _run: {e}")
        finally:
            if self.sock:
                self.sock.close()

    def _health_monitor(self):
        while self.running:
            time.sleep(HEALTH_CHECK_INTERVAL)
            if self.last_received_time is None:
                if not self.alerted:
                    print("[HEALTH] Aún no llegan paquetes.")
                    self.alerted = True
                continue
            elapsed = time.time() - self.last_received_time
            if elapsed > TIMEOUT_THRESHOLD and not self.alerted:
                print(f"[HEALTH] ¡Sin datos desde hace {round(elapsed,2)} s!")
                self.alerted = True
            elif elapsed <= TIMEOUT_THRESHOLD and self.alerted:
                print("[HEALTH] Datos restablecidos.")
                self.alerted = False

# ──── 3. Atajo global get_packet() para el dashboard ──────────────
_receiver_singleton: UDPReceiver | None = None
_singleton_lock = threading.Lock()

def _ensure_receiver():
    global _receiver_singleton
    with _singleton_lock:
        if _receiver_singleton is None:
            _receiver_singleton = UDPReceiver(UDP_IP, UDP_PORT, output_csv=None)
            _receiver_singleton.start()
    return _receiver_singleton

def get_packet(timeout: float = 0.05):
    """
    Función sencilla para consumir un paquete:
        seq:int, ndarray shape (16,3)
    """
    rx = _ensure_receiver()
    return rx.get_next(timeout)

# ──── 4. Modo CLI para probar rápidamente ─────────────────────────
if __name__ == "__main__":
    print("Esperando paquetes… Ctrl+C para salir")
    try:
        while True:
            seq, arr = get_packet(timeout=2.0)
            print(f"Seq {seq}  primera muestra {arr[0]}")
    except KeyboardInterrupt:
        print("\nBye!")

