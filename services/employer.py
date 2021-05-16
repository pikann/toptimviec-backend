import math
import hashlib
import random
import string

from jinja2 import Template

from models.User import User
from models.Employer import Employer
from services import db, email_form, smtp
from email.mime.text import MIMEText
from email.header import Header


def list_employer(name, page):
    employers = list(db.employer.find({"name": {'$regex': name, '$options': 'i'}}, {"name": 1, "avatar": 1, "bio": 1}).sort([("_id", 1)]).skip(page * 8).limit(8))
    for employer in employers:
        employer["_id"] = str(employer["_id"])
        if len(employer["bio"]) > 100:
            employer["bio"] = employer["bio"][:100] + "..."
    return employers


def count_page_list_employer(name):
    return math.ceil(db.employer.find({"name": {'$regex': name, '$options': 'i'}}).count()/8)


def create_employer(email, password, name):
    user = User()
    employer = Employer()
    employer.setID(user.id())
    user.email = email
    user.password = hashlib.md5(password.encode('utf-8')).hexdigest()
    user.role = "employer"
    employer.name = name

    user.validate = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(30))

    mail_content = "Chào " + employer.name + ",<br>Tài khoản của bạn đã được khởi tạo thành công.<br>Xin vui lòng nhấn vào link bên dưới để hoàn tất việc đăng ký."
    html_content = Template(email_form).render(
        {"content": mail_content, "href": "http://toptimviec.herokuapp.com/dang-ky/xac-nhan-email?id=" + str(
            user.id()) + "&key=" + user.validate, "button_text": "Xác nhận tài khoản"})

    msg = MIMEText(html_content, 'html', 'utf-8')
    msg['Subject'] = Header("Xác nhận tài khoản TopTimViec", 'utf-8')

    try:
        smtp.sendmail('toptimviec@gmail.com', user.email, msg.as_string())
    except:
        smtp.sendmail('toptimviec@gmail.com', user.email, msg.as_string())

    db.user.insert_one(user.__dict__)
    db.employer.insert(employer.__dict__, check_keys=False)


def get_employer_by_id(id_user, attribute):
    return db.employer.find_one({"_id": id_user}, attribute)


def update_employer_profile(id_user, name, bio):
    db.employer.update_one(
        {"_id": id_user},
        {"$set": {
            "name": name,
            "bio": bio
        }}
    )


def update_employer_avatar(id_user, avatar):
    db.employer.update_one(
        {"_id": id_user},
        {"$set": {
            "avatar": avatar
        }}
    )
