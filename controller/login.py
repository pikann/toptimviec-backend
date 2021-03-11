from flask import g, abort, request
from controller import bp, db
from controller.auth import basic_auth, token_auth
from model import Token
from bson.objectid import ObjectId
import datetime


@bp.route('/login', methods=['POST'])
@basic_auth.login_required
def login():
    token = g.current_token
    refreshToken = g.refresh_token
    try:
        user = db.user.find_one({"_id": token.id_user}, {"_id": 0, "role": 1})
        if user["role"] == "applicant":
            applicant = db.applicant.find_one({"_id": token.id_user}, {"_id": 0, "name": 1, "avatar": 1})
            return {"token": token.encode(), "refresh_token": refreshToken.show_key(), "id_user": str(token.id_user), "role": user["role"],
                    "name": applicant["name"], "avatar": applicant["avatar"]}
        if user["role"] == "employer":
            employer = db.employer.find_one({"_id": token.id_user}, {"_id": 0, "name": 1, "avatar": 1})
            return {"token": token.encode(), "refresh_token": refreshToken.show_key(), "id_user": str(token.id_user), "role": user["role"],
                    "name": employer["name"], "avatar": employer["avatar"]}
        abort(403)
    except:
        abort(403)


@bp.route('/logout', methods=['DELETE'])
@token_auth.login_required
def logout():
    token = g.current_token
    if token.revoke_token() == "ok":
        return "ok"
    else:
        abort(403)


@bp.route('/info', methods=['GET'])
@token_auth.login_required
def info():
    token = g.current_token
    try:
        if token.role == "applicant":
            applicant = db.applicant.find_one({"_id": token.id_user}, {"_id": 0, "name": 1, "avatar": 1})
            return {"id_user": str(token.id_user), "role": token.role,
                    "name": applicant["name"], "avatar": applicant["avatar"]}
        if token.role == "employer":
            employer = db.employer.find_one({"_id": token.id_user}, {"_id": 0, "name": 1, "avatar": 1})
            return {"id_user": str(token.id_user), "role": token.role,
                    "name": employer["name"], "avatar": employer["avatar"]}
        abort(401)
    except:
        abort(403)


@bp.route('/token', methods=['GET'])
def get_token():
    refresh_token = request.args.get('refresh-token')
    if not refresh_token:
        abort(400)
    try:
        key=refresh_token.split('.')
        refresh_token=db.refresh_token.find_one({"_id": ObjectId(key[0]), "key": key[1]})
    except:
        abort(403)
    if refresh_token is None or refresh_token["token_expiration"]<datetime.datetime.utcnow():
        abort(401)
    try:
        token=Token(refresh_token["id_user"], refresh_token["role"], refresh_token["_id"])
        return {"token": token.encode().decode('utf-8')}
    except:
        abort(403)

