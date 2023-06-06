import socket
local_ip = socket.gethostbyname(socket.gethostname())


CONNECTION_SERVER_IP = local_ip
CONNECTION_SERVER_PORT = 5000


PRIMARY_IP = "127.0.0.1"
PRIMARY_PORT = 5555
PRIMARY_NAME = "primary"

SECONDARY_IP = "127.0.0.1"
SECONDARY_PORT = 7890
SECONDARY_NAME = "secondary"

WCONN_IP = local_ip

MSG_SIZE = 4000