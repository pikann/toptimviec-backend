from flask import request, abort
from routes import bp
from services.auth import token_auth
from services.admin import count_user, count_cv, count_post, count_post_unexpired, count_employer, count_applicant
from services.employer import list_employer_admin
from services.post import get_post_admin, count_get_post_admin
from services.global_data import check_place, check_list_hashtag


@bp.route('/general-info', methods=['GET'])
@token_auth.login_required(role="admin")
def get_general_infomation():
    global rs
    try:
        rs = {
            "count_user": count_user(),
            "count_cv": count_cv(),
            "count_post": count_post(),
            "count_post_unexpired": count_post_unexpired(),
            "count_employer": count_employer(),
            "count_applicant": count_applicant()
        }
    except:
        abort(403)

    return rs


@bp.route('/admin/employer', methods=['GET'])
@token_auth.login_required(role="admin")
def get_list_employer_admin():
    global page, name
    try:
        name = str(request.args.get('name', default=""))
        page = int(request.args.get('page', default=0))
    except:
        abort(400)

    try:
        return {"list_employer": list_employer_admin(name, page)}
    except:
        abort(403)


@bp.route('/admin/post', methods=['GET'])
@token_auth.login_required(role="admin")
def get_list_post_admin():
    global page, name, list_hashtag, place
    try:
        title = str(request.args.get('title', default=""))
        page = int(request.args.get('page', default=0))
        list_hashtag = check_list_hashtag(str(request.args.get('list_hashtag', default="")).split(","))
        place = check_place(str(request.args.get('place', default="")))
    except:
        abort(400)

    try:
        return {"list_post": get_post_admin(title, page, list_hashtag, place)}
    except:
        abort(403)


@bp.route('/admin/post/count', methods=['GET'])
@token_auth.login_required(role="admin")
def count_get_list_post_admin():
    global title, list_hashtag, place
    try:
        title = str(request.args.get('title', default=""))
        list_hashtag = check_list_hashtag(str(request.args.get('list_hashtag', default="")).split(","))
        place = check_place(str(request.args.get('place', default="")))
    except:
        abort(400)

    try:
        return {"count_post": count_get_post_admin(title, list_hashtag, place)}
    except:
        abort(403)
