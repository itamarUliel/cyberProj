import socket
import os
from consts import *
import Encryption_handler

# Before
server_socket = socket.socket()
server_socket.bind((SERVER_IP, TCP_SERVER_PORT))
server_socket.listen()
print(f"TCP server is up and running. pid={os.getpid()}")
(client_socket, client_address) = server_socket.accept()
print("Client connected")

# During



data = None
server_keys = Encryption_handler.get_keys()
while data != EXIT_CODE:
    data = client_socket.recv(PACKET_SIZE).decode()
    if data != EXIT_CODE and data.split("|")[0] == "start_enc":
        client_socket.send(f"ok|".encode())
        key = Encryption_handler.load_public(client_socket.recv(1024))
        client_socket.send(Encryption_handler.save_public(server_keys["pb"]))
        print(key)
        print(Encryption_handler.decrypt(client_socket.recv(1024), server_keys["pr"]))
        client_socket.sendall(Encryption_handler.encrypt("heyyy", key))

# After
client_socket.close()
server_socket.close()