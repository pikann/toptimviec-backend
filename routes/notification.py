from bson import ObjectId
from flask import request, abort, g
from routes import bp
from services.auth import token_auth
from services.notification import get_list_notification


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
        list_notify = get_list_notification(token.id_user, list_showed)
        return {"list_notify": list_notify}
    except:
        abort(403)