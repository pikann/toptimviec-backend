from bson import ObjectId
from flask_socketio import SocketIO, join_room
from flask import request

from services.refresh_token import get_refresh_token

socketio = SocketIO(async_mode='eventlet', cors_allowed_origins="*", pingInterval=30000, pingTimeout=30000)


@socketio.on('connect')
def connect():
    key = request.headers.get('Authorization').split(' ')[1].split('.')
    try:
        token = get_refresh_token(ObjectId(key[0]), key[1])
        if token is None:
            return
        join_room(str(token["id_user"]))
    except:
        return
