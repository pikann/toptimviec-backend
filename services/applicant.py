import random
import string
from models.User import User
from models.Applicant import Applicant
import hashlib
import datetime
from services import db, email_form
from jinja2 import Template
from email.mime.text import MIMEText
from email.header import Header
from util.email import send_email


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

    user.validate = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(30))

    mail_content = "Chào " + name + ",<br>Tài khoản của bạn đã được khởi tạo thành công.<br>Xin vui lòng nhấn vào link bên dưới để hoàn tất việc đăng ký."
    html_content = Template(email_form).render(
        {"content": mail_content, "href": "http://toptimviec.herokuapp.com/dang-ky/xac-nhan-email?id=" + str(
            user.id()) + "&key=" + user.validate, "button_text": "Xác nhận tài khoản"})

    msg = MIMEText(html_content, 'html', 'utf-8')
    msg['Subject'] = Header("Xác nhận tài khoản TopTimViec", 'utf-8')

    try:
        send_email(user.email, msg)
    except:
        send_email(user.email, msg)

    db.user.insert_one(user.__dict__)
    db.applicant.insert(applicant.__dict__, check_keys=False)


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
