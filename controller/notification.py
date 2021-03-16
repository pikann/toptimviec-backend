from bson import ObjectId
from flask import request, abort, g
from controller import bp, db
from controller.auth import token_auth


@bp.route('/notification', methods=['GET'])
@token_auth.login_required()
def get_list_notify():
    token = g.current_token
    rq = request.json
    if not rq or not 'list_id_showed' in rq:
        abort(400)
    if rq["list_id_showed"].__class__ != list:
        abort(400)
    try:
        list_showed = [ObjectId(s) for s in rq["list_id_showed"]]
    except:
        abort(400)
    try:
        list_notify = list(db.notification.find({"user": token.id_user, "_id": {"$not": {"$in": list_showed}}}, {"user": 0}).sort([("_id", -1)]).limit(10))
        for notify in list_notify:
            notify["id_attach"] = str(notify["id_attach"])
            notify["_id"] = str(notify["_id"])
        return {"list_notify": list_notify}
    except:
        abort(403)