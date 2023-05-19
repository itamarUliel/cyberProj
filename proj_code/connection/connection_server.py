from flask import Flask, make_response, request, abort
import keyboard
import threading
from proj_code.common.colors import *
app = Flask(__name__)

PRIMARY_IP = "127.0.0.1"
PRIMARY_PORT = 5555
SECONDARY_IP = "127.0.0.1"
SECONDARY_PORT = 7890

DEFAULT_PRIMARY = f"{PRIMARY_IP}:{PRIMARY_PORT}"

primary_server = None
backup_server = None


def resetting():
    global primary_server, backup_server
    while True:
        event = keyboard.read_event()
        if event.name == 'esc' and event.event_type == 'down':
            print(DATA_COLOR + "servers reset! (will not work for old servers)")
            primary_server, backup_server = None, None


@app.route("/chat_server", methods=['GET'])
def get_chat_server():
    return get_primary()


@app.route("/primary", methods=['GET'])
def get_primary():
    global primary_server
    try:
        if primary_server is None:
            resp = make_response("Primary server not available", 400)
        else:
            resp = make_response(f"{primary_server[0]}:{primary_server[1]}", 200)
    except Exception:
        resp = make_response("Primary server not available", 400)
    return resp


@app.route("/backup", methods=['GET'])
def get_secondary():
    global backup_server
    try:
        if backup_server is None:
            resp = make_response("Backup server not available", 400)
        else:
            resp = make_response(f"{backup_server[0]}:{backup_server[1]}", 200)
    except Exception:
        resp = make_response("Backup server not available", 400)
    return resp


@app.route("/new_server", methods=['PUT'])
def put_new_server():
    global primary_server, backup_server
    try:
        server_address = request.data.decode().split(":")
        print("fefef", request.remote_addr)
        if primary_server is None:
            primary_server = (server_address[0], int(server_address[1]))
            resp = make_response("primary", 200)
            print(f"Added {server_address} as primary")
        elif backup_server is None:
            backup_server = (server_address[0], int(server_address[1]))
            print(f"Added {server_address} as backup")
            resp = make_response("backup", 200)
        else:
            resp = make_response("Your service is not currently needed please try again later", 409)
    except Exception:
        resp = make_response(f"unable to register", 500)
    return resp


@app.route("/primary", methods=['PUT'])
def put_primary():
    try:
        global primary_server
        server_address = request.data.decode().split(":")
        primary_server = f"{server_address[0]}:{server_address[1]}"
        resp = make_response(f"Primary updated {primary_server}", 200)
    except Exception:
        resp = make_response(f"Invalid server details", 400)
    return resp


@app.route("/backup", methods=['PUT'])
def put_backup():
    try:
        global backup_server
        server_address = request.data.decode().split(":")
        backup_server = f"{server_address[0]}:{server_address[1]}"
        resp = make_response(f"Backup updated {backup_server}", 200)
    except Exception:
        resp = make_response(f"Invalid server details", 400)
    return resp


@app.route("/free_backup", methods=['PUT'])
def put_free_backup():
    global backup_server
    try:
        backup_server = None
        resp = make_response("Backup is free", 200)
    except Exception:
        resp = make_response(f"unable to register", 501)
    return resp


@app.route("/switch_servers", methods=['PUT'])
def switch_servers():
    try:
        global primary_server, backup_server
        primary_server = backup_server
        put_free_backup()
        resp = make_response("server switched", 200)
    except Exception:
        resp = make_response(f"unable to switch", 501)
    return resp


if __name__ == '__main__':
    print(PENDING_COLOR + "to reset connection servers registered server press 'esc'", ERROR_COLOR + "DO NOT USE WHILE COMMUNICATING")
    threading.Thread(target=resetting).start()
    app.run()
