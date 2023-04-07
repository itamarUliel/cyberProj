import socket
import Encryption_handler
from colors import *
from network_utils import *
from server_handler import *

class ChatServer:
    def __init__(self, is_primary, address):
        self.__address = address
        self.__server_keys = None
        self.__server_socket: socket.socket = None
        self.__is_primary = is_primary

    def start_server(self):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind(self.__address)
        self.__server_socket.listen()
        print(DATA_COLOR + "START_SERVER: LISTENING AT:", self.__address)

        self.__server_keys = Encryption_handler.get_keys(KEY_SIZE)
        print(OK_COLOR + "START_SERVER: server got keys!", end="\n\n")

    def get_server_socket(self):
        return self.__server_socket

    def get_server_keys(self):
        return self.__server_keys


class PrimaryServer(ChatServer):
    def __init__(self):
        super().__init__(True, PRIMARY_ADDRESS)
        self.__backup_public_key = None
        self.__backup_socket = None
        self.start_server()

    def start_server(self):
        super().start_server()
        self.connect_backup()

    def get_backup_socket(self):
        return self.__backup_socket

    def get_backup_public_key(self):
        return self.__backup_public_key

    def connect_backup(self):
        self.__backup_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__backup_socket.connect(SECONDARY_ADDRESS)
        self.__backup_public_key = Encryption_handler.load_public(self.__backup_socket.recv(RECEIVE_SIZE))
        print(OK_COLOR + "backup is conncted!")


class BackupServer(ChatServer):
    def __init__(self):
        super().__init__(False, SECONDARY_ADDRESS)
        self.start_sync()
        self.__is_active = False
        self.__backup_data = None

    def start_sync(self):
        try:
            super().start_server()
            prime, address = self.get_server_socket().accept()
            prime.sendall(Encryption_handler.save_public(self.get_server_keys()["pb"]))
            data = True
            while data:
                data = Encryption_handler.decrypt(prime.recv(RECEIVE_SIZE), self.get_server_keys()["pr"])
                print(DATA_COLOR + f"got backup: {data}")
                if data == "nothing to share.":
                    continue
                self.__backup_data = load_backup(data)
        except ConnectionResetError:
            prime.close()
            self.get_server_socket().close()
            print(ERROR_COLOR + "prime server is down!")
            print(DATA_COLOR + "active backup!")
            self.__is_active = True
            super().start_server()

    def get_backup_data(self):
        return self.__backup_data











