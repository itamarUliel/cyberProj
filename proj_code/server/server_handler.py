import socket

from proj_code.common import *
from proj_code.server import *


def get_free_port(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def load_backup(data): # data = b"us1:a1,a2,a3|us2..."
    backup = {}
    for user in data.split("|"):
        if user == "":
            continue
        us, authorize_list = user.split(":")[0], user.split(":")[1].split(",")
        backup[us] = authorize_list
    return backup








