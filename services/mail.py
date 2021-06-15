import math
import threading
from jinja2 import Template
from routes.socket import socketio
from services import db, email_form
from models.Mail import Mail
from services.notification import notify_mail
from email.mime.text import MIMEText
from email.header import Header
from util.time_format import time_vietnam_format
from util.email import send_email


def gmail_has_email(title, content, receiver, attach_post, attach_cv, sender, role_sender):
    global sender_info
    try:
        receiver_emails = list(db.user.find({"_id": {"$in": receiver}}, {"_id": 0, "email": 1}))
        receiver_emails = [email["email"] for email in receiver_emails]
    except:
        return
    try:
        if role_sender == "employer":
            sender_info = db.employer.find_one({"_id": sender}, {"avatar": 1, "name": 1})
        elif role_sender == "applicant":
            sender_info = db.applicant.find_one({"_id": sender}, {"avatar": 1, "name": 1})
        if sender_info["avatar"] == "":
            sender_info[
                "avatar"] = "https://res.cloudinary.com/pikann22/image/upload/v1615044354/toptimviec/TCM27Jw1N8ESc1V0Z3gfriuG1NjS_hXXIww7st_jZ0bFz3xGRjKht7JXzfLoU_ZelO4KPiYFPi-ZBVZcR8wdQXYHnwL5SDFYu1Yf7UBT4jhd9d8gj0lCFBA5VbeVp9SveFfJVKRcLON-OyFX_kxrs3f.png"
    except:
        return
    post = None
    if attach_post is not None:
        try:
            post = db.post.find_one({"_id": attach_post}, {"_id": 1, "title": 1, "place": 1, "salary": 1, "hashtag": 1})
        except:
            pass
    cv = None
    if attach_cv is not None:
        try:
            cv = db.cv.find_one({"_id": attach_cv},
                                {"_id": 1, "name": 1, "avatar": 1, "position": 1, "hashtag": 1, "place": 1})
        except:
            pass

    try:
        mail_content = "<table>\
                            <tr><td>\
                                <img src='" + sender_info["avatar"] + "' class='avatar'></td>\
                            <td><div class='employer-name'><strong>" + sender_info["name"] + "</strong></div></td></tr>\
                        </table>\
                        <br>" + content
        html_content = Template(email_form).render(
            {"content": mail_content, "href": "#", "button_text": "Xem chi tiết"})

        msg = MIMEText(html_content, 'html', 'utf-8')
        msg['Subject'] = Header("[TopTimViec]" + title, 'utf-8')

        try:
            send_email(receiver_emails, msg)
        except:
            send_email(receiver_emails, msg)
    except:
        return


def add_mail(id_user, receiver, title, content, attach_post, attach_cv, role):
    mail = Mail(sender=id_user, receiver=receiver, title=title, content=content, attach_post=attach_post,
                attach_cv=attach_cv)
    db.mail.insert_one(mail.__dict__)
    threading.Thread(target=gmail_has_email, args=(
    mail.title, mail.content, mail.receiver, mail.attach_post, mail.attach_cv, id_user, role,)).start()

    socketio.start_background_task(target=notify_mail(id_user, role, receiver, mail.title, mail.id()))


def get_my_list_mail(id_user, page):
    return list(db.mail.find({"receiver": id_user}, {"title": 1, "sent_date": 1, "read": 1}).sort([("_id", -1)]).skip(
        page * 10).limit(10))


def count_page_my_list_mail(id_user):
    return math.ceil(db.mail.find({"receiver": id_user}).count() / 10)


def get_my_list_mail_send(id_user, page):
    return list(
        db.mail.find({"sender": id_user}, {"title": 1, "sent_date": 1}).sort([("_id", -1)]).skip(page * 10).limit(10))


def count_page_my_list_mail_send(id_user):
    return math.ceil(db.mail.find({"sender": id_user}).count() / 10)


def find_mail(id_mail):
    request = [
        {"$match": {"_id": id_mail}},
        {"$lookup": {
            "from": "user",
            "localField": "sender",
            "foreignField": "_id",
            "as": "sender"
        }},
        {"$unwind": "$sender"},
        {"$lookup": {
            "from": "applicant",
            "localField": "sender._id",
            "foreignField": "_id",
            "as": "sender.applicant"
        }},
        {"$lookup": {
            "from": "employer",
            "localField": "sender._id",
            "foreignField": "_id",
            "as": "sender.employer"
        }},
        {"$unwind": {
            "path": "$sender.applicant",
            "preserveNullAndEmptyArrays": True
        }},
        {"$unwind": {
            "path": "$sender.employer",
            "preserveNullAndEmptyArrays": True
        }},

        {"$unwind": "$receiver"},
        {"$set": {"receiver._id": "$receiver"}},
        {"$lookup": {
            "from": "applicant",
            "localField": "receiver._id",
            "foreignField": "_id",
            "as": "receiver.applicant"
        }},
        {"$lookup": {
            "from": "employer",
            "localField": "receiver._id",
            "foreignField": "_id",
            "as": "receiver.employer"
        }},
        {"$unwind": {
            "path": "$receiver.applicant",
            "preserveNullAndEmptyArrays": True
        }},
        {"$unwind": {
            "path": "$receiver.employer",
            "preserveNullAndEmptyArrays": True
        }},

        {"$lookup": {
            "from": "cv",
            "localField": "attach_cv",
            "foreignField": "_id",
            "as": "attach_cv"
        }},
        {"$lookup": {
            "from": "post",
            "localField": "attach_post",
            "foreignField": "_id",
            "as": "attach_post"
        }},
        {"$unwind": {
            "path": "$attach_cv",
            "preserveNullAndEmptyArrays": True
        }},
        {"$unwind": {
            "path": "$attach_post",
            "preserveNullAndEmptyArrays": True
        }},
        {"$lookup": {
            "from": "employer",
            "localField": "attach_post.employer",
            "foreignField": "_id",
            "as": "attach_post.employer"
        }},
        {"$unwind": {
            "path": "$attach_post.employer",
            "preserveNullAndEmptyArrays": True
        }},
        {"$project": {
            "attach_cv._id": {"$toString": "$attach_cv._id"},
            "attach_cv.name": 1,
            "attach_cv.avatar": 1,
            "attach_cv.position": 1,
            "attach_cv.hashtag": 1,
            "attach_cv.place": 1,
            "attach_post._id": {"$toString": "$attach_post._id"},
            "attach_post.title": 1,
            "attach_post.place": 1,
            "attach_post.hashtag": 1,
            "attach_post.salary": 1,
            "attach_post.employer._id": {"$toString": "$attach_post.employer._id"},
            "attach_post.employer.name": 1,
            "attach_post.employer.avatar": 1,
            "_id": {"$toString": "$_id"},
            "title": 1,
            "content": 1,
            "sent_date": 1,
            "sender.applicant._id": 1,
            "sender.applicant.name": 1,
            "sender.applicant.avatar": 1,
            "sender.employer._id": 1,
            "sender.employer.name": 1,
            "sender.employer.avatar": 1,
            "receiver.applicant._id": 1,
            "receiver.applicant.name": 1,
            "receiver.employer._id": 1,
            "receiver.employer.name": 1,
        }},
        {"$group": {
            "_id": {"$toString": "$_id"},
            "title": {"$first": "$title"},
            "content": {"$first": "$content"},
            "attach_cv": {"$first": "$attach_cv"},
            "attach_post": {"$first": "$attach_post"},
            "sent_date": {"$first": "$sent_date"},
            "sender": {"$first": '$sender'},
            "receiver": {"$addToSet": '$receiver'}
        }}
    ]
    return list(db.mail.aggregate(request))


def get_mail_info(mail):
    mail["sent_date"] = time_vietnam_format(mail["sent_date"])

    if "applicant" in mail["sender"]:
        mail["sender"] = mail["sender"]["applicant"]
        mail["sender"]["role"] = "applicant"
    elif "employer" in mail["sender"]:
        mail["sender"] = mail["sender"]["employer"]
        mail["sender"]["role"] = "employer"
    else:
        return None

    mail["sender"]["_id"] = str(mail["sender"]["_id"])

    receivers = []

    for receiver in mail["receiver"]:
        if "applicant" in receiver:
            receiver = receiver["applicant"]
            receiver["role"] = "applicant"
        elif "employer" in receiver:
            receiver = receiver["employer"]
            receiver["role"] = "employer"
        else:
            continue
        receiver["_id"] = str(receiver["_id"])
        receivers.append(receiver)

    mail["receiver"] = receivers

    if mail["attach_post"]["_id"] is None:
        mail["attach_post"] = None
    if mail["attach_cv"]["_id"] is None:
        mail["attach_cv"] = None

    return mail


def check_mail_readable(id_user, mail):
    if str(id_user) == mail["sender"]["_id"]:
        return True

    for receiver in mail["receiver"]:
        if str(id_user) == receiver["_id"]:
            return True

    return False


def set_read_mail(id_user, id_mail):
    db.mail.update_one({"_id": id_mail}, {"$push": {"read": id_user}})
