import base64
import os

from flask import request, abort
import hashlib
from controller import bp, db, yag
import datetime
from bson.objectid import ObjectId

@bp.route("/forget-password", methods=['POST'])
def forget_password():
    rq = request.json
    if not rq or not 'email' in rq:
        abort(400)
    try:
        user=db.user.find_one({"email": rq["email"]})
    except:
        abort(403)
    if user is None:
        abort(401)
    try:
        forget_key={"id_user": user["_id"],
                    "key": base64.b64encode(os.urandom(24)).decode('utf-8'),
                    "expiration": datetime.datetime.utcnow()+datetime.timedelta(seconds=3600)}
        db.forget_key.insert_one(forget_key)

        mail_content = "Link thay đổi mật khẩu:\n" + str(forget_key["id_user"]) + "\n" + forget_key["key"]

        yag.send(to=rq["email"], subject="Link thay đổi mật khẩu TopTimViec", contents=mail_content)

        return "ok"
    except:
        abort(403)

@bp.route("/reset-password-forget", methods=['PUT'])
def reset_password_forget():
    rq = request.json
    if not rq or not 'id_user' in rq or not 'key' in rq or not 'password' in rq:
        abort(400)

    if db.forget_key.find_one({"id_user": ObjectId(rq["id_user"]), "key": rq["key"]}) is not None:
        try:
            db.user.update_one({"_id": ObjectId(rq["id_user"])}, {"$set": {"password": hashlib.md5(rq['password'].encode('utf-8')).hexdigest()}})
            db.forget_key.delete_one({"id_user": ObjectId(rq["id_user"]), "key": rq["key"]})
        except:
            abort(403)
        return "ok"
    else:
        abort(401)