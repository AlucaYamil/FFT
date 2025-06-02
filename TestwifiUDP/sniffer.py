import socket, struct

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("192.168.4.2", 9000))     # ← pon aquí la IP que Wireshark reporta
print("Escuchando… Ctrl-C para salir")

while True:
    data, _ = sock.recvfrom(2048)
    seq, cnt = struct.unpack_from("<HH", data, 0)
    print(f"seq={seq:05d}  count={cnt}  bytes={len(data)}")
