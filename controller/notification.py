from flask_socketio import send, emit
from controller import token_auth
from run import socketio
from flask import g

@socketio.on('my event')
@token_auth.login_required()
def handle_message(message):
    token = g.current_token
    print(message)
    send("abc")
