from flask import g, abort, request
from routes import bp
from services.auth import token_auth
from services.mail import add_mail, get_my_list_mail, get_my_list_mail_send, find_mail, get_mail_info, \
    count_page_my_list_mail_send, count_page_my_list_mail, set_read_mail, check_mail_readable
from bson.objectid import ObjectId
from util.time_format import time_vietnam_format


@bp.route('/mail', methods=['POST'])
@token_auth.login_required()
def send_mail():
    token = g.current_token
    rq = request.json
    if not rq or not 'title' in rq or not 'content' in rq or not 'receiver' in rq or not 'attach_post' in rq or not 'attach_cv' in rq:
        abort(400)
    if rq["receiver"].__class__ != list or rq["title"].__class__ != str or rq["content"].__class__ != str or rq[
        "attach_post"].__class__ != str or rq["attach_cv"].__class__ != str:
        abort(400)
    receiver = [ObjectId(i) for i in rq["receiver"]]
    if rq["attach_post"] != "":
        attach_post = ObjectId(rq["attach_post"])
    else:
        attach_post = None
    if rq["attach_cv"] != "":
        attach_cv = ObjectId(rq["attach_cv"])
    else:
        attach_cv = None

    try:
        add_mail(token.id_user, receiver, rq["title"], rq["content"], attach_post, attach_cv, token.role)
    except:
        abort(403)

    return "ok"


@bp.route('/mail', methods=['GET'])
@token_auth.login_required()
def get_list_mail():
    global list_mail, page
    token = g.current_token
    try:
        page = int(request.args.get('page', default=0))
    except:
        abort(400)
    try:
        list_mail = get_my_list_mail(token.id_user, page)
    except:
        abort(403)
    rs = [{"_id": str(mail["_id"]), "name": mail["title"], "sent_date": time_vietnam_format(mail["sent_date"]),
           "read": token.id_user in mail["read"]} for mail in list_mail]
    return {"list_mail": rs}


@bp.route('/mail/page', methods=['GET'])
@token_auth.login_required()
def get_number_of_list_mail():
    token = g.current_token
    try:
        return {"count_page": count_page_my_list_mail(token.id_user)}
    except:
        abort(403)


@bp.route('/mail/send', methods=['GET'])
@token_auth.login_required()
def get_list_mail_send():
    global list_mail, page
    token = g.current_token
    try:
        page = int(request.args.get('page', default=0))
    except:
        abort(400)
    try:
        list_mail = get_my_list_mail_send(token.id_user, page)
    except:
        abort(403)
    rs = [{"_id": str(mail["_id"]), "name": mail["title"], "sent_date": time_vietnam_format(mail["sent_date"])} for
          mail in list_mail]
    return {"list_mail": rs}


@bp.route('/mail/send/page', methods=['GET'])
@token_auth.login_required()
def get_number_of_list_mail_send():
    token = g.current_token
    try:
        return {"count_page": count_page_my_list_mail_send(token.id_user)}
    except:
        abort(403)


@bp.route('/mail/<id>', methods=['GET'])
@token_auth.login_required()
def get_mail(id):
    global mail, sender, rs, able
    token = g.current_token

    try:
        mail = find_mail(ObjectId(id))
    except:
        abort(403)

    if len(mail) == 0:
        abort(404)

    try:
        mail = get_mail_info(mail[0])
    except:
        abort(403)

    if mail is None:
        abort(404)

    try:
        able = check_mail_readable(token.id_user, mail)
    except:
        abort(405)

    if not able:
        abort(405)

    try:
        set_read_mail(token.id_user, ObjectId(id))
    except:
        abort(403)
    return mail
