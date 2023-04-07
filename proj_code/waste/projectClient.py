import socket
import Encryption_handeler
import client_handler

client_keys = None
server_public_key = None

BYTE_SIZE = 4000

def start_server():
    global client_keys
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = '127.0.0.1'
    port = 5678
    client_socket.connect((host_ip, port))  # a tuple
    client_keys = Encryption_handeler.get_keys(1500)
    return client_socket


def start_sending(s):
    global client_keys
    global server_public_key

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
            print("connected successfully")
            break
        else:
            print(f"{status}: {msg}")

    data = "start_encrypt|"   # ready to send bytes
    s.sendall(data.encode())
    data = s.recv(BYTE_SIZE)
    s.sendall(Encryption_handeler.save_public(client_keys["pb"]))
    bpb = s.recv(BYTE_SIZE)
    server_public_key = Encryption_handeler.load_public(bpb)

    while True:                    # encrypt from now
        show = """
        'a' = ask server to authorize this user
        'm' = write a message
        'e' = close connection (exit)
        'c' = see who's connected and who you can talk to
        """
        print(show)
        act = input("act:")[0]
        if act in ['a', 'm', 'e', 'c']:
            if act == 'e':
                s.sendall(Encryption_handeler.encrypt("close|", server_public_key))
            elif act == 'c':
                print(client_handler.connected(s, server_public_key, client_keys["pr"]))
            else:
                if act == 'a':
                    send = client_handler.build_authorize(s, server_public_key, client_keys["pr"])
                elif act == 'm':
                    send = client_handler.build_sendto_msg(s, server_public_key, client_keys["pr"])
                s.sendall(send.encode())
                data = Encryption_handeler.decrypt(s.recv(BYTE_SIZE), client_keys["pr"])
                status, msg = data.split("|")
                if status == "ok":
                    print(msg)
                    break
                else:
                    print(f"{status} {msg}, try again")



def main():
    try:
        s = start_server()
        start_sending(s)
    except ConnectionResetError:
        print("the server crashed unexpectedly, please check and try again")
        exit()


if __name__ == '__main__':
    main()