import Encryption_handler
import bcrypt
import socket
from Connction_data import ConnectionData

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
        current_conn_data:ConnectionData = data[s]
        user = current_conn_data.get_user()
        authorize_u = current_conn_data.get_authorize()
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


def login(current_socket, data, self):    # data = [conn ,user, password]  # backup {us: [authrize]
    try:
        current_conn_data: ConnectionData = self.get_conn_data()[current_socket]
        if bcrypt.checkpw(data[1].encode(),  self.get_known_users()[data[0]].encode()):   # 0: us 1: pwd
            if data[0] not in self.get_connected_users().keys():
                current_conn_data.set_user(data[0])
                print(OK_COLOR + f"{data[0]} is now logged in!")
                if not self.get_is_primary():
                    backup = self.get_backup_data()
                    if data[0] in backup.keys():
                        current_conn_data.set_authorize(backup[data[0]])
                        print(DATA_COLOR + f"{data[0]} has aa backup, backup load: {backup[data[0]]}")
                    else:
                        print(DATA_COLOR + f"{data[0]} didn't have backup to load")
                self.update_connected_users(data[0], current_socket)
                return ["ok", "None"]
            else:
                return ["error", "user already connected, try again"]
        else:
            return ["error", "password_incorrect, try again"]
    except KeyError:
        return ["error", "user not exists, try again"]


def sendto_msg(conn, send_to, msg, self):
    current_conn_data: ConnectionData = self.get_conn_data()[conn]

    if send_to in self.get_connected_users().keys():
        print(DATA_COLOR + f"{current_conn_data.get_user()} wants to send {send_to} this: {msg}")
        if send_to in current_conn_data.get_authorize():
            try:
                send_msg = "msg|%s|%s" % (current_conn_data.get_user(), msg)  # msg|sender|{msg}
                sent_to_conn_data: ConnectionData = self.get_conn_data()[self.get_connected_users()[send_to]]
                wconn = sent_to_conn_data.get_write_socket()
                send_msg = Encryption_handler.encrypt(send_msg, sent_to_conn_data.get_public_key())
                wconn.sendall(send_msg)
            except Exception as e:
                print(e)
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


def authorize(current_socket, to_authorize, self):
    current_conn_data: ConnectionData = self.get_conn_data()[current_socket]
    if to_authorize not in self.get_connected_users().keys():
        return ["error", "the user is not currently connected"]
    if to_authorize not in current_conn_data.get_authorize():
        while True:
            ask = input(PENDING_COLOR + "does %s can connect to %s\n'd' = denied\t'o' = ok" % (current_conn_data.get_user(), to_authorize))
            if ask in ['d', 'o']:
                break
            else:
                print(ERROR_COLOR + "try again ('d'/'o'")
        if ask == 'd':
            return ["error", "the server denied"]
        elif ask == 'o':
            current_conn_data.update_authorize(to_authorize)
            return ["ok", f"the server accepted your conn to {to_authorize}"]
    else:
        return ["error", "user already authorize to send"]


def connected(conn, self):
    current_conn_data: ConnectionData = self.get_conn_data()[conn]
    data = [f'{",".join(self.get_connected_users())}', f'{",".join(current_conn_data.get_authorize())}']
    return data



