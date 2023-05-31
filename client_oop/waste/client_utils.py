def initialize():
    global client_keys, server_public_key, wconn_keys
    global wconn_ip, BYTE_SIZE, backup_bind, user_backup, server_address

    client_keys = None
    server_public_key = None
    wconn_keys = None
    wconn_ip = "127.0.0.1"
    BYTE_SIZE = 5000
    backup_bind = None
    server_address = ('127.0.0.1', 5555)
    try:
        if user_backup is not None:
            pass
    except NameError:
        user_backup = None


BYTE_SIZE = 5000
