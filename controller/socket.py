from flask_socketio import SocketIO, join_room
from flask import request
from model import Token

socketio = SocketIO(async_mode='eventlet', cors_allowed_origins="*", engineio_logger=True)


@socketio.on('connect')
def connect():
    token=Token.check_token(request.headers.get('Authorization').split(' ')[1])
    if token is None:
        return
    print(str(token.id_user))
    join_room(str(token.id_user))
