import socket
import struct
import numpy as np

HOST = ""          # 0.0.0.0  → todas las interfaces
PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

PKT_SIZE = 4 + 16*6   # 100 bytes
fmt_head = "<HH"      # seq (uint16), cnt (uint16)
fmt_block = "<hhh"    # x,y,z (int16)

while True:
    data, addr = sock.recvfrom(PKT_SIZE)
    if len(data) != PKT_SIZE:
        print("Paquete incompleto")
        continue

    seq, cnt = struct.unpack_from(fmt_head, data, 0)
    samples = struct.iter_unpack(fmt_block, data[4:])
    arr = np.array(list(samples), dtype=np.int16)   # shape (16,3)

    print(f"Seq {seq:5d}  RMS_x={np.sqrt(np.mean(arr[:,0]**2)):.1f}")
