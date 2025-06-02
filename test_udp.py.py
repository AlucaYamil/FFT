# test_udp.py
import socket

PORT = 9000
BUFFER = 1024

# Cambia “” por la IP concreta de tu PC si "" (0.0.0.0) no funciona:
BIND_IP = ""  

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((BIND_IP, PORT))
print(f"Escuchando UDP en {(BIND_IP or '0.0.0.0')}:{PORT}")

while True:
    data, addr = sock.recvfrom(BUFFER)
    print(f"Recibido {len(data)} bytes de {addr}")
