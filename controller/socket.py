from flask_socketio import SocketIO, join_room
from flask import request
from model import Token

socketio = SocketIO(async_mode='eventlet', cors_allowed_origins="*")


@socketio.on('connect')
def connect():
    token=Token.check_token(request.headers.get('Authorization').split(' ')[1])
    if token is None:
        return
    join_room(str(token.id_user))
