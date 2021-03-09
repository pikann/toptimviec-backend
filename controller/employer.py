import base64
import os

from flask import request, abort
from model import User, Employer
import hashlib
from controller import bp, db, yag, email_form
from jinja2 import Template
import datetime
import re
from bson.objectid import ObjectId


@bp.route("/employer", methods=['POST'])
def post_employer():
    rq = request.json
    if not rq or not 'email' in rq or not 'password' in rq or not "name" in rq:
        abort(400)

    if not re.match(r"[-a-zA-Z0-9.`?{}]+@\w+\.\w+", rq["email"]):
        abort(400)

    if db.user.find_one({"email": rq["email"]}) is not None:
        abort(409)

    try:
        user = User()
        employer = Employer()
        employer.setID(user.id())
        user.email = rq['email']
        user.password = hashlib.md5(rq['password'].encode('utf-8')).hexdigest()
        user.role = "employer"
        employer.name = rq['name']

        user.validate = base64.b64encode(os.urandom(24)).decode('utf-8')

        db.user.insert_one(user.__dict__)
        db.employer.insert(employer.__dict__, check_keys=False)

        mail_content = "Chào " + employer.name + ",<br>Tài khoản của bạn đã được khởi tạo thành công.<br>Xin vui lòng nhấn vào link bên dưới để hoàn tất việc đăng ký.<br>" + str(
            user.id()) + "<br>" + user.validate
        html_content = Template(email_form).render({"content": mail_content, "href": "#", "button_text": "Xác nhận tài khoản"})
        yag.send(to=user.email, subject="Xác nhận tài khoản TopTimViec", contents=html_content)
    except:
        abort(400)

    return "ok", 201


@bp.route("/employer/<id>", methods=['GET'])
def get_employer(id):
    try:
        employer = db.employer.find_one({"_id": ObjectId(id)}, {"_id": 0, "name": 1, "bio": 1, "avatar": 1})
    except:
        abort(403)
    return employer


@bp.route("/employer/<id>/post", methods=['GET'])
def get_post_employer(id):
    rq = request.json
    if not rq or not 'list_id_showed' in rq:
        abort(400)
    try:
        list_showed = [ObjectId(id_seen) for id_seen in rq["list_id_showed"]]
        list_post = list(db.post.aggregate([{"$match": {"_id": {"$not": {"$in": list_showed}}}},
                                            {"$match": {"employer": ObjectId(id)}},
                                            {"$sort": {"_id": -1}},
                                            {"$limit": 20},
                                            {"$project": {
                                                "_id": {"$toString": "$_id"},
                                                "title": 1,
                                                "employer": 1,
                                                "place": 1,
                                                "hashtag": 1,
                                                "salary": 1
                                            }},
                                            {"$lookup": {
                                                "from": "employer",
                                                "localField": "employer",
                                                "foreignField": "_id",
                                                "as": "employer"
                                            }},
                                            {"$unwind": "$employer"},
                                            {"$project": {
                                                "employer.bio": 0,
                                                "employer.url": 0
                                            }},
                                            {"$set": {
                                                "employer._id": {"$toString": "$employer._id"}
                                            }}]))
        return {"list_post": list_post}
    except:
        abort(403)
