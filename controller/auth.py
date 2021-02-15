from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask import abort, g, request
import hashlib
from controller import db
from model import Token, RefreshToken

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
    refreshToken=RefreshToken(user["_id"], user["role"])
    db.refresh_token.insert_one(refreshToken.__dict__)
    g.refresh_token = refreshToken
    g.current_token = Token(refreshToken.id_user, refreshToken.role, refreshToken.id())
    return True


@basic_auth.error_handler
def basic_auth_error():
    return abort(401)


@token_auth.verify_token
def verify_token(key):
    g.current_token = Token.check_token(key) if key else None
    return g.current_token is not None


@token_auth.error_handler
def token_auth_error():
    return abort(401)


@token_auth.get_user_roles
def get_user_roles(user):
    token = g.current_token
    return token.role
