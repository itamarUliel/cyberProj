import Encryption_handeler
from server_values import *

import colorama
from colorama import Back, Fore
colorama.init(autoreset=True)

error_c = Fore.BLACK + Back.RED
ok_c = Back.GREEN + Fore.BLACK
pending_c = Back.LIGHTBLUE_EX + Fore.BLACK
data_c = Back.LIGHTYELLOW_EX + Fore.GREEN


def login(s, data):    # data = [conn ,user, password]
    global known_users         # {user: password,...}
    global connected_users     # {user: conn,...}
    global conn_data
    try:
        if known_users[data[0]] == data[1]:   # 0: us 1: pass
            if data[0] not in connected_users.keys():
                conn_data[s]["user"] = data[0]
                connected_users[data[0]] = s
                print(ok_c + f"{data[0]} is now logged in!")
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
        print(data_c + f"{conn_data[conn]['user']} wants to send {send_to} this: {msg}")
        if send_to in conn_data[conn]["authorize"]:
            try:
                send_msg = "msg|%s|%s" % (conn_data[conn]["user"], msg)  # msg|sender|{msg}
                wconn = conn_data[connected_users[send_to]]["wconn"]
                send_msg = Encryption_handeler.encrypt(send_msg, conn_data[connected_users[send_to]]["wconn_key"])
                wconn.sendall(send_msg)
            except:
                print(error_c + "error happened while sending, msg didn't send!")
                return ["error", "problem accrue while sending the msg"]
            else:
                print(ok_c + "msg send!")
                return ["ok", "msg send"]
        else:
            print(error_c + "user unauthorized to send!")
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
            ask = input(pending_c + "does %s can connect to %s\n'd' = denied\t'o' = ok" % (conn_data[s]["user"], to_authorize))
            if ask in ['d', 'o']:
                break
            else:
                print(error_c + "try again ('d'/'o'")
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



