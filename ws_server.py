import json
from flask import Flask, request

ws_server = Flask(__name__)
from geventwebsocket.websocket import WebSocket
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

user_socket_dict = {}

@ws_server.route('/app/<app_id>')
def app(app_id):
    user_socket = request.environ.get('wsgi.websocket')  # type:WebSocket
    if user_socket:
        user_socket_dict[app_id] = user_socket
    print(len(user_socket_dict), user_socket_dict)

    while 1:
        msg = user_socket.receive()
        if not msg:
            continue
        else:
            msg_dict = json.loads(msg)
            # msg {to_user:toy01,music:学猫叫.mp3}
            to_user = msg_dict.get('to_user')
            to_user_socket = user_socket_dict.get(to_user)
            to_user_socket.send(msg)
            print(msg_dict)


@ws_server.route('/toy/<toy_id>')
def toy(toy_id):
    user_socket = request.environ.get('wsgi.websocket')  # type:WebSocket
    if user_socket:
        user_socket_dict[toy_id] = user_socket
    print(len(user_socket_dict), user_socket_dict)

    while 1:
        msg = user_socket.receive()
        if not msg:
            continue
        else:
            msg_dict = json.loads(msg)
            # {'to_user': to_user, 'from_user': from_user, 'chat': filename}

            to_user = msg_dict.get('to_user')
            to_user_socket = user_socket_dict.get(to_user)
            to_user_socket.send(msg)
            # print(msg_dict)


if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 8080), ws_server, handler_class=WebSocketHandler)
    http_server.serve_forever()
