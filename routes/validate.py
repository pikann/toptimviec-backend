from routes import bp
from flask import request, abort
from bson.objectid import ObjectId
from services.user import get_uset_by_validate_key, update_validate

@bp.route("/validate", methods=['PUT'])
def validate_user():
    global user
    rq = request.json
    if not rq or not 'id' in rq or not 'key' in rq:
        abort(400)

    try:
        user=get_uset_by_validate_key(ObjectId(rq["id"]), rq["key"])
    except:
        abort(403)

    if user is not None:
        try:
            update_validate(ObjectId(rq["id"]))
        except:
            abort(403)
        return "ok"
    else:
        return abort(401)
