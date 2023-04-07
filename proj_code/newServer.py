import select

from colors import *
from server_values import initialize
initialize()
from server_handler import *
from chat_server import PrimaryServer, BackupServer
import Encryption_handler
server_keys = None
ks, rs, BIND, backup_address = server_constants()
inputs = []
backup_public = None
update_chk = False


def handle_close(s):
    global conn_data
    global connected_users
    global update_chk
    try:
        conn_data[s]["wconn"].sendall(Encryption_handler.encrypt("close|", conn_data[s]["wconn_key"]))
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

    print(OK_COLOR + "\n\nHANDLE_CLOSE: done closing!")
    print(DATA_COLOR + f"""HANDLE_CLOSE: dicts status:
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
        return Encryption_handler.encrypt("|".join(msg), conn_data[s]["pb"])


def pending(s, msg, bm):
    global rs
    global conn_data
    global inputs
    global backup_address

    command, data = msg.split("|")[0], msg.split("|")[1:]
    if command == "login":                                       # send: login|us|ps  # recv: ok/error|response
        response = login(s, data, bm)
        print(DATA_COLOR + "LOGGIN: the login try went: ", response)
        s.sendall(send_msgs(response))
        if response[0] == "ok" and not bm[0]:
            s.sendall(f"backup|{'|'.join([backup_address[0], str(backup_address[1])])}".encode())
    elif command == "wconn" and conn_data[s]["user"] is not None:         # send: wconn|ip|port recv:ok/error|response
        ip, port = data
        res = connect_write(s, ip, port)
        if res[0] == "ok":
            s.sendall(send_msgs(res))
            print(DATA_COLOR + f"{conn_data[s]['user']} is now ready to encrypt!")
            conn_data[s]["status"] = "encrypt"

        else:
            s.sendall(send_msgs(res))

    elif command == "close":                                        # send: close|
        print(ERROR_COLOR + f"{s.getpeername()} ask to close, closing...")
        s.sendall("ok|")
        inputs.remove(s)
        handle_close(s)
    else:
        s.sendall(send_msgs(["error", "illegible command, closing connection"]))
        print(ERROR_COLOR + f"{s.getpeername()} is unknown and broke protocol, closing...")
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
            conn_data[s]["pb"] = Encryption_handler.load_public(key)
            s.sendall(Encryption_handler.save_public(server.get_server_keys()["pb"]))
        elif command == "wconn_enc":           # s: wconn_enc| r_client: ok| s: wconn_key r_client: ok
            error_msg = "error while replacing write conn keys"
            s.sendall(send_msgs(["ok"]))
            wconn_key = s.recv(rs)
            conn_data[s]["wconn_key"] = Encryption_handler.load_public(wconn_key)
            s.sendall(send_msgs(["ok"]))
            conn_data[s]["status"] = "comm"
            print(OK_COLOR + f"{conn_data[s]['user']} succeeded to enc, he is active!")
    except:
        print(ERROR_COLOR + f"{conn_data[s]['user']} failed to enc, reason:")
        print(ERROR_COLOR + error_msg)
        s.sendall(send_msgs(["error", error_msg]))

    if command == "close":
        print(ERROR_COLOR + f"{conn_data[s]['user']} ask to close, closing...")
        inputs.remove(s)
        handle_close(s)

    elif command != "start_enc" and command != "wconn_enc":
        print(ERROR_COLOR + f"{s.getpeername()} is unknown and broke protocol, closing...")
        s.sendall(send_msgs(["error", "illegible command, closing connection"]))
        inputs.remove(s)
        handle_close(s)


def comm(s, msg):
    global conn_data
    global server_keys
    global update_chk

    msg = Encryption_handler.decrypt(msg, server_keys["pr"])
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
        print(ERROR_COLOR + f"{conn_data[s]['user']} ask to close, closing...")
        inputs.remove(s)
        handle_close(s)

    else:
        print(ERROR_COLOR + f"{s.getpeername()} is unknown and broke protocol, closing...")
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
    server_keys = Encryption_handler.get_keys(ks)
    print(DATA_COLOR + "START_SERVER: LISTENING AT:", socket_address)
    print(OK_COLOR + "START_SERVER: server got keys!", end="\n\n")

    if backup:
        backup_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backup_server.connect(backup_address)
        # backup_server.sendall(Encryption_handler.save_public(server_keys["pb"]))
        backup_public = Encryption_handler.load_public(backup_server.recv(1024))
        print(OK_COLOR + "backup is conncted!")
        return server, backup_server

    return server


def start_listening(server, backup_server=None, bm=[False]):    # bm = [T/F, back]
    global conn_data
    global connected_users
    global rs
    global inputs
    global update_chk

    inputs = [server]
    print(PENDING_COLOR + "LISTEN: listening started")
    while inputs:
        readable, writable, exceptional = select.select(inputs, [], [])
        for s in readable:
            if s is server:
                # New connection
                connection, client_address = s.accept()
                print(DATA_COLOR + f'LISTEN: new connection from {client_address}', end="\n\n")
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
                    print(ERROR_COLOR + f'\n\nclosing {s.getpeername()}, he died')
                    # Stop listening for input on the connection
                    inputs.remove(s)
                    handle_close(s)

        if not bm[0]:
            if update_chk:
                backup_server.sendall(Encryption_handler.encrypt(save_backup(conn_data), backup_public))
            update_chk = False


def backup_mode():
    global server
    server = BackupServer()
    global server_keys
    server_keys = server.get_server_keys()
    start_listening(server.get_server_socket(), bm=[True, server.get_backup_data()])



def prime_mode():
    global server
    server = PrimaryServer()
    global server_keys, backup_public
    backup_public = server.get_backup_public_key()
    server_keys = server.get_server_keys()
    start_listening(server.get_server_socket(), server.get_backup_socket())



def main():
    print("""
                   .d888                       888               888    
                  d88P"                        888               888    
                  888                          888               888    
.d8888b   8888b.  888888 .d88b.        .d8888b 88888b.   8888b.  888888 
88K          "88b 888   d8P  Y8b      d88P"    888 "88b     "88b 888    
"Y8888b. .d888888 888   88888888      888      888  888 .d888888 888    
     X88 888  888 888   Y8b.          Y88b.    888  888 888  888 Y88b.  
 88888P' "Y888888 888    "Y8888        p"Y8888P 888  888 "Y888888  "Y888
                                    the project of ITAMAR ULIEL
    """)
    server_type = ""
    while server_type not in ['p', 'b']:
        server_type = input("'p' for primary or 'b' for backup: ")

    if server_type == 'p':
        print(DATA_COLOR + "server running in PRIMARY MODE")
        prime_mode()
    else:
        print(DATA_COLOR + "server running in BACKUP MODE")
        backup_mode()


if __name__ == '__main__':
    main()