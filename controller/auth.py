from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask import abort, g, request
import hashlib
from controller import db
from model import Token

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(username, password):
    rq = request.json
    if not rq or not "email" in rq or not "password" in rq:
        abort(400)

    email = rq["email"]
    password = rq["password"]

    user = db.user.find_one({"email": email, "password": hashlib.md5(password.encode('utf-8')).hexdigest()})
    if user is None:
        return False
    if user["validate"]!="":
        abort(405)
    g.current_token = Token(user['_id'])
    return True


@basic_auth.error_handler
def basic_auth_error():
    return abort(401)


@token_auth.verify_token
def verify_token(id_token):
    g.current_token = Token.check_token(id_token) if id_token else None
    return g.current_token is not None


@token_auth.error_handler
def token_auth_error():
    return abort(401)


@token_auth.get_user_roles
def get_user_roles(user):
    token = g.current_token.get_token()
    return db.user.find_one({"_id": token.id_user}, {"_id": 0, "role": 1})["role"]