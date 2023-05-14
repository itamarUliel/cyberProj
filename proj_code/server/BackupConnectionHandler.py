import socket
import time

from proj_code.common import *


SLEEP_TIME = 20


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

    @staticmethod
    def save_backup(conn_data):
        return ChatProtocol.save_backup(conn_data)

    @staticmethod
    def connect(backup_handler, connections_data):
        while True:
            try:
                backup_handler.__backup_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                address = ConnectionUtils.get_backup_server_address()
                if address is None:
                    raise HasNoBackupException
                backup_handler.__backup_socket.connect(ConnectionUtils.get_backup_server_address())
                backup_handler.__backup_public_key = EncryptionUtils.load_public(backup_handler.__backup_socket.recv(RECEIVE_SIZE))
                backup_handler.update(connections_data)
                print(OK_COLOR + "backup is connected!")
                backup_handler.set_backed_up(True)
                break

            except HasNoBackupException:
                print(ERROR_COLOR + f"there is no backup, running without it, trying again in {SLEEP_TIME} seconds")
                backup_handler.set_backed_up(False)
                time.sleep(SLEEP_TIME)

            except ConnectionRefusedError:
                print(ERROR_COLOR + f"couldn't connect backup, running without it, trying again in {SLEEP_TIME} seconds")
                print(DATA_COLOR + "sending the connection server to free backup")
                ConnectionUtils.put_free_backup()
                backup_handler.set_backed_up(False)
                time.sleep(SLEEP_TIME)

    def update(self, conn_data):
        backup_updated = False
        try:
            self.__backup_socket.sendall(EncryptionUtils.encrypt(self.save_backup(conn_data), self.__backup_public_key))
            backup_updated = True
        except ConnectionResetError:
            print(ERROR_COLOR + "couldn't backup")
            backup_updated = False
        return backup_updated
