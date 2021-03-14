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
    if not rq or not 'title' in rq or not 'content' in rq or not 'receiver' in rq or not 'attach_post' in rq or not 'attach_cv' in rq:
        abort(400)
    if rq["receiver"].__class__ != list or rq["title"].__class__ != str or rq["content"].__class__ != str or rq["attach_post"].__class__ != str or rq["attach_cv"].__class__ != str:
        abort(400)
    receiver=[ObjectId(i) for i in rq["receiver"]]
    if rq["attach_post"]!="":
        attach_post=ObjectId(rq["attach_post"])
    else:
        attach_post=None
    if rq["attach_cv"]!="":
        attach_cv=ObjectId(rq["attach_cv"])
    else:
        attach_cv=None
    mail=Mail(sender=token.id_user, receiver=receiver, title=rq["title"], content=rq["content"], attach_post=attach_post, attach_cv=attach_cv)
    db.mail.insert_one(mail.__dict__)
    return "ok"