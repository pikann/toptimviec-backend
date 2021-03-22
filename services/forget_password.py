from services import db, yag, email_form
import base64
import os
import datetime
from jinja2 import Template
import hashlib


def send_forget_key(id_user, email):
    forget_key = {"id_user": id_user,
                  "key": base64.b64encode(os.urandom(24)).decode('utf-8'),
                  "expiration": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)}
    db.forget_key.insert_one(forget_key)

    mail_content = "Link thay đổi mật khẩu:<br>" + str(forget_key["id_user"]) + "<br>" + forget_key["key"]
    html_content = Template(email_form).render(
        {"content": mail_content, "href": "#", "button_text": "Đặt lại mật khẩu"})

    yag.send(to=email, subject="Link thay đổi mật khẩu TopTimViec", contents=html_content)


def check_forget_key(id_user, key):
    return db.forget_key.find_one({"id_user": id_user, "key": key}) is not None


def reset_password_with_forget_key(id_user, password, key):
    db.user.update_one({"_id": id_user},
                       {"$set": {"password": hashlib.md5(password.encode('utf-8')).hexdigest()}})
    db.forget_key.delete_one({"id_user": id_user, "key": key})
    db.refresh_token.delete_many({"id_user": id_user})
