import select
import socket
from server_values import *
initialize()
from server_handeler import *
server_keys = None


BYTE_SIZE = 4000
# Bind the socket to the port
def start_server():
    global server_keys
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_address = ("127.0.0.1", 7777)
    server.bind(socket_address)
    server.listen()
    server_keys = Encryption_handeler.get_keys(1500)
    print("START_SERVER: LISTENING AT:", socket_address)
    print("START_SERVER: server got keys!", end="\n\n")
    return server


def handle_close(s):
    global connected_users
    global authorize_connection
    global users_keys

    try:
        print(f"HANDLE_CLOSE: closing {s.getpeername()} user: {connected_users[s]}")
    except:
        print(f"HANDLE_CLOSE: closing {s.getpeername()}")
    try:
        authorize_connection.pop(connected_users[s])
    except KeyError:
        pass

    try:
        users_keys.pop(s)
    except KeyError:
        pass

    try:
        connected_users.pop(s)
    except KeyError:
        pass
    print("HANDLE_CLOSE: done closing!")
    print(f"""HANDLE_CLOSE: dicts status:
              conncted_users: {connected_users}
              authorize_connection: {authorize_connection}
              users_keys: {users_keys}
    """, end="\n\n")


def sendmsgs(msg, s=None):
    global users_keys

    if s is None:
        print("SENDMSGS: sending-", "|".join(msg).encode())
        return "|".join(msg).encode()
    else:
        print("SENDMSGS: sending-", Encryption_handeler.encrypt("|".join(msg), users_keys[s]), end="\n\n")
        return Encryption_handeler.encrypt("|".join(msg), users_keys[s])


def start_listening(server):
    global known_users
    global connected_users
    global users_keys
    global authorize_connection

    inputs = [server]
    print("LISTEN: listening started")
    while inputs:
        readable, writable, exceptional = select.select(inputs, [], [])
        for s in readable:
            if s is server:
                # New connection
                connection, client_address = s.accept()
                print(f'LISTEN: new connection from {client_address}', end="\n\n")
                inputs.append(connection)

            else:  # s.getpeername()
                data = s.recv(BYTE_SIZE)
                if data:
                    if s not in users_keys.keys():
                        print(f"LISTEN: {s.getpeername()} sending NOT ENCR \nmsg:{data.decode()}", end="\n\n")
                        data = data.decode().split("|")
                        command, c_data = data[0], data[1:]
                        if command == "close":
                            print(f"LISTEN: {s.getpeername()} asked to start closing")
                            inputs.remove(s)
                            handle_close(s)
                            s.close()
                        else:
                            if command == "login":          # login|user|password
                                print(f"LISTEN: {s.getpeername()} begin to login")
                                returned = login([s] + c_data)
                                if returned[0] == "ok":
                                    print(f"LISTEN: user {connected_users[s]} is now conncted, conn: {s.getpeername()}")
                                    s.sendall("ok|None".encode())
                                else:
                                    print(f"LISTEN: {s.getpeername()} connection failed, error msg: {returned}")
                                    s.sendall(sendmsgs(returned))
                            else:
                                if s not in connected_users.keys():
                                    print(f"LISTEN: {s.getpeername()} is unknown, the server blocks him")
                                    s.sendall("error|unauthorized user, connection closed".encode())
                                    inputs.remove(s)
                                    handle_close(s)
                                    s.close()

                                else:
                                    if command == "start_encrypt":   # start_encrypt|pb
                                        print(f"LISTEN: {connected_users[s]} start to ENC")
                                        s.sendall(sendmsgs(["ok"]))
                                        key = s.recv(BYTE_SIZE)
                                        start_encrypt(key, s)
                                        s.sendall(Encryption_handeler.save_public(server_keys["pb"]))
                                        print(f"LISTEN: {connected_users[s]} done ENC!\nhis pb:\t{users_keys[s]}")

                                    elif command == "ok":
                                        print("client response successfully")
                                        s.sendall("ok|None".encode())

                    else:              # data received is now encrypted
                        if s not in connected_users.keys():
                            print("ENC_LISTEN: unauthorized user found, the server closed connection", s.getpeername())
                            s.sendall("error|unauthorized user, connection closed".encode())
                            inputs.remove(s)
                            handle_close(s)
                            s.close()
                        else:
                            print(f"ENC_LISTEN: got an ENC msg from {connected_users[s]}")
                            data = Encryption_handeler.decrypt(data, server_keys["pr"])
                            print("the msg:", data)
                            data = data.split("|")
                            command, c_data = data[0], data[1:]
                            if command == "close":
                                inputs.remove(s)
                                handle_close(s)
                                s.close()

                            elif command == "authorize":     # authorize|want2chat
                                data = authorize(connected_users[s], c_data)
                                s.sendall(sendmsgs(data, s))

                            elif command == "sendto_msg":         # sendto_msg|sendto|data
                                data = sendto_msg(s, c_data[0], c_data[1])
                                s.sendall(sendmsgs(data, s))

                            elif command == "connected":
                                print("faf")
                                data = conncted(s)
                                s.sendall(Encryption_handeler.encrypt(data, users_keys[s]))
                else:
                    # Interpret empty result as closed connection
                    print(f'closing {client_address}, he died')
                    # Stop listening for input on the connection
                    inputs.remove(s)
                    handle_close(s)
                    s.close()


def main():
    server = start_server()
    start_listening(server)


if __name__ == '__main__':
    main()

