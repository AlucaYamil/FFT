"""
Recepci\u00f3n de paquetes UDP de 100 bytes enviados por el ESP32-ADXL345:
<seq:uint16><cnt:uint16><16*(x:int16,y:int16,z:int16)>
Devuelve (seq, ndarray shape 16 \u00d7 3).
"""
import socket, struct, numpy as np

HOST, PORT = "", 5005
PKT_SIZE   = 100
FMT_HEAD   = "<HH"
FMT_SAMP   = "<hhh"

_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
_sock.bind((HOST, PORT))

def get_packet(timeout=None):
    _sock.settimeout(timeout)
    data, _ = _sock.recvfrom(PKT_SIZE)
    if len(data) != PKT_SIZE:
        raise ValueError(
            f"Paquete UDP {len(data)} bytes \u2013 esperado {PKT_SIZE}. "
            "Formato: seq,cnt,16*(x,y,z int16)."
        )
    seq, cnt = struct.unpack_from(FMT_HEAD, data, 0)
    assert cnt == 16
    samples  = struct.iter_unpack(FMT_SAMP, data[4:])
    arr = np.fromiter(samples, dtype=np.int16).reshape(16, 3)
    return seq, arr
