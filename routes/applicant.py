from flask import request, abort
from routes import bp
from services.applicant import create_applicant
from services.user import check_email
import re


@bp.route("/applicant", methods=['POST'])
def post_applicant():
    rq=request.json
    if not rq or not 'email' in rq or not 'password' in rq or not "name" in rq or not "gender" in rq or not "dob" in rq:
        abort(400)

    if not re.match(r"[-a-zA-Z0-9.`?{}]+@\w+\.\w+", rq["email"]):
        abort(400)

    if not check_email(rq["email"]):
        abort(409)

    try:
        create_applicant(rq['email'], rq['password'], rq['name'], rq['gender'], rq['dob'])
    except:
        abort(403)

    return "ok", 201
