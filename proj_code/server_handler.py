import Encryption_handler
from server_values import *
import bcrypt
import socket

from colors import *


def get_free_port(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def save_backup(data):
    backup = ""
    for s in data.keys():
        user = data[s]["user"]
        authorize_u = data[s]["authorize"]
        if user is not None and authorize_u != []:
            backup += ":".join([user, ",".join(authorize_u)]) + "|"
    if backup == "":
        backup = "nothing to share."
    return backup


def load_backup(data): # data = b"us1:a1,a2,a3|us2..."
    backup = {}
    for user in data.split("|"):
        if user == "":
            continue
        us, authorize_list = user.split(":")[0], user.split(":")[1].split(",")
        backup[us] = authorize_list
    return backup


def login(s, data, bm):    # data = [conn ,user, password]  # backup {us: [authrize]
    global known_users         # {user: password,...}
    global connected_users     # {user: conn,...}
    global conn_data
    try:
        if bcrypt.checkpw(data[1].encode(),  known_users[data[0]].encode()):   # 0: us 1: pass
            if data[0] not in connected_users.keys():
                conn_data[s]["user"] = data[0]
                print(OK_COLOR + f"{data[0]} is now logged in!")
                if bm[0]:
                    backup = bm[1]
                    if data[0] in backup.keys():
                        conn_data[s]["authorize"] = backup[data[0]]
                        print(DATA_COLOR + f"{data[0]} has aa backup, backup load: {backup[data[0]]}")
                    else:
                        print(DATA_COLOR + f"{data[0]} didn't have backup to load")
                connected_users[data[0]] = s
                return ["ok", "None"]
            else:
                return ["error", "user already connected, try again"]
        else:
            return ["error", "password_incorrect, try again"]
    except KeyError:
        return ["error", "user not exists, try again"]


def sendto_msg(conn, send_to, msg):
    global connected_users        # {user: conn,...}
    global conn_data

    if send_to in connected_users.keys():
        print(DATA_COLOR + f"{conn_data[conn]['user']} wants to send {send_to} this: {msg}")
        if send_to in conn_data[conn]["authorize"]:
            try:
                send_msg = "msg|%s|%s" % (conn_data[conn]["user"], msg)  # msg|sender|{msg}
                wconn = conn_data[connected_users[send_to]]["wconn"]
                send_msg = Encryption_handler.encrypt(send_msg, conn_data[connected_users[send_to]]["wconn_key"])
                wconn.sendall(send_msg)
            except:
                print(ERROR_COLOR + "error happened while sending, msg didn't send!")
                return ["error", "problem accrue while sending the msg"]
            else:
                print(OK_COLOR + "msg send!")
                return ["ok", "msg send"]
        else:
            print(ERROR_COLOR + "user unauthorized to send!")
            return ["error", "the sender is not authorize to send to_send"]
    else:
        return ["error", "to_send is not currently connected (or exist)"]


def authorize(s, to_authorize):
    global conn_data
    global connected_users
    if to_authorize not in connected_users.keys():
        return ["error", "the user is not currently connected"]
    if to_authorize not in conn_data[s]["authorize"]:
        while True:
            ask = input(PENDING_COLOR + "does %s can connect to %s\n'd' = denied\t'o' = ok" % (conn_data[s]["user"], to_authorize))
            if ask in ['d', 'o']:
                break
            else:
                print(ERROR_COLOR + "try again ('d'/'o'")
        if ask == 'd':
            return ["error", "the server denied"]
        elif ask == 'o':
            conn_data[s]["authorize"].append(to_authorize)
            return ["ok", f"the server accepted your conn to {to_authorize}"]
    else:
        return ["error", "user already authorize to send"]


def connected(conn):
    global conn_data
    global connected_users

    data = [f'{",".join(connected_users.keys())}', f'{",".join(conn_data[conn]["authorize"])}']
    return data



