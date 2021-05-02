from models.User import User
from models.Employer import Employer
import hashlib
import base64
import os
from services import db, email_form, yag
from jinja2 import Template


def create_employer(email, password, name):
    user = User()
    employer = Employer()
    employer.setID(user.id())
    user.email = email
    user.password = hashlib.md5(password.encode('utf-8')).hexdigest()
    user.role = "employer"
    employer.name = name

    user.validate = base64.b64encode(os.urandom(24)).decode('utf-8')

    db.user.insert_one(user.__dict__)
    db.employer.insert(employer.__dict__, check_keys=False)

    mail_content = "Chào " + employer.name + ",<br>Tài khoản của bạn đã được khởi tạo thành công.<br>Xin vui lòng nhấn vào link bên dưới để hoàn tất việc đăng ký."
    html_content = Template(email_form).render(
        {"content": mail_content, "href": "http://toptimviec.herokuapp.com/dang-ky/xac-nhan-email?id=" + str(user.id()) + "&key=" + user.validate, "button_text": "Xác nhận tài khoản"})
    yag.send(to=user.email, subject="Xác nhận tài khoản TopTimViec", contents=html_content)


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
