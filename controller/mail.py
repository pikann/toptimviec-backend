from flask import g, abort, request
from controller import bp, db
from controller.auth import token_auth
from bson.objectid import ObjectId
from model import Mail
import threading


@bp.route('/mail', methods=['POST'])
@token_auth.login_required()
def send_mail():
    token = g.current_token
    rq = request.json
    if not rq or not 'title' in rq or not 'content' in rq or not 'receiver' in rq:
        abort(400)
    if rq["receiver"].__class__ != list or rq["title"].__class__ != str or rq["content"].__class__ != str:
        abort(400)
    receiver=[ObjectId(i) for i in rq["receiver"]]
    mail=Mail(token.id_user, receiver, rq["title"], rq["content"])
    db.mail.insert_one(mail.__dict__)
