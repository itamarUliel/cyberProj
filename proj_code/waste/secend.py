import socket
def start_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_address = ("127.0.0.1", 7777)
    server.bind(socket_address)
    server.listen()
    print("START_SERVER: LISTENING AT:", socket_address)
    secend, adreess = server.accept()

    data = True
    while data:
        data = secend.recv(1024).decode()
        print(data)

    print("ima shef")


start_server()
