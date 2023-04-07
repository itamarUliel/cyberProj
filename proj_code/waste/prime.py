import socket
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_address = ("127.0.0.1", 7777)
    server.connect(socket_address)
    server.close()
    server.sendall("hey".encode())
    a = "2" // 2




start_server()