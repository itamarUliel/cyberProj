import socket
import Encryption_handeler
import client_handler
import threading
import time

import colorama
from colorama import Back, Fore
colorama.init(autoreset=True)

client_keys = None
server_public_key = None
wconn_keys = None
wconn_ip = "127.0.0.1"
BYTE_SIZE = 4000

error_c = Fore.BLACK + Back.RED
ok_c = Back.GREEN + Fore.BLACK
pending_c = Back.LIGHTBLUE_EX + Fore.BLACK
data_c = Back.LIGHTYELLOW_EX + Fore.GREEN


def wconn(bind, pr):
    global BYTE_SIZE
    global server_public_key

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(bind)
    server.listen()
    conn, address = server.accept()
    d = conn.recv(BYTE_SIZE).decode()
    print(ok_c + d)
    while True:
        data = b''
        while data == b'':
            data = conn.recv(BYTE_SIZE)

        msg = Encryption_handeler.decrypt(data, pr)
        command, data = msg.split("|")[0], msg.split("|")[1:]

        if command == "msg":
            print(Back.MAGENTA + f"got msg from {data[0]}: {data[1]}")
        elif command == "close":
            conn.close()
            exit(error_c + "the server close the connection with the wconn")
        else:
            print(error_c + "the server send an illegal command to wconn, shutting down the client!")
            exit()


def encrypt(s):
    global BYTE_SIZE
    global client_keys
    global wconn_keys
    global server_public_key
    print(pending_c + "setting up encryption")
    s.sendall("start_enc|".encode())
    msg = s.recv(BYTE_SIZE).decode()
    status, msg = msg.split("|")[0], msg.split("|")[1:]
    if status != "ok":
        exit(error_c + msg)
    s.sendall(Encryption_handeler.save_public(client_keys["pb"]))
    server_public_key = Encryption_handeler.load_public(s.recv(BYTE_SIZE))

    s.sendall("wconn_enc|".encode())
    msg = s.recv(BYTE_SIZE).decode()
    status, msg = msg.split("|")[0], msg.split("|")[1:]
    if status != "ok":
        exit(error_c + msg)
    s.sendall(Encryption_handeler.save_public(wconn_keys["pb"]))
    msg = s.recv(BYTE_SIZE).decode()
    status, msg = msg.split("|")[0], msg.split("|")[1:]
    if status != "ok":
        exit(error_c + msg)
    print(ok_c + "encryption is now up!")


def get_free_port(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def start_comm(s):
    while True:                    # encrypt from now
        show = """\n
        'a' = ask server to authorize this user
        'm' = write a message
        'e' = close connection (exit)
        'c' = see who's connected and who you can talk to
        """
        print(show)
        act = input(pending_c + "\t\t\tact:")[0]
        if act in ['a', 'm', 'e', 'c']:
            if act == 'e':
                s.sendall(Encryption_handeler.encrypt("close|", server_public_key))
                s.close()
                exit(ok_c + "closing...")
            elif act == 'c':
                client_handler.connected(s, server_public_key, client_keys["pr"])
            else:
                if act == 'a':
                    send = client_handler.build_authorize(s, server_public_key, client_keys["pr"])
                elif act == 'm':
                    send = client_handler.build_sendto_msg(s, server_public_key, client_keys["pr"])
                s.sendall(Encryption_handeler.encrypt(send, server_public_key))
                data = Encryption_handeler.decrypt(s.recv(BYTE_SIZE), client_keys["pr"])
                status, msg = data.split("|")
                if status == "ok":
                    print(ok_c + msg)
                    continue
                else:
                    print(error_c + f"{status} {msg}, try again")


def start_server():
    global client_keys
    print(pending_c + "trying to connect")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = '127.0.0.1'
    port = 5678
    client_socket.connect((host_ip, port))  # a tuple
    client_keys = Encryption_handeler.get_keys(500)
    print(ok_c + "server now connected, with keys")
    print(data_c + f"server running on ({host_ip},{port})")
    return client_socket


def start_sending(s):
    global client_keys
    global server_public_key
    global wconn_keys
    global wconn_ip
    print(pending_c + "beginning to login")
    while True:
        data = client_handler.build_login()
        if data is None:
            s.sendall("close|".encode())
            s.close()
            exit()
        s.sendall(data.encode())
        data = s.recv(BYTE_SIZE).decode()
        status, msg = data.split("|")
        if status == "ok":
            print(ok_c + "logged in successfully")
            break
        else:
            print(error_c + f"{status}: {msg}")

    wconn_keys, wconn_port = Encryption_handeler.get_keys(500), get_free_port(wconn_ip)
    wconn_bind = (wconn_ip, wconn_port)
    print(data_c + f'wconn running on ({wconn_bind[0]},{wconn_bind[1]})')
    wconn_thread = threading.Thread(target=wconn, args=(wconn_bind, wconn_keys["pr"]))
    wconn_thread.start()

    s.sendall(f'wconn|{"|".join([wconn_bind[0], str(wconn_bind[1])])}'.encode())
    data = s.recv(BYTE_SIZE).decode()
    status, msg = data.split("|")
    if status == "ok":
        pass
    else:
        print(error_c + msg + ", resetting connection, fix it")
        exit()

    encrypt(s)

    start_comm(s)

def main():
    s = start_server()
    start_sending(s)

if __name__ == '__main__':
    main()
