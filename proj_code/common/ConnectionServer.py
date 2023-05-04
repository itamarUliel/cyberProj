import requests
import time

from proj_code.connection import *
from proj_code.common.colors import *


class ConnectionServer:
    @staticmethod
    def get_chat_server_address():
        while True:
            try:
                response = requests.get(f"http://{CONNECTION_SERVER_IP}:{CONNECTION_SERVER_PORT}/primary")
                if response.status_code == 200:
                    address = response.content.decode().split(":")
                    return (address[0], int(address[1]))
                else:
                    print(f"Got error {response.status_code} from connection server: {response.content.decode()}")
                    return None
            except ValueError:
                print(f"Invalid chat server address received")
                return None
            except Exception:
                print("Error connecting connection server, Retry in 5 sec")
                time.sleep(5)

    @staticmethod
    def get_backup_server_address():
        while True:
            try:
                response = requests.get(f"http://{CONNECTION_SERVER_IP}:{CONNECTION_SERVER_PORT}/backup")
                if response.status_code == 200:
                    address = response.content.decode().split(":")
                    return (address[0], int(address[1]))
                else:
                    print(f"Got error {response.status_code} from connection server: {response.content.decode()}")
                    return None
            except ValueError:
                print(f"Invalid chat server address received")
                return None
            except Exception:
                print("Error connecting connection server, Retry in 5 sec")
                time.sleep(5)

    @staticmethod
    def put_primary_server(ip, port):
        while True:
            try:
                response = requests.put(f"http://{CONNECTION_SERVER_IP}:{CONNECTION_SERVER_PORT}/primary"
                                        , data= f"{ip}:{port}")
                if response.status_code == 200:
                    return True
                else:
                    print(f"Got error {response.status_code} from connection server: {response.content.decode()}")
                    time.sleep(5)
            except Exception:
                print("Error connecting connection server, Retry in 5 sec")
                time.sleep(5)

    @staticmethod
    def put_backup_server(ip, port):
        while True:
            try:
                response = requests.put(f"http://{CONNECTION_SERVER_IP}:{CONNECTION_SERVER_PORT}/backup"
                                        , data=f"{ip}:{port}")
                if response.status_code == 200:
                    return True
                else:
                    print(f"Got error {response.status_code} from connection server: {response.content.decode()}")
                    time.sleep(5)
            except Exception:
                print("Error connecting connection server, Retry in 5 sec")
                time.sleep(5)

    @staticmethod
    def put_new_server(ip, port):
        while True:
            try:
                response = requests.put(f"http://{CONNECTION_SERVER_IP}:{CONNECTION_SERVER_PORT}/new_server"
                                        ,data=f"{ip}:{port}")
                if response.status_code == 200:
                    return response.content.decode()
                elif response.status_code == 409:
                    print(response.content.decode())
                    return None
                else:
                    raise Exception
            except Exception:
                print("Error connecting connection server, Retry in 5 sec")
                time.sleep(5)

    @staticmethod
    def put_free_backup():
        try:
            response = requests.put(f"http://{CONNECTION_SERVER_IP}:{CONNECTION_SERVER_PORT}/free_backup")
            if response.status_code == 200:
                print(response.content.decode())
            elif response.status_code == 501:
                print(response.content.decode())
        except Exception:
            print("unable to connected conn server")

    @staticmethod
    def put_switch_servers():
        try:
            response = requests.put(f"http://{CONNECTION_SERVER_IP}:{CONNECTION_SERVER_PORT}/switch_servers")
            if response.status_code == 200:
                print(response.content.decode())
            elif response.status_code == 501:
                print(response.content.decode())
        except Exception:
            print("unable to switch")

def test():
    print(DATA_COLOR + "utils demo", PENDING_COLOR + "work only on unused conn server.")
    print(OK_COLOR + "new server putting:")
    resp = ConnectionServer.put_new_server("127.0.0.1", 4545)
    print(resp)
    if resp == "primary":
        print(ConnectionServer.get_chat_server_address())
    else:
        raise Exception

    resp = ConnectionServer.put_new_server("127.0.0.1", 4444)
    print(resp)
    if resp == "backup":
        print(ConnectionServer.get_backup_server_address())
    else:
        raise Exception

    resp = ConnectionServer.put_new_server("127.0.0.1", 7777)
    print(resp, "\n")

    print(OK_COLOR + "backup freeing:")
    ConnectionServer.put_free_backup()
    print(ConnectionServer.get_backup_server_address(), "\n")

    print(OK_COLOR + "resseting backup for switch demo:")
    resp = ConnectionServer.put_new_server("127.0.0.1", 76767)
    print(resp)
    if resp == "backup":
        print(ConnectionServer.get_backup_server_address(), "\n")
    else:
        raise Exception

    print(OK_COLOR + "switching now:")
    print(ConnectionServer.get_chat_server_address())
    print(ConnectionServer.get_backup_server_address())
    ConnectionServer.put_switch_servers()
    print(ConnectionServer.get_chat_server_address())
    print(ConnectionServer.get_backup_server_address())
    print(OK_COLOR + "adding backup")
    resp = ConnectionServer.put_new_server("127.0.0.1", 9999)
    print(resp)
    if resp == "backup":
        print(ConnectionServer.get_backup_server_address())
    else:
        raise Exception
def main():
    test()

if __name__ == '__main__':
    main()
