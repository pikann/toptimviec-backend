from controller import db

list_id=list(db.post.find({}, {"_id": 1}))
list_hashtag = [d["name"] for d in list(db.hashtag.find({}, {"_id": 0, "name": 1}))]

for i, id in enumerate(list_id):
    print(i)
    post=db.post.find_one(id)
    if len(post["hashtag"])>5:
        post_hashtag={}
        for hashtag in list_hashtag:
            if hashtag.lower() in post["title"].lower():
                if hashtag in post_hashtag:
                    post_hashtag[hashtag] += post["title"].lower().count(hashtag.lower())
                else:
                    post_hashtag[hashtag] = post["title"].lower().count(hashtag.lower())
            if hashtag.lower() in post["description"].lower():
                if hashtag in post_hashtag:
                    post_hashtag[hashtag] += post["description"].lower().count(hashtag.lower())
                else:
                    post_hashtag[hashtag] = post["description"].lower().count(hashtag.lower())
            if hashtag.lower() in post["request"].lower():
                if hashtag in post_hashtag:
                    post_hashtag[hashtag] += post["request"].lower().count(hashtag.lower())
                else:
                    post_hashtag[hashtag] = post["request"].lower().count(hashtag.lower())
        rs=[k for k, v in sorted(post_hashtag.items(), key=lambda item: item[1], reverse=True)][:5]
        db.post.update_one(id, {"$set": {"hashtag": rs}})