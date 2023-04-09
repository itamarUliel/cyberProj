from flask import Flask, make_response, request, abort

app = Flask(__name__)

PRIMARY_IP = "127.0.0.1"
PRIMARY_PORT = 5555
SECONDARY_IP = "127.0.0.1"
SECONDARY_PORT = 7890

@app.route("/primary", methods=['GET'])
def get_primary():
    try:
        resp = make_response(f"{PRIMARY_IP}:{PRIMARY_PORT}", 200)
        return resp
    except Exception:
        abort(500)

@app.route("/secondary", methods=['GET'])
def get_secondary():
    try:
        resp = make_response(f"{SECONDARY_IP}:{SECONDARY_PORT}", 200)
        return resp
    except Exception:
        abort(500)

if __name__ == '__main__':
    app.run()