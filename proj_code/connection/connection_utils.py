import socket

CONNECTION_SERVER_IP = "127.0.0.1"
CONNECTION_SERVER_PORT = 5000

local_ip = socket.gethostbyname(socket.gethostname())

PRIMARY_IP = "127.0.0.1"
PRIMARY_PORT = 5555
PRIMARY_NAME = "primary"

SECONDARY_IP = "127.0.0.1"
SECONDARY_PORT = 7890
SECONDARY_NAME = "secondary"

WCONN_IP = "127.0.0.1"

MSG_SIZE = 4000