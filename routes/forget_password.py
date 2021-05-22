from flask import request, abort
from routes import bp
from bson.objectid import ObjectId
from services.user import get_user_by_email
from services.forget_password import send_forget_key, check_forget_key, reset_password_with_forget_key


@bp.route("/forget-password", methods=['POST'])
def forget_password():
    global user
    rq = request.json
    if not rq or not 'email' in rq:
        abort(400)
    try:
        user = get_user_by_email(rq["email"], {"_id": 1})
    except:
        abort(403)
    if user is None:
        abort(401)
    try:
        send_forget_key(user["_id"], rq["email"])
        return "ok"
    except:
        abort(403)


@bp.route("/reset-password-forget", methods=['PUT'])
def reset_password_forget():
    global is_able
    rq = request.json
    if not rq or not 'id_user' in rq or not 'key' in rq or not 'password' in rq:
        abort(400)

    try:
        is_able = check_forget_key(ObjectId(rq["id_user"]), rq["key"])
    except:
        abort(403)

    if is_able:
        try:
            reset_password_with_forget_key(ObjectId(rq["id_user"]), rq['password'], rq["key"])
        except:
            abort(403)
        return "ok"
    else:
        abort(401)
