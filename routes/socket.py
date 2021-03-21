from flask_socketio import SocketIO, join_room
from flask import request
from models.Token import Token

socketio = SocketIO(async_mode='eventlet', cors_allowed_origins="*", pingInterval=30000, pingTimeout=30000)


@socketio.on('connect')
def connect():
    token=Token.check_token(request.headers.get('Authorization').split(' ')[1])
    if token is None:
        return
    print(str(token.id_user))
    join_room(str(token.id_user))
