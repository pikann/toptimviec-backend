from models.User import User
from models.Applicant import Applicant
import hashlib
import datetime
import base64
import os
from services import db, email_form, yag
from jinja2 import Template


def create_applicant(email, password, name, gender, dob):
    user = User()
    applicant = Applicant()
    applicant.setID(user.id())
    user.email = email
    user.password = hashlib.md5(password.encode('utf-8')).hexdigest()
    user.role = "applicant"
    applicant.name = name
    applicant.gender = gender
    applicant.dob = datetime.datetime.strptime(dob, "%Y-%m-%dT%H:%M:%S.%fZ")

    user.validate = base64.b64encode(os.urandom(24)).decode('utf-8')

    db.user.insert_one(user.__dict__)
    db.applicant.insert(applicant.__dict__, check_keys=False)

    mail_content = "Chào " + name + ",<br>Tài khoản của bạn đã được khởi tạo thành công.<br>Xin vui lòng nhấn vào link bên dưới để hoàn tất việc đăng ký."
    html_content = Template(email_form).render(
        {"content": mail_content, "href": "http://toptimviec.herokuapp.com/dang-ky/xac-nhan-email?id=" + str(user.id()) + "&key=" + user.validate, "button_text": "Xác nhận tài khoản"})
    yag.send(to=user.email, subject="Xác nhận tài khoản TopTimViec", contents=html_content)


def get_applicant_by_id(id_user, attribute=None):
    if attribute is None:
        return db.applicant.find_one({"_id": id_user})
    return db.applicant.find_one({"_id": id_user}, attribute)


def update_applicant_profile(id_user, name, gender, dob, place):
    db.applicant.update_one(
        {"_id": id_user},
        {"$set": {
            "name": name,
            "gender": gender,
            "dob": datetime.datetime.strptime(dob, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "place": place
        }}
    )


def update_applicant_avatar(id_user, avatar):
    db.applicant.update_one(
        {"_id": id_user},
        {"$set": {
            "avatar": avatar
        }}
    )
