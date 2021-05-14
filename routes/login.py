from flask import g, abort, request
from routes import bp
from services.auth import basic_auth, token_auth
from services.user import get_user_by_id
from services.applicant import get_applicant_by_id
from services.employer import get_employer_by_id
from util.token import encode, revoke_token
from services.refresh_token import get_refresh_token
from models.Token import Token
from bson.objectid import ObjectId
import datetime


@bp.route('/login', methods=['POST'])
@basic_auth.login_required
def login():
    token = g.current_token
    refreshToken = g.refresh_token
    try:
        user = get_user_by_id(token.id_user, {"_id": 0, "role": 1})
        if user["role"] == "applicant":
            applicant = get_applicant_by_id(token.id_user, {"_id": 0, "name": 1, "avatar": 1})
            return {"token": encode(token), "refresh_token": refreshToken.show_key(), "id_user": str(token.id_user), "role": user["role"],
                    "name": applicant["name"], "avatar": applicant["avatar"]}
        if user["role"] == "employer":
            employer = get_employer_by_id(token.id_user, {"_id": 0, "name": 1, "avatar": 1})
            return {"token": encode(token), "refresh_token": refreshToken.show_key(), "id_user": str(token.id_user), "role": user["role"],
                    "name": employer["name"], "avatar": employer["avatar"]}
        if user["role"] == "admin":
            return {"token": encode(token), "refresh_token": refreshToken.show_key(), "id_user": str(token.id_user), "role": user["role"],
                    "name": "Admin", "avatar": "https://res.cloudinary.com/pikann22/image/upload/v1613642165/toptimviec/LogoMakr-87TXng_pnsj0a.png"}
        abort(403)
    except:
        abort(403)


@bp.route('/logout', methods=['DELETE'])
@token_auth.login_required
def logout():
    token = g.current_token
    if revoke_token(token) == "ok":
        return "ok"
    else:
        abort(403)


@bp.route('/token', methods=['GET'])
def get_token():
    refresh_token = request.args.get('refresh-token')
    if not refresh_token:
        abort(400)
    try:
        key=refresh_token.split('.')
        refresh_token=get_refresh_token(ObjectId(key[0]), key[1])
    except:
        abort(403)
    if refresh_token is None or refresh_token["token_expiration"]<datetime.datetime.utcnow():
        abort(401)
    try:
        token=Token(refresh_token["id_user"], refresh_token["role"], refresh_token["_id"])
        return {"token": encode(token)}
    except:
        abort(403)

