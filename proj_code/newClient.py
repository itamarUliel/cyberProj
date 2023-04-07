import socket
import threading
import Encryption_handeler
import client_handler
from prompt_toolkit import prompt
import sys

import colorama
from colorama import Back, Fore
colorama.init(autoreset=True)

from client_utils import initialize
initialize()
from client_utils import *


error_c = Fore.BLACK + Back.RED
ok_c = Back.GREEN + Fore.BLACK
pending_c = Back.LIGHTBLUE_EX + Fore.BLACK
data_c = Back.LIGHTYELLOW_EX + Fore.GREEN


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
            print(ok_c + "logged in successfully (if you have backup its restored)")
            if not bm:
                backup_bind = list(s.recv(BYTE_SIZE).decode().split("|")[1:])
                backup_bind[1] = int(backup_bind[1])
                backup_bind = tuple(backup_bind)
                user_backup = built.split("|")[1:]
            break
        else:
            print(error_c + f"{status}: {msg}")


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
            try:
                data = conn.recv(BYTE_SIZE)
            except ConnectionResetError:
                print(error_c + "the main server is down. closing conn")
                handle_close(server, conn)
                exit()
        msg = Encryption_handeler.decrypt(data, pr)
        command, data = msg.split("|")[0], msg.split("|")[1:]

        if command == "msg":
            print(Back.MAGENTA + f"got msg from {data[0]}: {data[1]}")
        elif command == "close":
            handle_close(server, conn)
            exit(error_c + "the server close the connection with the wconn")
        else:
            print(error_c + "the server send an illegal command to wconn, shutting down the client!")
            handle_close(server, conn)
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
        handle_close(s)
        exit(error_c + msg)
    s.sendall(Encryption_handeler.save_public(client_keys["pb"]))
    server_public_key = Encryption_handeler.load_public(s.recv(BYTE_SIZE))

    s.sendall("wconn_enc|".encode())
    msg = s.recv(BYTE_SIZE).decode()
    status, msg = msg.split("|")[0], msg.split("|")[1:]
    if status != "ok":
        handle_close(s)
        exit(error_c + msg)
    s.sendall(Encryption_handeler.save_public(wconn_keys["pb"]))
    msg = s.recv(BYTE_SIZE).decode()
    status, msg = msg.split("|")[0], msg.split("|")[1:]
    if status != "ok":
        handle_close(s)
        exit(error_c + msg)
    print(ok_c + "encryption is now up!")


def start_wconn(s):
    global wconn_keys, wconn_ip
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
            act = input(pending_c + "\t\t\tact:")[0]
        except IndexError:
            print("try again...")
            continue
        except ValueError:
            sys.stdin = open(0, 'r')
            act = input(pending_c + "\t\t\tact:")[0]

        if act in ['a', 'm', 'e', 'c']:
            if act == 'e':
                s.sendall(Encryption_handeler.encrypt("close|", server_public_key))
                handle_close(s)
                exit(ok_c + "closing...")
            elif act == 'c':
                client_handler.connected(s, server_public_key, client_keys["pr"])
            else:
                if act == 'a':
                    send = client_handler.build_authorize(s, server_public_key, client_keys["pr"])
                    print(pending_c + "waiting for server response.")
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


def backup_client():
    try:
        global backup_bind
        s1 = start_server(backup_bind)
        start_sending(s1, True)
    except (ConnectionRefusedError, TypeError):
        print(error_c + "cant connect to backup")


def start_server():
    global server_address
    initialize()

    global client_keys
    print(pending_c + "trying to connect")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect(server_address)  # a tuple
    client_keys = Encryption_handeler.get_keys(500)
    print(ok_c + "server now connected, with keys")
    print(data_c + f"server running on {server_address}")
    return client_socket


def start_sending(s, bm=False):
    global client_keys
    global server_public_key
    global wconn_keys
    global wconn_ip
    global backup_bind
    global user_backup

    print(pending_c + "beginning to login")
    try:
        login(s, bm)
        start_wconn(s)
        encrypt(s)
        start_comm(s)

    except (ConnectionResetError, ConnectionAbortedError):
        handle_close(s)
        if not bm:
            print(error_c + "server went down, proceeding to back up if possible!")
            raise client_handler.NeedBackupException()
        else:
            print(error_c + "the backup client falled, goodbye losers")


def main():
    try:
        server = start_server()
        start_sending(server)
    except (client_handler.NeedBackupException, ConnectionRefusedError) as e:
        if "actively refused it" in str(e):
            print(error_c + "couldnt connected to prime, trying backup")

        backup_client()


if __name__ == '__main__':
    main()
