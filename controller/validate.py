from controller import bp, db
from flask import request, abort
from bson.objectid import ObjectId

@bp.route("/validate", methods=['PUT'])
def validate_user():
    rq = request.json
    if not rq or not 'id' in rq or not 'key' in rq:
        abort(400)

    if db.user.find_one({"_id": ObjectId(rq["id"]), "validate": rq["key"]}) is not None:
        db.user.update_one({"_id": ObjectId(rq["id"])}, {"$set": {"validate": ""}})
        return "ok"
    else:
        abort(401)