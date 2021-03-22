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
    applicant.dob = datetime.datetime.strptime(dob, '%d/%m/%Y')

    user.validate = base64.b64encode(os.urandom(24)).decode('utf-8')

    db.user.insert_one(user.__dict__)
    db.applicant.insert(applicant.__dict__, check_keys=False)

    mail_content = "Chào " + name + ",<br>Tài khoản của bạn đã được khởi tạo thành công.<br>Xin vui lòng nhấn vào link bên dưới để hoàn tất việc đăng ký.<br>" + str(user.id()) + "<br>" + user.validate
    html_content = Template(email_form).render(
        {"content": mail_content, "href": "#", "button_text": "Xác nhận tài khoản"})
    yag.send(to=user.email, subject="Xác nhận tài khoản TopTimViec", contents=html_content)


def get_applicant_by_id(id_user, attribute):
    return db.applicant.find_one({"_id": id_user}, attribute)
