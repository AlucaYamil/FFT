import os
import socket
import struct
import time
import threading
import pandas as pd

# ──── 1. CONFIGURACIÓN ───────────────────────────────────────────────

# Puerto/IP en el que el ESP32 envía datos (debe coincidir con ESP32 HOST_PORT)
UDP_IP     = "0.0.0.0"  # Escucha en todas las interfaces
UDP_PORT   = 9000       # Cambiar si el ESP32 se configura en otro puerto

# Estructura de cada paquete:
BATCH_SIZE     = 16  # número de muestras que envía el ESP32 por paquete
HEADER_FMT     = "<HH"               # seq:uint16, count:uint16
SAMPLE_FMT     = "<" + "hhh" * BATCH_SIZE  # (x:int16, y:int16, z:int16) × 16
HEADER_SIZE    = struct.calcsize(HEADER_FMT)      # 4 bytes
SAMPLES_SIZE   = struct.calcsize("hhh") * BATCH_SIZE  # 6 bytes × 16 = 96 bytes
PACKET_SIZE    = HEADER_SIZE + SAMPLES_SIZE       # 100 bytes

# CSV de salida donde se van a agregar las muestras (modo append)
OUTPUT_CSV         = "simulated_data.csv"
# Umbral de timeout para detectar falta de paquetes (en segundos)
TIMEOUT_THRESHOLD  = 2.0   # si pasan >2s sin datos, se alerta
# Frecuencia con la que el health monitor verifica el timeout (en segundos)
HEALTH_CHECK_INTERVAL = 1.0

# ──── 2. CLASE UDPReceiver ────────────────────────────────────────────

class UDPReceiver:
    """
    Clase que:
    - Abre un socket UDP.
    - Recibe paquetes, valida tamaño y formato.
    - Desempaqueta las 16 muestras de aceleración (X, Y, Z).
    - Escribe cada muestra en un DataFrame/CSV.
    - Monitorea si dejan de llegar paquetes y alerta.
    """

    def __init__(self, ip: str, port: int, output_csv: str):
        self.ip            = ip
        self.port          = port
        self.output_csv    = output_csv
        self.sock          = None
        self.running       = False

        # Para detección de pérdida de paquetes:
        self.last_seq          = None
        self.last_received_time = None  # timestamp Unix (segundos) de la última recepción
        self.alerted           = False  # para no imprimir warnings repetidos

        # Inicializar CSV con encabezados si no existe
        if not os.path.exists(self.output_csv):
            df_init = pd.DataFrame(columns=["timestamp", "seq", "sample_idx", "x", "y", "z"])
            df_init.to_csv(self.output_csv, index=False)

    def start(self):
        """
        Inicia two hilos:
        1) receptor UDP (_run)
        2) health monitor (_health_monitor)
        """
        self.running = True

        # Hilo principal de recepción UDP
        thread_recv = threading.Thread(target=self._run, daemon=True)
        thread_recv.start()

        # Hilo de monitoreo de salud
        thread_health = threading.Thread(target=self._health_monitor, daemon=True)
        thread_health.start()

        print(f"[UDPReceiver] Hilos iniciados. Escuchando en {self.ip}:{self.port}")

    def stop(self):
        """
        Detiene la recepción y cierra el socket. 
        """
        self.running = False
        if self.sock:
            self.sock.close()
            print("[UDPReceiver] Socket cerrado.")

    def _run(self):
        """
        Bucle principal de recepción:
        - bind al socket UDP
        - recvfrom, validar tamaño, desempaquetar, escribir al CSV
        - actualizar self.last_received_time y self.last_seq
        """
        try:
            # Crear y bindear el socket UDP
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.ip, self.port))
            print(f"[UDPReceiver] Socket UDP bind en {self.ip}:{self.port}")

            while self.running:
                packet, addr = self.sock.recvfrom(1024)  # buffer 1024 bytes

                # Validar tamaño de paquete
                if len(packet) != PACKET_SIZE:
                    print(f"[WARNING] Tamaño incorrecto: {len(packet)} bytes. Esperados: {PACKET_SIZE}. Ignorando paquete.")
                    continue

                # Desempaquetar cabecera (seq, count)
                try:
                    header_bytes = packet[:HEADER_SIZE]
                    seq, count   = struct.unpack(HEADER_FMT, header_bytes)
                except struct.error as e:
                    print(f"[ERROR] No se pudo desempaquetar cabecera: {e}")
                    continue

                # Validar que count coincida con el BATCH_SIZE
                if count != BATCH_SIZE:
                    print(f"[WARNING] Campo 'count' incorrecto: {count}. Se esperaba: {BATCH_SIZE}.")
                    # No se aborta; se sigue procesando de todos modos

                # Detectar pérdida de paquetes (basado en secuencia)
                if self.last_seq is not None:
                    expected_seq = (self.last_seq + 1) & 0xFFFF  # rollover a 16 bits
                    if seq != expected_seq:
                        print(f"[WARNING] Posible paquete perdido: último seq={self.last_seq}, actual={seq}")
                self.last_seq = seq

                # Desempaquetar las 16 muestras: offset desde HEADER_SIZE
                samples_bytes = packet[HEADER_SIZE:]
                try:
                    raw_vals = struct.unpack(SAMPLE_FMT, samples_bytes)
                    # raw_vals → tupla de 48 int16: (x0, y0, z0, x1, y1, z1, …, x15, y15, z15)
                except struct.error as e:
                    print(f"[ERROR] No se pudo desempaquetar muestras: {e}")
                    continue

                # Actualizar marca de tiempo de última recepción
                self.last_received_time = time.time()
                # Resetear alerta si antes estaba en estado de timeout
                if self.alerted:
                    print("[UDPReceiver] Datos restablecidos: llegan paquetes de ESP32 nuevamente.")
                    self.alerted = False

                # Construir lista de diccionarios: cada fila = una muestra
                timestamp_base = int(self.last_received_time * 1000)  # ms
                filas = []
                for i in range(BATCH_SIZE):
                    idx_base = i * 3
                    x = raw_vals[idx_base + 0]
                    y = raw_vals[idx_base + 1]
                    z = raw_vals[idx_base + 2]
                    filas.append({
                        "timestamp":   timestamp_base,
                        "seq":         int(seq),
                        "sample_idx":  i,
                        "x":           int(x),
                        "y":           int(y),
                        "z":           int(z)
                    })

                # Convertir a DataFrame y hacer append al CSV
                df = pd.DataFrame(filas, columns=["timestamp", "seq", "sample_idx", "x", "y", "z"])
                try:
                    df.to_csv(self.output_csv, mode="a", header=False, index=False)
                except Exception as e:
                    print(f"[ERROR] No se pudo escribir en CSV: {e}")

        except Exception as e:
            print(f"[ERROR] Excepción en bucle UDPReceiver: {e}")
        finally:
            if self.sock:
                self.sock.close()

    def _health_monitor(self):
        """
        Hilo que, cada HEALTH_CHECK_INTERVAL segundos, verifica cuánto tiempo
        ha pasado desde self.last_received_time. Si supera TIMEOUT_THRESHOLD,
        emite un warning (solo una vez) e indica que no llegan datos.
        """
        while self.running:
            time.sleep(HEALTH_CHECK_INTERVAL)

            # Si aún no hemos recibido ningún paquete
            if self.last_received_time is None:
                # Solo alertar una sola vez
                if not self.alerted:
                    print(f"[HEALTH CHECK] Aún no han llegado datos del ESP32.")
                    self.alerted = True
                continue

            # Calcular tiempo transcurrido desde la última recepción
            elapsed = time.time() - self.last_received_time
            if elapsed > TIMEOUT_THRESHOLD:
                if not self.alerted:
                    secs = round(elapsed, 2)
                    print(f"[HEALTH CHECK] ¡No se reciben datos desde hace {secs} segundos!")
                    print("               → Verificar conexión Wi-Fi, firewall, o que el ESP32 esté encendido.")
                    self.alerted = True
            else:
                # Si ya habíamos alertado antes y ahora llegan datos, reseteamos la alerta
                if self.alerted:
                    print(f"[HEALTH CHECK] Datos recibidos nuevamente después de timeout ({round(elapsed,2)}s).")
                    self.alerted = False

# ──── 3. FUNCIÓN PRINCIPAL ───────────────────────────────────────────

def main():
    """
    Punto de entrada:
    - Instancia UDPReceiver y lo arranca.
    - Mantiene el hilo principal vivo hasta Ctrl+C.
    """
    receiver = UDPReceiver(UDP_IP, UDP_PORT, OUTPUT_CSV)
    try:
        receiver.start()
        # Mantener el hilo principal vivo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[MAIN] Interrupción por teclado. Deteniendo UDPReceiver...")
    finally:
        receiver.stop()
        print("[MAIN] Finalizado.")

# ──── 4. EJECUCIÓN DIRECTA ───────────────────────────────────────────

if __name__ == "__main__":
    main()
