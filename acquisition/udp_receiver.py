import socket
import struct
import numpy as np

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
