import socket
import threading
import Encryption_handler
from client_oop.waste import client_handler
import sys

from colors import *

from client_oop.waste.client_utils import initialize
initialize()
from client_oop.waste.client_utils import *


def handle_close(*socks):
    for sock in socks:
        sock.close()


def login(s, bm):
    global backup_bind, user_backup

    while True:
        built = client_handler.build_login(bm, user_backup)
        if built is None:
            s.sendall("close|".encode())
            handle_close(s)
            exit()
        s.sendall(built.encode())
        data = s.recv(BYTE_SIZE).decode()
        status, msg = data.split("|")
        if status == "ok":
            print(OK_COLOR + "logged in successfully (if you have backup its restored)")
            if not bm:
                backup_bind = list(s.recv(BYTE_SIZE).decode().split("|")[1:])
                backup_bind[1] = int(backup_bind[1])
                backup_bind = tuple(backup_bind)
                user_backup = built.split("|")[1:]
            break
        else:
            print(ERROR_COLOR + f"{status}: {msg}")


def wconn(bind, pr):
    global BYTE_SIZE
    global server_public_key

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(bind)
    server.listen()
    conn, address = server.accept()
    d = conn.recv(BYTE_SIZE).decode()
    print(OK_COLOR + d)
    while True:
        data = b''
        while data == b'':
            try:
                data = conn.recv(BYTE_SIZE)
            except ConnectionResetError:
                print(ERROR_COLOR + "the main server is down. closing conn")
                handle_close(server, conn)
                exit()
        msg = Encryption_handler.decrypt(data, pr)
        command, data = msg.split("|")[0], msg.split("|")[1:]

        if command == "msg":
            print(Back.MAGENTA + f"got msg from {data[0]}: {data[1]}")
        elif command == "close":
            handle_close(server, conn)
            exit(ERROR_COLOR + "the server close the connection with the wconn")
        else:
            print(ERROR_COLOR + "the server send an illegal command to wconn, shutting down the client!")
            handle_close(server, conn)
            exit()


def encrypt(s):
    global BYTE_SIZE
    global client_keys
    global wconn_keys
    global server_public_key
    print(PENDING_COLOR + "setting up encryption")
    s.sendall("start_enc|".encode())
    msg = s.recv(BYTE_SIZE).decode()
    status, msg = msg.split("|")[0], msg.split("|")[1:]
    if status != "ok":
        handle_close(s)
        exit(ERROR_COLOR + msg)
    s.sendall(Encryption_handler.save_public(client_keys["pb"]))
    server_public_key = Encryption_handler.load_public(s.recv(BYTE_SIZE))

    s.sendall("wconn_enc|".encode())
    msg = s.recv(BYTE_SIZE).decode()
    status, msg = msg.split("|")[0], msg.split("|")[1:]
    if status != "ok":
        handle_close(s)
        exit(ERROR_COLOR + msg)
    s.sendall(Encryption_handler.save_public(wconn_keys["pb"]))
    msg = s.recv(BYTE_SIZE).decode()
    status, msg = msg.split("|")[0], msg.split("|")[1:]
    if status != "ok":
        handle_close(s)
        exit(ERROR_COLOR + msg)
    print(OK_COLOR + "encryption is now up!")


def start_wconn(s):
    global wconn_keys, wconn_ip
    wconn_keys, wconn_port = Encryption_handler.get_keys(500), get_free_port(wconn_ip)
    wconn_bind = (wconn_ip, wconn_port)
    print(DATA_COLOR + f'wconn running on ({wconn_bind[0]},{wconn_bind[1]})')

    wconn_thread = threading.Thread(target=wconn, args=(wconn_bind, wconn_keys["pr"]))
    wconn_thread.start()

    s.sendall(f'wconn|{"|".join([wconn_bind[0], str(wconn_bind[1])])}'.encode())
    data = s.recv(BYTE_SIZE).decode()
    status, msg = data.split("|")
    if status == "ok":
        pass
    else:
        print(ERROR_COLOR + msg + ", resetting connection, fix it")
        s.close()
        exit()


def get_free_port(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def start_comm(s):
    while True:  # encrypt from now
        show = """\n
                        'a' = ask server to authorize this user
                        'm' = write a message
                        'e' = close connection (exit)
                        'c' = see who's connected and who you can talk to
                        """
        print(show)
        try:
            act = input(PENDING_COLOR + "\t\t\tact:")[0]
        except IndexError:
            print("try again...")
            continue
        except ValueError:
            sys.stdin = open(0, 'r')
            act = input(PENDING_COLOR + "\t\t\tact:")[0]

        if act in ['a', 'm', 'e', 'c']:
            if act == 'e':
                s.sendall(Encryption_handler.encrypt("close|", server_public_key))
                handle_close(s)
                exit(OK_COLOR + "closing...")
            elif act == 'c':
                client_handler.connected(s, server_public_key, client_keys["pr"])
            else:
                if act == 'a':
                    send = client_handler.build_authorize(s, server_public_key, client_keys["pr"])
                    print(PENDING_COLOR + "waiting for server response.")
                elif act == 'm':
                    send = client_handler.build_sendto_msg(s, server_public_key, client_keys["pr"])
                s.sendall(Encryption_handler.encrypt(send, server_public_key))
                data = Encryption_handler.decrypt(s.recv(BYTE_SIZE), client_keys["pr"])
                status, msg = data.split("|")
                if status == "ok":
                    print(OK_COLOR + msg)
                    continue
                else:
                    print(ERROR_COLOR + f"{status} {msg}, try again")


def backup_client():
    try:
        global backup_bind
        s1 = start_server(backup_bind)
        start_sending(s1, True)
    except (ConnectionRefusedError, TypeError):
        print(ERROR_COLOR + "cant connect to backup")


def start_server(bind):
    initialize()

    global client_keys
    print(PENDING_COLOR + "trying to connect")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect(bind)  # a tuple
    client_keys = Encryption_handler.get_keys(500)
    print(OK_COLOR + "server now connected, with keys")
    print(DATA_COLOR + f"server running on {bind}")
    return client_socket


def start_sending(s, bm=False):
    global client_keys
    global server_public_key
    global wconn_keys
    global wconn_ip
    global backup_bind
    global user_backup

    print(PENDING_COLOR + "beginning to login")
    try:
        login(s, bm)
        start_wconn(s)
        encrypt(s)
        start_comm(s)

    except (ConnectionResetError, ConnectionAbortedError):
        handle_close(s)
        if not bm:
            print(ERROR_COLOR + "server went down, proceeding to back up if possible!")
            raise client_handler.NeedBackupException()
        else:
            print(ERROR_COLOR + "the backup client falled, goodbye losers")


def main():
    global server_address
    try:
        server = start_server(server_address)
        start_sending(server)
    except (client_handler.NeedBackupException, ConnectionRefusedError) as e:
        if "actively refused it" in str(e):
            print(ERROR_COLOR + "couldnt connected to prime, trying backup")

        backup_client()


if __name__ == '__main__':
    main()
