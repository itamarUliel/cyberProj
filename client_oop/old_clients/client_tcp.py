import socket
import os
from consts import *

# Before
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect((SERVER_IP, TCP_SERVER_PORT))
print(f"TCP client is up and running. pid={os.getpid()}")

import Encryption_handler
# During
msg = None


def start_encrypt(s: socket.socket, keys):
    s.sendall("start_enc|".encode())
    status, msg = s.recv(1024).decode().split("|")
    if status != "ok":
        raise Exception
    s.sendall(Encryption_handler.save_public(keys["pb"]))
    server_public_key = Encryption_handler.load_public(s.recv(1024))
    print(server_public_key)
    return server_public_key


while msg != EXIT_CODE:
    keys = Encryption_handler.get_keys()
    s_key = start_encrypt(my_socket, keys)
    my_socket.sendall(Encryption_handler.encrypt("hrhrhrh", s_key))

# After
my_socket.close()
