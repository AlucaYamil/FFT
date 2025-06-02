import socket
import struct
import numpy as np
from settings import HW
from processing.integration import accel_to_vel_rms
FS_HZ = HW.SAMPLE_RATE
PORT = 9000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))     # ← ¡IMPRESCINDIBLE!
sock.settimeout(1.0)
print(f"[listener_udp] escuchando en puerto {PORT}…")

def setup_udp(ip: str, port: int, timeout: float = 0.2):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip, port))
    sock.settimeout(timeout)
    return sock

def receive_batch(sock):
    """
    Recibe un paquete UDP:
      - 4 bytes Seq (uint32 LE)
      - N muestras de int16 LE en tramas [x,y,z]
    """
    try:
        data, addr = sock.recvfrom(4096)
        print(f"[receive_batch] {len(data)} bytes from {addr}")
        if len(data) < 4:
            print("[receive_batch] paquete muy corto")
            return None, None
        #Nuevo Bloque
        seq, n = struct.unpack_from("<HH", data, 0)
        expected_bytes = 4 + n * 6
        
        if len(data) != expected_bytes:
            print(f"[receive_batch] ⚠️ tamaño incoherente: "
          f"esperado {expected_bytes} bytes, llegó {len(data)}")
            return None, None
        raw = np.frombuffer(data, dtype="<i2", offset=4)
        raw = raw.reshape(n, 3)

        vel_rms = accel_to_vel_rms(raw, fs=FS_HZ)
        print(f"[receive_batch] seq={seq}  n={n}  rms={vel_rms:.3f} mm/s")
        # Fin De Bloque     
        
        seq = struct.unpack_from('<I', data, 0)[0]
        payload = data[4:]
        if len(payload) % 6 != 0:
            print(f"[receive_batch] payload len {len(payload)} no es múltiplo de 6")
            return seq, None
        count = len(payload) // 2
        vals = struct.unpack('<' + 'h'*count, payload)
        raw = np.array(vals, dtype=np.int16).reshape(-1, 3)
        print(f"[receive_batch] parsed raw.shape = {raw.shape}")
        return seq, raw
    except socket.timeout:
        return None, None
    except Exception as e:
        print(f"[receive_batch] excepción: {e}")
        return None, None
