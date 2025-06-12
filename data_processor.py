import socket
import struct
import numpy as np

from calibration import calibration
from conversion import acc_to_velocity
from signal_processing import apply_hanning_window, compute_rms, compute_fft

FS = 800

HOST = ""          # 0.0.0.0  → todas las interfaces
PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

PKT_SIZE = 4 + 16 * 6  # 100 bytes
fmt_head = "<HH"      # seq (uint16), cnt (uint16)
fmt_block = "<hhh"    # x,y,z (int16)

while True:
    data, addr = sock.recvfrom(PKT_SIZE)
    if len(data) != PKT_SIZE:
        print("Paquete incompleto")
        continue

    seq, cnt = struct.unpack_from(fmt_head, data, 0)
    samples = struct.iter_unpack(fmt_block, data[4:])
    arr = np.array(list(samples), dtype=np.int16)

    vel = acc_to_velocity(arr.astype(float), FS)

    for sample in vel:
        if calibration.capturing:
            calibration.add_sample(sample)

    if calibration.is_complete():
        calibration.compute_offset()

    vel -= calibration.offset
    rms = compute_rms(vel)
    freqs, amps = compute_fft(apply_hanning_window(vel), FS)
    print(f"Seq {seq:5d}  RMS_x={rms[0]:.1f}")