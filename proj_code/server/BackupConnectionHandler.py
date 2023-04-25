import socket
from proj_code.common import *


class BackupConnectionHandler:

    def __init__(self):
        self.__update_chk = False
        self.__backup_public_key = None
        self.__backup_socket: socket.socket = None

    def get_backup_public_key(self):
        return self.__backup_public_key

    def get_backup_socket(self):
        return self.__backup_socket

    def save_backup(self, data):
        backup = ""
        for s in data.keys():
            current_conn_data = data[s]
            user = current_conn_data.get_user()
            authorize_u = current_conn_data.get_authorize()
            if user is not None and authorize_u != []:
                backup += ":".join([user, ",".join(authorize_u)]) + "|"
        if backup == "":
            backup = "nothing to share."
        return backup

    def connect(self):
        self.__backup_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__backup_socket.connect(SECONDARY_ADDRESS)
        self.__backup_public_key = Encryption_handler.load_public(self.__backup_socket.recv(RECEIVE_SIZE))
        print(OK_COLOR + "backup is connected!")

    def update(self, connections_update):
        backup_updated = False
        try:
            self.__backup_socket.sendall(Encryption_handler.encrypt(self.save_backup(connections_update), self.__backup_public_key))
            backup_updated = True
        except ConnectionResetError:
            print(ERROR_COLOR + "couldnt backup")
            backup_updated = False

        return backup_updated
