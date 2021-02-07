from controller import bp, list_hashtag, list_place

@bp.route('/list-hashtag', methods=['GET'])
def get_list_hashtag():
    return {"list_hashtag": list_hashtag}

@bp.route('/list-place', methods=['GET'])
def get_list_place():
    return {"list_place": list_place}