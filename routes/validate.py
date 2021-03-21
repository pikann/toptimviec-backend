from routes import bp, db
from flask import request, abort
from bson.objectid import ObjectId

@bp.route("/validate", methods=['PUT'])
def validate_user():
    global user
    rq = request.json
    if not rq or not 'id' in rq or not 'key' in rq:
        abort(400)

    try:
        user=db.user.find_one({"_id": ObjectId(rq["id"]), "validate": rq["key"]})
    except:
        abort(403)

    if user is not None:
        try:
            db.user.update_one({"_id": ObjectId(rq["id"])}, {"$set": {"validate": ""}})
        except:
            abort(403)
        return "ok"
    else:
        return abort(401)
