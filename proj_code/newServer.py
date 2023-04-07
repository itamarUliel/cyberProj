import select

from server_values import *
initialize()
from server_handeler import *

import colorama
from colorama import Back, Fore
colorama.init(autoreset=True)

server_keys = None
ks, rs, BIND = server_constants()
inputs = []
backup_public = None
update_chk = False
backup_address = ("127.0.0.1", 7890)

error_c = Fore.BLACK + Back.RED
ok_c = Back.GREEN + Fore.BLACK
pending_c = Back.LIGHTBLUE_EX + Fore.BLACK
data_c = Back.LIGHTYELLOW_EX + Fore.GREEN


def handle_close(s):
    global conn_data
    global connected_users
    global update_chk
    try:
        conn_data[s]["wconn"].sendall(Encryption_handeler.encrypt("close|", conn_data[s]["wconn_key"]))
        conn_data[s]["wconn"].close()
    except (AttributeError, ConnectionResetError):
        pass

    try:
        connected_users.pop(conn_data[s]["user"])
    except KeyError:
        pass
    for user in conn_data.keys():
        try:
            conn_data[user]["authorize"].remove(conn_data[s]["user"])
            update_chk = True
        except ValueError:
            continue
    conn_data.pop(s)
    s.close()

    print(ok_c + "\n\nHANDLE_CLOSE: done closing!")
    print(data_c + f"""HANDLE_CLOSE: dicts status:
       conn_data:     {conn_data}
       connected users: {connected_users}     
    """, end="\n\n")


def connect_write(s, ip, port):
    try:
        global conn_data
        wconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        wconn.connect((ip, int(port)))
        conn_data[s]["wconn"] = wconn
        wconn.sendall("the server connected 2 U, you can start recv msg!".encode())
        return ["ok", ""]
    except:
        print("unable to connect sendable conn")
        return ["error", "unable 2 connete, please check and send again"]


def send_msgs(msg, s=None):
    global conn_data
    if s is None:
        return "|".join(msg).encode()
    else:
        return Encryption_handeler.encrypt("|".join(msg), conn_data[s]["pb"])


def pending(s, msg, bm):
    global rs
    global conn_data
    global inputs
    global backup_address

    command, data = msg.split("|")[0], msg.split("|")[1:]
    if command == "login":                                       # send: login|us|ps  # recv: ok/error|response
        response = login(s, data, bm)
        print(data_c + "LOGGIN: the login try went: ", response)
        s.sendall(send_msgs(response))
        if response[0] == "ok" and not bm[0]:
            s.sendall(f"backup|{'|'.join([backup_address[0], str(backup_address[1])])}".encode())
    elif command == "wconn" and conn_data[s]["user"] is not None:         # send: wconn|ip|port recv:ok/error|response
        ip, port = data
        res = connect_write(s, ip, port)
        if res[0] == "ok":
            s.sendall(send_msgs(res))
            print(data_c + f"{conn_data[s]['user']} is now ready to encrypt!")
            conn_data[s]["status"] = "encrypt"

        else:
            s.sendall(send_msgs(res))

    elif command == "close":                                        # send: close|
        print(error_c + f"{s.getpeername()} ask to close, closing...")
        s.sendall("ok|")
        inputs.remove(s)
        handle_close(s)
    else:
        s.sendall(send_msgs(["error", "illegible command, closing connection"]))
        print(error_c + f"{s.getpeername()} is unknown and broke protocol, closing...")
        inputs.remove(s)
        handle_close(s)


def encrypt(s, msg):
    global rs
    global conn_data
    global server_keys
    global inputs

    command, data = msg.split("|")[0], msg.split("|")[1:]
    error_msg = ""
    try:
        if command == "start_enc":                               # s: start_enc| r: ok| s: client_key r: server_key
            error_msg = "error while replacing main conn keys"
            s.sendall(send_msgs(["ok"]))
            key = s.recv(rs)
            conn_data[s]["pb"] = Encryption_handeler.load_public(key)
            s.sendall(Encryption_handeler.save_public(server_keys["pb"]))
        elif command == "wconn_enc":           # s: wconn_enc| r_client: ok| s: wconn_key r_client: ok
            error_msg = "error while replacing write conn keys"
            s.sendall(send_msgs(["ok"]))
            wconn_key = s.recv(rs)
            conn_data[s]["wconn_key"] = Encryption_handeler.load_public(wconn_key)
            s.sendall(send_msgs(["ok"]))
            conn_data[s]["status"] = "comm"
            print(ok_c + f"{conn_data[s]['user']} succeeded to enc, he is active!")
    except:
        print(error_c + f"{conn_data[s]['user']} failed to enc, reason:")
        print(error_c + error_msg)
        s.sendall(send_msgs(["error", error_msg]))

    if command == "close":
        print(error_c + f"{conn_data[s]['user']} ask to close, closing...")
        inputs.remove(s)
        handle_close(s)

    elif command != "start_enc" and command != "wconn_enc":
        print(error_c + f"{s.getpeername()} is unknown and broke protocol, closing...")
        s.sendall(send_msgs(["error", "illegible command, closing connection"]))
        inputs.remove(s)
        handle_close(s)


def comm(s, msg):
    global conn_data
    global server_keys
    global update_chk

    msg = Encryption_handeler.decrypt(msg, server_keys["pr"])
    command, data = msg.split("|")[0], msg.split("|")[1:]

    if command == "authorize":                          # authorize|us
        res = authorize(s, data[0])
        s.sendall(send_msgs(res, s))
        update_chk = True

    elif command == "connected":                                      # connected|
        data = connected(s)            # "[connected],[authorize]"
        s.sendall(send_msgs(data, s))  # ["user1,user2,user3","user1,user3"]

    elif command == "sendto_msg":                               # sendto_msg|userToSend|msg
        res = sendto_msg(s, data[0], data[1])
        s.sendall(send_msgs(res, s))

    elif command == "close":                          # close|
        print(error_c + f"{conn_data[s]['user']} ask to close, closing...")
        inputs.remove(s)
        handle_close(s)

    else:
        print(error_c + f"{s.getpeername()} is unknown and broke protocol, closing...")
        s.sendall(send_msgs(["error", "illegible command, closing connection"]))
        inputs.remove(s)
        handle_close(s)


def start_server(bind, backup=True):
    global server_keys
    global backup_public
    global backup_address

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_address = bind
    server.bind(socket_address)
    server.listen()
    server_keys = Encryption_handeler.get_keys(ks)
    print(data_c + "START_SERVER: LISTENING AT:", socket_address)
    print(ok_c + "START_SERVER: server got keys!", end="\n\n")

    if backup:
        backup_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backup_server.connect(backup_address)
        # backup_server.sendall(Encryption_handeler.save_public(server_keys["pb"]))
        backup_public = Encryption_handeler.load_public(backup_server.recv(1024))
        print(ok_c + "backup is conncted!")
        return server, backup_server

    return server


def start_listening(server, backup_server=None, bm=[False]):    # bm = [T/F, back]
    global conn_data
    global connected_users
    global rs
    global inputs
    global update_chk

    inputs = [server]
    print(pending_c + "LISTEN: listening started")
    while inputs:
        readable, writable, exceptional = select.select(inputs, [], [])
        for s in readable:
            if s is server:
                # New connection
                connection, client_address = s.accept()
                print(data_c + f'LISTEN: new connection from {client_address}', end="\n\n")
                inputs.append(connection)
                conn_data[connection] = {"status": "pending", "user": None, "authorize": [], "pb": None, "wconn": None,
                                         "wconn_key": None}

            else:  # s.getpeername()
                try:
                    data = s.recv(rs)
                    if data:
                        if conn_data[s]["status"] == "pending":
                            pending(s, data.decode(), bm)
                        elif conn_data[s]["status"] == "encrypt":
                            encrypt(s, data.decode())
                        elif conn_data[s]["status"] == "comm":
                            comm(s, data)
                    else:
                        raise ConnectionResetError
                except ConnectionResetError:
                    # Interpret empty result as closed connection
                    print(error_c + f'\n\nclosing {s.getpeername()}, he died')
                    # Stop listening for input on the connection
                    inputs.remove(s)
                    handle_close(s)

        if not bm[0]:
            if update_chk:
                backup_server.sendall(Encryption_handeler.encrypt(save_backup(conn_data), backup_public))
            update_chk = False


def backup_mode():
    global backup_address
    backup = {}
    try:
        backup_key = Encryption_handeler.get_keys()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(backup_address)
        server.listen()
        print("START_SERVER: LISTENING AT:", backup_address)
        prime, adreess = server.accept()

        # prime_key = Encryption_handeler.load_public(prime.recv(1024))
        prime.sendall(Encryption_handeler.save_public(backup_key["pb"]))

        data = True
        while data:
            data = Encryption_handeler.decrypt(prime.recv(1024), backup_key["pr"])
            print(data)
            if data == "nothing to share.":
                continue
            backup = load_backup(data)

    except ConnectionResetError:
        prime.close()
        server.close()
        print(error_c + "prime server is down!")
        print(data_c + "active backup!")
        initialize()
        server = start_server(backup_address, backup=False)
        start_listening(server, bm=[True, backup])


def prime_mode():
    global BIND

    server, backup_server = start_server(BIND)
    start_listening(server, backup_server)


def main():
    print("""
                   .d888                       888               888    
                  d88P"                        888               888    
                  888                          888               888    
.d8888b   8888b.  888888 .d88b.        .d8888b 88888b.   8888b.  888888 
88K          "88b 888   d8P  Y8b      d88P"    888 "88b     "88b 888    
"Y8888b. .d888888 888   88888888      888      888  888 .d888888 888    
     X88 888  888 888   Y8b.          Y88b.    888  888 888  888 Y88b.  
 88888P' "Y888888 888    "Y8888        "Y8888P 888  888 "Y888888  "Y888
                                    the project of ITAMAR ULIEL
    """)
    server_type = ""
    while server_type not in ['p', 'b']:
        server_type = input("'p' or 'b'?")

    if server_type == 'p':
        print(data_c + "server running in PRIMARY MODE")
        prime_mode()
    else:
        print(data_c + "server running in BACKUP MODE")
        backup_mode()


if __name__ == '__main__':
    main()