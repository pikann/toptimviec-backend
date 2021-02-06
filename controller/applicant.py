import base64
import os

from flask import request, abort
from model import User, Applicant
import hashlib
from controller import bp, db, yag
import datetime

@bp.route("/applicant", methods=['POST'])
def post_applicant():
    rq=request.json
    if not rq or not 'email' in rq or not 'password' in rq or not "name" in rq or not "gender" in rq or not "dob" in rq:
        abort(400)

    if db.user.find_one({"email": rq["email"]}) is not None:
        abort(409)

    try:
        user=User()
        applicant=Applicant()
        applicant.setID(user.id())
        user.email=rq['email']
        user.password=hashlib.md5(rq['password'].encode('utf-8')).hexdigest()
        user.role="applicant"
        applicant.name=rq['name']
        applicant.gender=rq['gender']
        applicant.dob=datetime.datetime.strptime(rq['dob'], '%d/%m/%Y')

        user.validate=base64.b64encode(os.urandom(24)).decode('utf-8')

        db.user.insert_one(user.__dict__)
        db.applicant.insert_one(applicant.__dict__)

        mail_content="Chào "+applicant.name+",\nTài khoản của bạn đã được khởi tạo thành công.\nXin vui lòng nhấn vào link bên dưới để hoàn tất việc đăng ký.\n"+str(user.id())+"\n"+user.validate

        yag.send(to=user.email, subject="Xác nhận tài khoản TopTimViec", contents=mail_content)
    except:
        abort(403)

    return "ok", 201
