import requests
from connection_utils import *
import time

class ConnectionServer:

    @staticmethod
    def get_chat_server_address():
        while True:
            try:
                response = requests.get(f"http://{CONNECTION_SERVER_IP}:{CONNECTION_SERVER_PORT}/chat_server")
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
