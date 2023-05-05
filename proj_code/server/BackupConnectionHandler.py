import socket
import time

from proj_code.common import *

SLEEP_TIME = 30

class BackupConnectionHandler:

    def __init__(self):
        self.__backup_public_key = None
        self.__backup_socket: socket.socket = None
        self.__has_backup = False

    def get_backup_public_key(self):
        return self.__backup_public_key

    def get_backup_socket(self):
        return self.__backup_socket

    def is_backed_up(self):
        return self.__has_backup

    def set_backed_up(self, has_backup):
        self.__has_backup = has_backup

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

    @staticmethod
    def connect(backup_handler):
        while True:
            try:
                backup_handler.__backup_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                backup_handler.__backup_socket.connect(SECONDARY_ADDRESS)
                backup_handler.__backup_public_key = EncryptionUtils.load_public(backup_handler.__backup_socket.recv(RECEIVE_SIZE))
                print(OK_COLOR + "backup is connected!")
                backup_handler.set_backed_up(True)
                break
            except ConnectionRefusedError:
                print(ERROR_COLOR + f"couldn't connect backup, running without it, trying again in {SLEEP_TIME} seconds")
                backup_handler.set_backed_up(False)
                time.sleep(SLEEP_TIME)



    def update(self, connections_update):
        backup_updated = False
        try:
            self.__backup_socket.sendall(EncryptionUtils.encrypt(self.save_backup(connections_update), self.__backup_public_key))
            backup_updated = True
        except ConnectionResetError:
            print(ERROR_COLOR + "couldnt backup")
            backup_updated = False

        return backup_updated
