from flask import g, abort, request
from controller import bp, db, email_form, yag
from controller.auth import token_auth
from bson.objectid import ObjectId
from model import Mail
import threading
from jinja2 import Template


def gmail_has_email(title, content, receiver, attach_post, attach_cv, sender, role_sender):
    global sender_info
    try:
        receiver_emails=list(db.user.find({"_id": {"$in": receiver}}, {"_id":0, "email":1}))
        receiver_emails=[email["email"] for email in receiver_emails]
    except:
        return
    try:
        if role_sender=="employer":
            sender_info=db.employer.find_one({"_id": sender}, {"avatar": 1, "name":1})
        elif role_sender=="applicant":
            sender_info = db.applicant.find_one({"_id": sender}, {"avatar": 1, "name": 1})
        if sender_info["avatar"]=="":
            sender_info["avatar"]="https://res.cloudinary.com/pikann22/image/upload/v1615044354/toptimviec/TCM27Jw1N8ESc1V0Z3gfriuG1NjS_hXXIww7st_jZ0bFz3xGRjKht7JXzfLoU_ZelO4KPiYFPi-ZBVZcR8wdQXYHnwL5SDFYu1Yf7UBT4jhd9d8gj0lCFBA5VbeVp9SveFfJVKRcLON-OyFX_kxrs3f.png"
    except:
        return
    post=None
    if attach_post is not None:
        try:
            post=db.post.find_one({"_id": attach_post}, {"_id":1, "title":1, "place": 1, "salary": 1, "hashtag":1})
        except:
            pass
    cv=None
    if attach_cv is not None:
        try:
            cv=db.cv.find_one({"_id": attach_cv}, {"_id":1, "name":1, "avatar":1, "position":1, "hashtag":1, "place":1})
        except:
            pass

    try:
        mail_content="<table>\
                            <tr><td>\
                                <img src='"+sender_info["avatar"]+"' class='avatar'></td>\
                            <td><div class='employer-name'><strong>"+sender_info["name"]+"</strong></div></td></tr>\
                        </table>\
                        <br>"+content
        html_content = Template(email_form).render({"content": mail_content, "href": "#", "button_text": "Xem chi tiết"})
        yag.send(to=receiver_emails, subject="[TopTimViec]"+title, contents=html_content)
    except:
        return


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
    try:
        db.mail.insert_one(mail.__dict__)
    except:
        abort(403)
    threading.Thread(target=gmail_has_email, args=(mail.title, mail.content, mail.receiver, mail.attach_post, mail.attach_cv, token.id_user, token.role,)).start()
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
        list_mail=list(db.mail.find({"receiver": token.id_user}, {"title": 1}).sort([("_id", -1)]).skip(page*10).limit(10))
    except:
        abort(403)
    rs=[{"_id": str(mail["_id"]), "name": mail["title"]} for mail in list_mail]
    return {"list_mail": rs}


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
        list_mail=list(db.mail.find({"sender": token.id_user}, {"title": 1}).sort([("_id", -1)]).skip(page*10).limit(10))
    except:
        abort(403)
    rs=[{"_id": str(mail["_id"]), "name": mail["title"]} for mail in list_mail]
    return {"list_mail": rs}


@bp.route('/mail/<id>', methods=['GET'])
@token_auth.login_required()
def get_mail(id):
    global mail, sender
    token = g.current_token
    try:
        mail=db.mail.find_one({"_id": ObjectId(id)})
    except:
        abort(403)
    if mail is None:
        abort(404)
    if token.id_user != mail["sender"] and token.id_user not in mail["receiver"]:
        abort(405)
    try:
        rs={"_id": str(mail["_id"]), "title": mail["title"], "content": mail["content"], "attact_post": None, "attach_cv": None}
        sender_role=db.user.find_one({"_id": mail["sender"]}, {"role":1})
        if sender_role["role"]=="applicant":
            sender=db.applicant.find_one({"_id": mail["sender"]}, {"_id":1, "avatar":1, "name":1})
        elif sender_role["role"]=="employer":
            sender = db.employer.find_one({"_id": mail["sender"]}, {"_id": 1, "avatar": 1, "name": 1})
        post = None
        if mail["attach_post"] is not None:
            post = db.post.find_one({"_id": mail["attact_post"]},
                                    {"_id": 1, "title": 1, "place": 1, "salary": 1, "hashtag": 1})
            post["_id"]=str(post["_id"])
            rs["attach_post"]=post
        cv = None
        if mail["attach_cv"] is not None:
            cv = db.cv.find_one({"_id": mail["attach_cv"]},
                                {"_id": 1, "name": 1, "avatar": 1, "position": 1, "hashtag": 1, "place": 1})
            cv["_id"]=str(cv["_id"])
            rs["attach_cv"]=cv
        sender["_id"]=str(sender["_id"])
        rs["sender"]=sender
    except:
        abort(403)
    return rs
