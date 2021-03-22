from services import db

list_hashtag = [d["name"] for d in list(db.hashtag.find({}, {"_id": 0, "name": 1}))]
list_place = [p["name"] for p in list(db.place.find({}, {"_id": 0, "name": 1}))]


def check_list_hashtag(hashtags):
    return [h for h in hashtags if h in list_hashtag]


def check_place(place):
    if place in list_place:
        return place
    else:
        return ""


def check_list_place(places):
    return [p for p in places if p in list_place]
