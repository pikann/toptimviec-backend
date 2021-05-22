import random
import string
from services import db, email_form
import datetime
from jinja2 import Template
import hashlib
from email.mime.text import MIMEText
from email.header import Header
from util.email import send_email


def send_forget_key(id_user, email):
    forget_key = {"id_user": id_user,
                  "key": ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(30)),
                  "expiration": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)}

    mail_content = "Chào bạn!<br>Đây là link thay đổi mật khẩu:<br>"
    html_content = Template(email_form).render({"content": mail_content,
                                                "href": "http://toptimviec.herokuapp.com/quen-mat-khau/tao-mat-khau-moi?id_user=" + str(
                                                    forget_key["id_user"]) + "&key=" + forget_key["key"],
                                                "button_text": "Đặt lại mật khẩu"})

    msg = MIMEText(html_content, 'html', 'utf-8')
    msg['Subject'] = Header("Link thay đổi mật khẩu TopTimViec", 'utf-8')

    try:
        send_email(email, msg)
    except:
        send_email(email, msg)

    db.forget_key.insert_one(forget_key)


def check_forget_key(id_user, key):
    return db.forget_key.find_one(
        {"id_user": id_user, "key": key, "expiration": {"$gte": datetime.datetime.utcnow()}}) is not None


def reset_password_with_forget_key(id_user, password, key):
    db.user.update_one({"_id": id_user},
                       {"$set": {"password": hashlib.md5(password.encode('utf-8')).hexdigest()}})
    db.forget_key.delete_one({"id_user": id_user, "key": key})
    db.refresh_token.delete_many({"id_user": id_user})
