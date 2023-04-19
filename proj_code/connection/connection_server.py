from flask import Flask, make_response, request, abort

app = Flask(__name__)

PRIMARY_IP = "127.0.0.1"
PRIMARY_PORT = 5555
SECONDARY_IP = "127.0.0.1"
SECONDARY_PORT = 7890

DEFAULT_PRIMARY = f"{PRIMARY_IP}:{PRIMARY_PORT}"

chat_server = None


@app.route("/chat_server", methods=['GET'])
def get_chat_server():
    try:
        global chat_server
        if chat_server is not None:
            resp = make_response(f"{str(chat_server)}", 200)
        elif DEFAULT_PRIMARY is not None:
            resp = make_response(DEFAULT_PRIMARY, 200)
        else:
            resp = make_response("Chat server not available", 503)
        return resp
    except Exception:
        abort(500)


@app.route("/primary", methods=['GET'])
def get_primary():
    try:
        return get_chat_server()
    except Exception:
        abort(500)


@app.route("/secondary", methods=['GET'])
def get_secondary():
    try:
        resp = make_response(f"{SECONDARY_IP}:{SECONDARY_PORT}", 200)
        return resp
    except Exception:
        abort(500)



@app.route("/primary", methods=['PUT'])
def put_primary():
    try:
        global chat_server
        server_address = request.data.decode().split(":")
        chat_server = f"{server_address[0]}:{server_address[1]}"
        resp = make_response(f"Primary updated {chat_server}", 200)
    except Exception:
        resp = make_response(f"Invalid server details", 400)
    return resp


if __name__ == '__main__':
    app.run()
