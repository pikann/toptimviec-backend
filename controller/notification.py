from flask_socketio import send, emit
from controller import token_auth
from run import socketio
from flask import g

@socketio.on('message')
def test_connect(message):
    print(message)
