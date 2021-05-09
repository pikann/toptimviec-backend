import math
import threading
from jinja2 import Template
from routes.socket import socketio
from services import db, email_form, smtp
from models.Mail import Mail
from services.notification import notify_mail
from email.mime.text import MIMEText
from email.header import Header


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

        msg = MIMEText(html_content, 'html', 'utf-8')
        msg['Subject'] = Header("[TopTimViec]"+title, 'utf-8')

        try:
            smtp.sendmail('toptimviec@gmail.com', receiver_emails, msg.as_string())
        except:
            smtp.sendmail('toptimviec@gmail.com', receiver_emails, msg.as_string())
    except:
        return


def add_mail(id_user, receiver, title, content, attach_post, attach_cv, role):
    mail = Mail(sender=id_user, receiver=receiver, title=title, content=content, attach_post=attach_post, attach_cv=attach_cv)
    db.mail.insert_one(mail.__dict__)
    threading.Thread(target=gmail_has_email, args=(mail.title, mail.content, mail.receiver, mail.attach_post, mail.attach_cv, id_user, role,)).start()

    socketio.start_background_task(target=notify_mail(id_user, role, receiver, mail.title, mail.id()))


def get_my_list_mail(id_user, page):
    return list(db.mail.find({"receiver": id_user}, {"title": 1, "sent_date": 1, "read": 1}).sort([("_id", -1)]).skip(page*10).limit(10))


def count_page_my_list_mail(id_user):
    return math.ceil(db.mail.find({"receiver": id_user}).count()/10)


def get_my_list_mail_send(id_user, page):
    return list(db.mail.find({"sender": id_user}, {"title": 1, "sent_date": 1}).sort([("_id", -1)]).skip(page*10).limit(10))


def count_page_my_list_mail_send(id_user):
    return math.ceil(db.mail.find({"sender": id_user}).count()/10)


def find_mail(id_mail):
    return db.mail.find_one({"_id": id_mail})


def get_mail_info(mail):
    rs = {"_id": str(mail["_id"]), "title": mail["title"], "content": mail["content"], "sent_date": mail["sent_date"], "attact_post": None,
          "attach_cv": None}
    sender_role = db.user.find_one({"_id": mail["sender"]}, {"role": 1})
    if sender_role["role"] == "applicant":
        sender = db.applicant.find_one({"_id": mail["sender"]}, {"_id": 1, "avatar": 1, "name": 1})
    elif sender_role["role"] == "employer":
        sender = db.employer.find_one({"_id": mail["sender"]}, {"_id": 1, "avatar": 1, "name": 1})
    post = None
    if mail["attach_post"] is not None:
        post = db.post.find_one({"_id": mail["attact_post"]},
                                {"_id": 1, "title": 1, "place": 1, "salary": 1, "hashtag": 1})
        post["_id"] = str(post["_id"])
        rs["attach_post"] = post
    cv = None
    if mail["attach_cv"] is not None:
        cv = db.cv.find_one({"_id": mail["attach_cv"]},
                            {"_id": 1, "name": 1, "avatar": 1, "position": 1, "hashtag": 1, "place": 1})
        cv["_id"] = str(cv["_id"])
        rs["attach_cv"] = cv
    sender["_id"] = str(sender["_id"])
    rs["sender"] = sender
    return rs


def set_read_mail(id_user, id_mail):
    db.mail.update_one({"_id": id_mail}, {"$push": {"read": id_user}})
