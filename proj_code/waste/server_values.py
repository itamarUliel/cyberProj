def initialize():
    global known_users
    global connected_users
    global users_keys
    global authorize_connection
    global conn_data

    conn_data = {}
    known_users = {}  # {user: password,...}
    f = open("../server/users.txt", 'r')
    for line in f:
        us, ps = line.split("|")
        known_users[us] = ps.replace("\n", "")
    f.close()

    connected_users = {}           # {user: conn,...}
    users_keys = {}              # {conn: public_key,...}
    authorize_connection = {}    # {user1: [user2, user3], user2: [user1],...}


def server_constants(ks=500, rs=1024, ip="127.0.0.1", port=5555, client=False):
    if not client:
        keys_size = ks
        recv_size = rs
        bind = (ip, port)
        backup_address = ("127.0.0.1", 7890)
        return keys_size, recv_size, bind, backup_address
    else:
        bind = (ip, port)
        return bind
