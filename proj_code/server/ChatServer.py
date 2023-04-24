import socket
import time

import select

from proj_code.common import *
from proj_code.server import *
from proj_code.server.ServerConnectionHandler import ServerConnectionHandler


class ChatServer:

    def __init__(self, is_primary, address):

        self.__is_primary = is_primary
        self.__update_chk = False
        self.__backup_public_key = None
        self.__backup_socket: socket.socket = None
        self.__is_active = False
        self.__backup_data = None

        self.__conn_handler = ServerConnectionHandler(address)
        self.__user_handler = UserHandler()

    def start_running(self):
        if self.__is_primary:
            self.start_server()
            self.connect_backup()
            self.start_listening()
        else:
            self.start_sync()

    def get_backup_socket(self):
        return self.__backup_socket

    def get_backup_public_key(self):
        return self.__backup_public_key

    def connect_backup(self):
        self.__backup_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__backup_socket.connect(SECONDARY_ADDRESS)
        self.__backup_public_key = Encryption_handler.load_public(self.__backup_socket.recv(RECEIVE_SIZE))
        print(OK_COLOR + "backup is connected!")

    def start_server(self):
        self.__conn_handler.start()

    def get_server_socket(self):
        return self.__conn_handler.get_server_socket()

    def get_server_keys(self):
        return self.__conn_handler.get_server_keys()

    def add_connection(self, connection, conn_data=False):
        self.__conn_handler.add_connection(connection, conn_data)

    def get_all_conn_data(self):
        return self.__conn_handler.get_all_conn_data()

    def get_is_primary(self):
        return self.__is_primary

    def get_username(self, connection):
        return self.__conn_handler.get_username(connection)

    def set_username(self, connection, username):
        return self.__conn_handler.set_username(connection, username)

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

    def get_public_key(self, connection):
        return self.__conn_handler.get_public_key(connection)

    def set_public_key(self, connection, public_key):
        self.__conn_handler.set_public_key(connection, public_key)

    def get_write_socket(self, connection):
        return self.__conn_handler.get_write_socket(connection)

    def set_write_socket(self, connection, write_socket):
        return self.__conn_handler.set_write_socket(connection, write_socket)

    def get_connected_users(self):
        return self.__conn_handler.get_connected_users()

    def update_connected_users(self, key, value):
        self.__conn_handler.add_connected_user(key, value)

    def get_backup_data(self):
        return self.__backup_data

    def handle_close(self, connection):
        username = self.get_username(connection)

        try:
            self.__update_chk = self.__conn_handler.close_connection(connection)
        except ValueError:
            pass

        try:
            self.__user_handler.close_user(username)
        except KeyError:
            pass

        print(OK_COLOR + "\n\nHANDLE_CLOSE: done closing!")
        print(DATA_COLOR + f"""HANDLE_CLOSE: 
           connected users: {self.__conn_handler.get_connected_users()}     
        """, end="\n\n")

    def send_msgs(self, msg, conn=None):
        if conn is None:
            return "|".join(msg).encode()
        else:
            return Encryption_handler.encrypt("|".join(msg), self.get_public_key(conn))

    def connected(self, conn):
        return [f'{",".join(self.get_connected_users())}', f'{",".join(self.get_authorize(conn))}']

    def sendto_msg(self, conn, send_to, msg):
        if send_to in self.get_connected_users().keys():
            print(DATA_COLOR + f"{self.get_username(conn)} wants to send {send_to} this: {msg}")
            if send_to in self.get_authorize(conn):
                try:
                    send_msg = "msg|%s|%s" % (self.get_username(conn), msg)  # msg|sender|{msg}
                    target_user_connection = self.get_connected_users()[send_to]
                    wconn = self.get_write_socket(target_user_connection)
                    send_msg = Encryption_handler.encrypt(send_msg, self.get_public_key(target_user_connection))
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

    def authorize(self, current_socket, to_authorize):
        if to_authorize not in self.get_connected_users().keys():
            return ["error", "the user is not currently connected"]
        if to_authorize not in self.get_authorize(current_socket):
            while True:
                # ask = input(PENDING_COLOR + "does %s can connect to %s\n'd' = denied\t'o' = ok" % (current_conn_data.get_user(), to_authorize))
                ask = 'o'
                if ask in ['d', 'o']:
                    break
                else:
                    print(ERROR_COLOR + "try again ('d'/'o'")
            if ask == 'd':
                return ["error", "the server denied"]
            elif ask == 'o':
                self.update_authorize(current_socket, to_authorize)
                return ["ok", f"the server accepted your conn to {to_authorize}"]
        else:
            return ["error", "user already authorize to send"]

    def encrypt(self, current_socket: socket.socket, msg):
        command, data = msg.split("|")[0], msg.split("|")[1:]
        error_msg = "error while replacing keys"
        try:
            if command == "start_enc":  # s: start_enc| r: ok| s: client_key r: server_key
                current_socket.sendall(ChatProtocol.built_ok().encode())
                key = current_socket.recv(RECEIVE_SIZE)
                self.set_public_key(current_socket, Encryption_handler.load_public(key))
                current_socket.sendall(Encryption_handler.save_public(self.get_server_keys()["pb"]))
                self.set_status(current_socket, "pending")
            else:
                raise Exception

        except:
            print(ERROR_COLOR + f"{current_socket.getpeername()} failed to enc, reason: {error_msg}")
            current_socket.sendall(ChatProtocol.built_error(error_msg).encode())

    def comm(self, current_socket, msg):

        msg = Encryption_handler.decrypt(msg, self.get_server_keys()["pr"])
        command, data = msg.split("|")[0], msg.split("|")[1:]

        if command == "authorize":  # authorize|us
            res = self.authorize(current_socket, data[0])
            current_socket.sendall(self.send_msgs(res, current_socket))
            try:
                self.__update_chk = True
            except ValueError:
                pass
        elif command == "connected":  # connected|
            data = self.connected(current_socket)  # "[connected],[authorize]"
            current_socket.sendall(self.send_msgs(data, current_socket))  # ["user1,user2,user3","user1,user3"]

        elif command == "sendto":  # sendto_msg|userToSend|msg
            res = self.sendto_msg(current_socket, data[0], data[1])
            current_socket.sendall(self.send_msgs(res, current_socket))

        elif command == "close":  # close|
            print(ERROR_COLOR + f"{self.get_username(current_socket)} ask to close, closing...")
            self.__conn_handler.remove_connection(current_socket)
            self.handle_close(current_socket)
        else:
            print(ERROR_COLOR + f"{current_socket.getpeername()} is unknown and broke protocol, closing...")
            current_socket.sendall(self.send_msgs(["error", "illegible command, closing connection"]))
            self.__conn_handler.remove_connection(current_socket)
            self.handle_close(current_socket)

    def start_sync(self):
        try:
            self.start_server()
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
            self.start_server()
            self.start_listening()

    def start_listening(self):
        self.__conn_handler.add_connection(self.get_server_socket())
        print(PENDING_COLOR + "LISTEN: listening started")
        while self.__conn_handler.get_connections_list():
            readable, writable, exceptional = select.select(self.__conn_handler.get_connections_list(), [], [])
            for current_socket in readable:
                if current_socket is self.get_server_socket():
                    # New connection
                    connection, client_address = current_socket.accept()
                    print(DATA_COLOR + f'LISTEN: new connection from {client_address}', end="\n\n")
                    self.add_connection(connection, True)
                else:  # s.getpeername()
                    try:
                        data = current_socket.recv(RECEIVE_SIZE)
                        if data:
                            if self.get_status(current_socket) == "encrypt":
                                self.encrypt(current_socket, data.decode())
                            elif self.get_status(current_socket) == "pending":
                                self.pending(current_socket, data)
                            elif self.get_status(current_socket) == "comm":
                                self.comm(current_socket, data)
                        else:
                            raise ConnectionResetError
                    except ConnectionResetError:
                        # Interpret empty result as closed connection
                        print(ERROR_COLOR + f'\n\nclosing {current_socket.getpeername()}, he died')
                        # Stop listening for input on the connection
                        self.__conn_handler.remove_connection(current_socket)
                        self.handle_close(current_socket)
            if self.__is_primary and self.__update_chk:
                try:
                    print(self.__backup_socket)
                    self.__backup_socket.sendall(Encryption_handler.encrypt(save_backup(self.get_all_conn_data()), self.__backup_public_key))
                    self.__update_chk = False
                except ConnectionResetError:
                    print(ERROR_COLOR + "couldnt backup")
                    self.__update_chk = False

    def connect_write(self, current_socket, ip, port):
        try:
            wconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            wconn.connect((ip, int(port)))
            self.set_write_socket(current_socket, wconn)
            wconn.sendall(Encryption_handler.encrypt("ok|the server connected 2 U, you can start recv msg!",
                                                     self.get_public_key(current_socket)))
            return ["ok", ""]
        except:
            print("unable to connect sendable conn")
            return ["error", "unable to connect, please check and send again"]

    def pending(self, current_socket, msg):
        msg = Encryption_handler.decrypt(msg, self.__conn_handler.get_private_key())
        command, data = msg.split("|")[0], msg.split("|")[1:]
        if command == "login":  # send: login|us|ps  # recv: ok/error|response
            # response = login(current_socket, data, self)
            username, pwd = data
            response = self.__user_handler.login(username, pwd)
            print(DATA_COLOR + "LOGGIN: the login try went: ", response[1])
            if response[0]:
                current_socket.sendall(Encryption_handler.encrypt(ChatProtocol.built_ok(response[1]),
                                                                  self.get_public_key(current_socket)))
                self.set_username(current_socket, username)
                self.__conn_handler.add_connected_user(username, current_socket)
                if not self.__is_primary and username in self.__backup_data.keys():
                    self.set_authorize(current_socket, self.__backup_data[username])
            else:
                current_socket.sendall(Encryption_handler.encrypt(ChatProtocol.built_ok(response[1]),
                                                                  self.get_public_key(current_socket)))

        elif command == "wconn" and self.get_username(current_socket) is not None:  # send: wconn|ip|port recv:ok/error|response
            ip, port = data
            res = self.connect_write(current_socket, ip, port)
            if res[0] == "ok":
                current_socket.sendall(self.send_msgs(res, current_socket))
                print(DATA_COLOR + f"{self.get_username(current_socket)} is now ready to comm!")
                self.set_status(current_socket, "comm")
            else:
                current_socket.sendall(self.send_msgs(res, current_socket))

        elif command == "close":  # send: close|
            print(ERROR_COLOR + f"{current_socket.getpeername()} ask to close, closing...")
            current_socket.sendall(self.send_msgs(ChatProtocol.built_ok(), current_socket))
            self.__conn_handler.remove_connection(current_socket)
            self.handle_close(current_socket)
        else:
            current_socket.sendall(self.send_msgs(["error", "illegible command, closing connection"], current_socket))
            print(ERROR_COLOR + f"{current_socket.getpeername()} is unknown and broke protocol, closing...")
            self.__conn_handler.remove_connection(current_socket)
            self.handle_close(current_socket)


class PrimaryServer(ChatServer):
    def __init__(self):
        super().__init__(True, PRIMARY_ADDRESS)
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
        self.__is_active = False
        self.__backup_data = None
        self.start_sync()

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

