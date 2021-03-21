from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask import abort, g, request
from models.Token import Token
from services.user import check_password
from services.refresh_token import create_refresh_token

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(username, password):
    rq = request.json
    if not rq or not "email" in rq or not "password" in rq:
        abort(400)

    user = check_password(rq["email"], rq["password"])
    if user is None:
        return False
    if user["validate"]!="":
        abort(405)
    refreshToken=create_refresh_token(user["_id"], user["role"])
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
