from flask import g, abort, request, make_response
from routes import bp
from services.auth import token_auth
from bson.objectid import ObjectId
import datetime
import threading
from services.learn import learn_employer_hashtag, learn_applicant_hashtag
from services.global_data import check_place, check_list_hashtag, check_list_place
from services.post import recommend_post, search_post, get_all_post, get_post_info, new_post, find_post, update_post, delete_post_by_id, get_post_of_employer, count_page_my_list_post
from services.list_candidate import create_candidate_list_for_post


@bp.route('/post-list', methods=['POST'])
@token_auth.login_required(optional=True)
def get_list_post():
    global hashtag, list_showed, place, list_post
    rq = request.json
    if not rq or not 'list_id_showed' in rq or not 'list_hashtag' in rq or not 'place' in rq:
        abort(400)
    if rq["list_id_showed"].__class__ != list or rq["list_hashtag"].__class__ != list or rq["place"].__class__ != str:
        abort(400)
    try:
        list_showed = [ObjectId(s) for s in rq["list_id_showed"]]
        hashtag = check_list_hashtag(rq["list_hashtag"])
        place = check_place(rq["place"])
    except:
        abort(400)

    if g.current_token is not None and len(hashtag)==0:
        token = g.current_token
        try:
            list_post = recommend_post(token.id_user, list_showed, place)
        except:
            abort(403)
        return {"list_post": list_post}
    else:
        if len(hashtag) > 0:
            try:
                list_post = search_post(list_showed, place, hashtag)
            except:
                abort(403)
            return {"list_post": list_post}
        else:
            try:
                list_post = get_all_post(list_showed, place)
            except:
                abort(403)
            response=make_response({"list_post": list_post})
            response.status_code=401
            return response


@bp.route('/post/<id>', methods=['GET'])
@token_auth.login_required(optional=True, role="applicant")
def get_post(id):
    global post
    try:
        post = get_post_info(ObjectId(id))
    except:
        abort(403)
    if post is None:
        abort(404)
    if g.current_token is not None:
        threading.Thread(target=learn_applicant_hashtag, args=(g.current_token.id_user, post[0]["hashtag"],)).start()
    return {"post": post}


@bp.route('/post', methods=['POST'])
@token_auth.login_required(role="employer")
def post_post():
    global id_post, deadline
    token = g.current_token
    rq = request.json
    if not rq or not 'title' in rq or not 'description' in rq or not 'request' in rq or \
            not 'benefit' in rq or not 'place' in rq or not 'salary' in rq or \
            not 'deadline' in rq or not 'hashtag' in rq or not 'address' in rq:
        abort(400)
    if rq["title"].__class__ != str or rq["description"].__class__ != str or rq["request"].__class__ != str or rq[
        "benefit"].__class__ != str or rq["place"].__class__ != list or rq["salary"].__class__ != str or rq[
        "deadline"].__class__ != str or rq["hashtag"].__class__ != list or rq["address"].__class__ != str:
        abort(400)
    hashtag = check_list_hashtag(rq["hashtag"])
    place = check_list_place(rq["place"])

    if len(hashtag) == 0:
        abort(400)

    if len(place) == 0:
        abort(400)

    try:
        deadline = datetime.datetime.strptime(rq["deadline"], '%d/%m/%Y')
    except:
        abort(400)

    try:
        id_post=new_post(rq["title"], rq["description"], rq["request"], rq["benefit"], place, rq["salary"], deadline, hashtag, rq["address"], token.id_user)
    except:
        abort(403)

    threading.Thread(target=create_candidate_list_for_post, args=(token.id_user, rq["title"],)).start()
    threading.Thread(target=learn_employer_hashtag, args=(token.id_user, hashtag,)).start()

    return {"id_post": str(id_post)}


@bp.route('/post/<id>', methods=['PUT'])
@token_auth.login_required()
def put_post(id):
    global db_post, deadline
    token = g.current_token
    try:
        db_post = find_post(ObjectId(id))
    except:
        abort(403)

    if db_post is None:
        abort(404)

    if db_post["employer"] != token.id_user:
        abort(405)

    rq = request.json
    if not rq or not 'title' in rq or not 'description' in rq or not 'request' in rq or \
            not 'benefit' in rq or not 'place' in rq or not 'salary' in rq or \
            not 'deadline' in rq or not 'hashtag' in rq or not 'address' in rq:
        abort(400)
    if rq["title"].__class__ != str or rq["description"].__class__ != str or rq["request"].__class__ != str or rq[
        "benefit"].__class__ != str or rq["place"].__class__ != list or rq["salary"].__class__ != str or rq[
        "deadline"].__class__ != str or rq["hashtag"].__class__ != list or rq["address"].__class__ != str:
        abort(400)
    hashtag = check_list_hashtag(rq["hashtag"])
    place = check_list_place(rq["place"])

    if len(hashtag) == 0:
        abort(400)

    if len(place) == 0:
        abort(400)

    try:
        deadline = datetime.datetime.strptime(rq["deadline"], '%d/%m/%Y')
    except:
        abort(400)

    try:
        update_post(db_post, ObjectId(id), rq["title"], rq["description"], rq["request"], rq["benefit"], place, rq["salary"], deadline, hashtag, rq["address"])
    except:
        abort(403)

    return "ok"


@bp.route('/post/<id>', methods=['DELETE'])
@token_auth.login_required()
def delete_post(id):
    global db_post
    token = g.current_token
    try:
        db_post = find_post(ObjectId(id), {"_id": 0, "employer": 1})
    except:
        abort(403)

    if db_post is None:
        abort(404)

    if db_post["employer"] != token.id_user:
        abort(405)

    delete_post_by_id(ObjectId(id))
    return "ok"


@bp.route("/post/my", methods=['GET'])
@token_auth.login_required(role="employer")
def get_my_post():
    global page
    try:
        page = int(request.args.get('page', default=0))
    except:
        abort(400)
    token = g.current_token
    try:
        list_post = get_post_of_employer(token.id_user, page)
        return {"list_post": list_post}
    except:
        abort(403)


@bp.route("/post/my/page", methods=['GET'])
@token_auth.login_required(role="employer")
def get_number_my_post_page():
    token = g.current_token
    try:
        return {"count_page": count_page_my_list_post(token.id_user)}
    except:
        abort(403)