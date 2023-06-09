import select
from threading import Thread
import argparse

from proj_code.server import *
from proj_code.server.ServerConnectionHandler import ServerConnectionHandler
from proj_code.server.BackupConnectionHandler import BackupConnectionHandler
from proj_code.common import *
from proj_code.common import ChatProtocol

ENCRYPT_CONNECTION_STATUS = "encrypt"
PENDING_CONNECTION_STATUS = "pending"
COMM_CONNECTION_STATUS = "comm"


class ChatServer:

    def __init__(self, address):

        self.__is_primary = None
        self.__update_chk = False
        self.__is_active = False
        self.__backup_data = {}
        self.__server_keys = None
        self.__backup_thread = None

        self.__conn_handler = ServerConnectionHandler(address)
        self.__backup_handler = BackupConnectionHandler()

        self.__user_handler = UserHandler()

    def start_running(self):
        self.start_server()
        self.register_server()
        if self.__is_primary:
            self.connect_backup()
            self.start_listening()
        else:
            self.start_sync()

    def register_server(self):
        self.__is_primary = self.__conn_handler.register_server()

    def connect_backup(self):
        self.__backup_thread = Thread(target=BackupConnectionHandler.connect, args=[self.__backup_handler, self.__conn_handler.get_all_conn_data()]).start()

    def start_server(self):
        self.__server_keys = EncryptionUtils.get_keys(KEY_SIZE)
        print(OK_COLOR + "START_SERVER: server got keys!", end="\n\n")
        self.__conn_handler.start()

    def get_server_socket(self):
        return self.__conn_handler.get_server_socket()

    def __get_server_private_key(self):
        return self.__server_keys["pr"]

    def __get_server_public_key(self):
        return self.__server_keys["pb"]

    def __add_connection(self, connection, conn_data=False):
        self.__conn_handler.add_connection(connection, conn_data)

    def __close_connection(self, connection):
        return self.__conn_handler.close_connection(connection)

    def get_username(self, connection):
        return self.__conn_handler.get_username(connection)

    def get_status(self, connection):
        return self.__conn_handler.get_status(connection)

    def set_status(self, connection, status):
        self.__conn_handler.set_status(connection, status)

    def get_authorize(self, connection):
        return self.__conn_handler.get_authorize(connection)

    def set_authorize(self, connection, to_authorize):
        self.__conn_handler.set_authorize(connection, to_authorize)

    def update_authorize(self, connection, to_authorize):
        self.__conn_handler.update_authorize(connection, to_authorize)

    def update_waiting(self, want_to_wait_socket, to_ask_user):
        self.__conn_handler.update_waiting(want_to_wait_socket, to_ask_user)

    def get_public_key(self, connection):
        return self.__conn_handler.get_public_key(connection)

    def set_public_key(self, connection, public_key):
        self.__conn_handler.set_public_key(connection, public_key)

    def get_write_socket(self, connection):
        return self.__conn_handler.get_write_socket(connection)

    def set_write_socket(self, connection, write_socket):
        return self.__conn_handler.set_write_socket(connection, write_socket)

    def update_backup(self):
        return self.__backup_handler.update(self.__conn_handler.get_all_conn_data())

    def print_connected_users(self):
        self.__conn_handler.print_connected_users()

    def receive_message(self, connection):
        return self.__conn_handler.receive_message(connection)

    def handle_close(self, connection):
        username = self.get_username(connection)

        self.__update_chk = self.__close_connection(connection)
        self.__user_handler.close_user(username)
        print(OK_COLOR + "\n\nHANDLE_CLOSE: done closing!")
        self.print_connected_users()

    def send_message(self, connection, msg):
        self.__conn_handler.send_message(connection, msg)

    def get_connected_and_authorized(self, conn):
        return self.__conn_handler.get_connected_and_authorized(conn)

    def is_connected(self, user):
        return self.__conn_handler.is_connected(user)

    def is_authorized(self, source, target):
        return self.__conn_handler.is_authorized(source, target)

    def is_waiting(self, current_socket, to_wait):
        return self.__conn_handler.is_waiting(current_socket, to_wait)

    def is_in_waiting(self, current_socket, to_allow):
        return self.__conn_handler.is_in_waiting(current_socket,to_allow)

    def push_message(self, target, msg):
        self.__conn_handler.push_message(target, msg)

    def connect_wconn(self, current_socket, ip, port):
        try:
            self.__conn_handler.connect_wconn(current_socket, ip, port)
            return ChatProtocol.build_ok_message()
        except:
            print("unable to connect sendable conn")
            return ChatProtocol.build_error_message("unable to connect, please check and send again")

    def get_waiting_list(self, current_socket):
        return [WAITING_COMMAND, self.__conn_handler.get_waiting_list(current_socket)]

    def sendto_msg(self, conn, send_to, msg):
        if self.is_connected(send_to):
            print(DATA_COLOR + f"{self.get_username(conn)} wants to send {send_to} this: {msg}")
            if self.is_authorized(conn, send_to):
                try:
                    self.push_message(send_to, ChatProtocol.build_push_msg(self.get_username(conn), msg)) # msg|sender|{msg}
                except Exception as e:
                    print(e)
                    print(ERROR_COLOR + "error happened while sending, msg didn't send!")
                    return ChatProtocol.build_error_message("problem accrue while sending the msg")
                else:
                    print(OK_COLOR + "msg sent!")
                    return ChatProtocol.build_ok_message("msg send")
            else:
                print(ERROR_COLOR + "user unauthorized to send!")
                return ChatProtocol.build_error_message(f"the sender is not authorize to send {send_to}")
        else:
            return ChatProtocol.build_error_message(f"{send_to} is not currently connected (or exist)")

    def authorize(self, current_socket, ask_to_authorize):
        if not self.is_connected(ask_to_authorize):
            return ChatProtocol.build_error_message("the user is not currently connected")
        if not self.is_authorized(current_socket, ask_to_authorize):
            if not self.is_waiting(current_socket, ask_to_authorize):
                self.update_waiting(current_socket, ask_to_authorize)
                return ChatProtocol.build_ok_message(f"the server ask {ask_to_authorize} to authorize you")
            else:
                return ChatProtocol.build_ok_message(f"you already asked {ask_to_authorize} to authorize you")
        else:
            return ChatProtocol.build_ok_message("user already authorize to send")

    def allow(self, current_socket, to_allow):
        if not self.is_connected(to_allow):
            return ChatProtocol.build_error_message(f"{to_allow} is not currently connected")

        if self.is_in_waiting(current_socket, to_allow):
            self.__conn_handler.allow(current_socket, to_allow)
            self.__update_chk = True
            return ChatProtocol.build_ok_message(f"{to_allow} is now allowed to send you message")
        else:
            return ChatProtocol.build_error_message(f"{to_allow} didn't ask to get allowed")
    def encrypt(self, current_socket, msg):
        command, data = ChatProtocol.parse_command(msg)
        try:
            if command == START_ENCRYPT_COMMAND:  # s: start_enc| r: ok| s: client_key r: server_key
                self.__conn_handler.share_public_keys(current_socket, self.__get_server_public_key())
                self.set_status(current_socket, PENDING_CONNECTION_STATUS)
            else:
                raise Exception

        except:
            print(ERROR_COLOR + f"{current_socket.getpeername()} failed to enc, error while replacing keys")
            self.send_message(current_socket, ChatProtocol.build_error_message("error while replacing keys"))

    def comm(self, current_socket, msg):

        msg = EncryptionUtils.decrypt(msg, self.__get_server_private_key())
        command, data = ChatProtocol.parse_command(msg)

        if command == AUTHORIZE_COMMAND:  # authorize|us
            try:
                res = self.authorize(current_socket, data[0])
                self.send_message(current_socket, res)
                self.__update_chk = True
            except ValueError:
                pass

        elif command == CONNECTED_COMMAND:  # connected|
            res = self.get_connected_and_authorized(current_socket)  # "[connected],[authorize]"
            self.send_message(current_socket, res)

        elif command == SEND_MESSAGE_COMMAND:  # sendto_msg|userToSend|msg
            res = self.sendto_msg(current_socket, data[0], data[1])
            self.send_message(current_socket, res)

        elif command == CLOSE_COMMAND:  # close|
            print(ERROR_COLOR + f"{self.get_username(current_socket)} ask to close, closing...")
            self.handle_close(current_socket)

        elif command == WAITING_COMMAND:   # see_waiting|
            waiting_msg = self.get_waiting_list(current_socket)
            self.send_message(current_socket, waiting_msg)

        elif command == ALLOW_COMMAND:       #allow|to_allow
            res = self.allow(current_socket, data[0])
            self.send_message(current_socket, res)

        else:
            self.send_message(current_socket, ChatProtocol.build_error_message("illegible command, closing connection"))
            print(ERROR_COLOR + f"{current_socket.getpeername()} is unknown and broke protocol, closing...")
            self.handle_close(current_socket)

    def pending(self, current_socket, msg):
        msg = EncryptionUtils.decrypt(msg, self.__get_server_private_key())
        command, data = ChatProtocol.parse_command(msg)
        if command == LOGIN_COMMAND:  # send: login|us|ps  # recv: ok/error|response
            username, pwd = data
            response = self.__user_handler.login(username, pwd)
            print(DATA_COLOR + "LOGIN: the login try went: ", response[1])
            if response[0]:
                self.send_message(current_socket, ChatProtocol.build_ok_message(response[1]))
                self.__conn_handler.add_connected_user(username, current_socket)
                if self.__is_active and username in self.__backup_data.keys():
                    self.set_authorize(current_socket, self.__backup_data[username])
            else:
                self.send_message(current_socket, ChatProtocol.build_error_message(response[1]))

        elif command == WCONN_COMMAND and self.get_username(current_socket) is not None:  # send: wconn|ip|port recv:ok/error|response
            ip, port = data
            res = self.connect_wconn(current_socket, ip, port)
            self.send_message(current_socket, res)
            if ChatProtocol.is_ok_status(res):
                self.set_status(current_socket, COMM_CONNECTION_STATUS)
                print(DATA_COLOR + f"{self.get_username(current_socket)} is now ready to comm!")

        elif command == CLOSE_COMMAND:  # send: close|
            print(ERROR_COLOR + f"{current_socket.getpeername()} ask to close, closing...")
            self.send_message(current_socket, ChatProtocol.build_ok_message())
            self.handle_close(current_socket)
        else:
            self.send_message(current_socket, ChatProtocol.build_error_message("illegible command, closing connection"))
            print(ERROR_COLOR + f"{current_socket.getpeername()} is unknown and broke protocol, closing...")
            self.handle_close(current_socket)

    def switch_servers(self):
        ConnectionUtils.put_switch_servers()
        self.__conn_handler.restart_as_primary()

    def start_sync(self):
        try:
            self.__conn_handler.open_as_backup(self.__get_server_public_key())
            data = True
            while data:
                data = self.__conn_handler.get_backup_update(self.__get_server_private_key())
                print(DATA_COLOR + f"got backup: {data}")
                if data == "nothing to share.":
                    continue
                self.__backup_data = ChatProtocol.load_backup(data)
        except ConnectionResetError:
            self.switch_servers()
            self.__is_active = True
            self.__is_primary = True
            self.connect_backup()
            self.start_listening()

    def start_listening(self):
        self.__add_connection(self.get_server_socket())
        print(PENDING_COLOR + "LISTEN: listening started")
        while self.__conn_handler.get_connections_list():
            readable, writable, exceptional = select.select(self.__conn_handler.get_connections_list(), [], [])
            for current_socket in readable:
                if current_socket is self.get_server_socket():
                    # New connection
                    connection, client_address = current_socket.accept()
                    print(DATA_COLOR + f'LISTEN: new connection from {client_address}', end="\n\n")
                    self.__add_connection(connection, True)
                else:  # s.getpeername()
                    try:
                        data = self.receive_message(current_socket)
                        if data:
                            if self.get_status(current_socket) == ENCRYPT_CONNECTION_STATUS:
                                self.encrypt(current_socket, data.decode())
                            elif self.get_status(current_socket) == PENDING_CONNECTION_STATUS:
                                self.pending(current_socket, data)
                            elif self.get_status(current_socket) == COMM_CONNECTION_STATUS:
                                self.comm(current_socket, data)
                        else:
                            raise ConnectionResetError
                    except ConnectionResetError:
                        # Interpret empty result as closed connection
                        print(ERROR_COLOR + f'\n\nclosing {current_socket.getpeername()}, he died')
                        # Stop listening for input on the connection
                        self.handle_close(current_socket)
            if self.__is_primary and self.__update_chk and self.__backup_handler.is_backed_up():
                self.__update_chk = not self.update_backup()
                if self.__update_chk is True:
                    ConnectionUtils.put_free_backup()
                    self.connect_backup()



def main(ip=DEFAULT_IP, port=0):
    server = ChatServer((ip, port))
    server.start_running()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str)
    parser.add_argument('--port', type=int)
    args = parser.parse_args()
    main(args.ip if args.ip is not None else DEFAULT_IP, args.port if args.port is not None else 0)
