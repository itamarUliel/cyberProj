import socket
import Encryption_handler
from colors import *
from network_utils import *


class ChatServer:
    def __init__(self, is_primary=True):
        if is_primary:
            self.address = PRIMARY_ADDRESS
        else:
            self.address = SECONDARY_ADDRESS

        self.server_keys = None
        self.backup_public_key = None
        self.server_socket = None
        self.backup_socket = None
        self.is_primary = is_primary

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.address)
        self.server_socket.listen()
        print(DATA_COLOR + "START_SERVER: LISTENING AT:", self.address)

        self.server_keys = Encryption_handler.get_keys(KEY_SIZE)
        print(OK_COLOR + "START_SERVER: server got keys!", end="\n\n")

        if self.is_primary:
            self.backup_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.backup_socket.connect(SECONDARY_ADDRESS)
            self.backup_public_key = Encryption_handler.load_public(self.backup_socket.recv(RECEIVE_SIZE))
            print(OK_COLOR + "backup is conncted!")
