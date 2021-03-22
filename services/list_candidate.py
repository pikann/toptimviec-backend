from services import db
from models.List_Candidate import List_Candidate


def create_candidate_list(id_user, name):
    list_candidate = List_Candidate(id_user)
    list_candidate.name = name
    db.list_candidate.insert_one(list_candidate.__dict__)
    return list_candidate.id()


def create_candidate_list_for_post(id_user, name):
    try:
        list_candidate = List_Candidate(id_user)
        list_candidate.name = name
        db.list_candidate.insert_one(list_candidate.__dict__)
    except:
        pass


def get_list_my_list_candidate(id_user, page):
    return list(db.list_candidate.find({"employer": id_user}, {"_id": 1, "name": 1}).sort([("_id", -1)]).skip(page * 10).limit(10))


def add_candidate(id_list, id_user, id_cv):
    db.list_candidate.update({"_id": id_list, "employer": id_user}, {"$addToSet": {"list": id_cv}})


def remove_candidate(id_list, id_user, id_cv):
    return db.list_candidate.update_one({"_id": id_list, "employer": id_user}, {"$pull": {"list": id_cv}})


def get_candidate_list(id_list, id_user):
    candidate_list = db.list_candidate.find_one({"_id": id_list, "employer": id_user})
    if len(candidate_list["list"]) == 0:
        return {"_id": str(candidate_list["_id"]), "name": candidate_list["name"], "list": candidate_list["list"]}
    candidate_list = list(db.list_candidate.aggregate([{"$match": {"_id": id_list, "employer": id_user}},
                                                       {"$unwind": "$list"},
                                                       {"$lookup": {
                                                           "from": "cv",
                                                           "localField": "list",
                                                           "foreignField": "_id",
                                                           "as": "list"
                                                       }},
                                                       {"$unwind": "$list"},
                                                       {"$set": {
                                                           "list._id": {"$toString": "$list._id"}
                                                       }},
                                                       {"$group": {
                                                           "_id": "$_id",
                                                           "name": {"$first": "$name"},
                                                           "list": {"$push": "$list"}
                                                       }},
                                                       {"$project": {
                                                           "_id": 1,
                                                           "name": 1,
                                                           "list._id": 1,
                                                           "list.name": 1,
                                                           "list.avatar": 1,
                                                           "list.position": 1,
                                                           "list.hashtag": 1,
                                                           "list.place": 1
                                                       }},
                                                       {"$set": {
                                                           "_id": {"$toString": "$_id"}
                                                       }}]))[0]
    return candidate_list


def update_list_name(id_list, id_user, name):
    db.list_candidate.update_one({"_id": id_list, "employer": id_user}, {"$set": {"name": name}})


def delete_list(id_list, id_user):
    return db.list_candidate.delete_one({"_id": id_list, "employer": id_user})
