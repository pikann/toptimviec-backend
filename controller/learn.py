from controller import db


def learn_employer_hashtag(id_user, cv_hashtag):
    try:
        user = db.employer.find_one({"_id": id_user})
        user_hashtag = user["hashtag"]
        hashtag = {}
        for h in cv_hashtag:
            user_hashtag[h] += 1
        for h in user_hashtag:
            hashtag[h] = user_hashtag[h] * 10 / sum(user_hashtag.values())
        db.employer.update_one({"_id": id_user}, {"$set": {"hashtag": hashtag}})
    except:
        pass


def learn_applicant_hashtag(id_user, post_hashtag):
    try:
        user = db.applicant.find_one({"_id": id_user})
        user_hashtag = user["hashtag"]
        hashtag = {}
        for h in post_hashtag:
            user_hashtag[h] += 1
        for h in user_hashtag:
            hashtag[h] = user_hashtag[h] * 10 / sum(user_hashtag.values())
        db.applicant.update_one({"_id": id_user}, {"$set": {"hashtag": hashtag}})
    except:
        pass