from flask import request, abort
from routes import bp
import re
from bson.objectid import ObjectId
from services.user import check_email
from services.employer import create_employer, get_employer_by_id, list_employer, count_page_list_employer
from services.post import get_post_of_employer


@bp.route("/employer", methods=['GET'])
def get_list_employer():
    global page, name
    try:
        name = str(request.args.get('name', default=""))
        page = int(request.args.get('page', default=0))
    except:
        abort(400)

    try:
        return {"list_employer": list_employer(name, page), "count_page": count_page_list_employer(name)}
    except:
        abort(403)


@bp.route("/employer", methods=['POST'])
def post_employer():
    rq = request.json
    if not rq or not 'email' in rq or not 'password' in rq or not "name" in rq:
        abort(400)

    if rq["email"].__class__ != str or rq["password"].__class__ != str or rq["name"].__class__ != str:
        abort(400)

    if not re.match(r"[-a-zA-Z0-9.`?{}]+@\w+\.\w+", rq["email"]):
        abort(400)

    if not check_email(rq["email"]):
        abort(409)

    try:
        create_employer(rq['email'], rq['password'], rq['name'])
    except:
        abort(400)

    return "ok", 201


@bp.route("/employer/<id>", methods=['GET'])
def get_employer(id):
    global employer
    try:
        employer = get_employer_by_id(ObjectId(id), {"_id": 0, "name": 1, "bio": 1, "avatar": 1})
    except:
        abort(403)
    return employer


@bp.route("/employer/<id>/post", methods=['GET'])
def get_post_employer(id):
    try:
        page = int(request.args.get('page', default=0))
    except:
        abort(400)
    try:
        list_post = get_post_of_employer(ObjectId(id), page)
        return {"list_post": list_post}
    except:
        abort(403)
