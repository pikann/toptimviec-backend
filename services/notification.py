from services import db
from models.Notification import Notification
from routes.socket import socketio


def notify_mail(id_user, role, receivers, title, id_mail):
    global user
    try:
        notify_content = "Bạn có một thư mới từ "
        if role == "employer":
            user = db.employer.find_one({"_id": id_user}, {"_id": 0, "name": 1, "avatar": 1})
        elif role == "applicant":
            user = db.applicant.find_one({"_id": id_user}, {"_id": 0, "name": 1, "avatar": 1})
        notify_content += user["name"] + ": " + title
    except:
        return

    for receiver in receivers:
        try:
            notification = Notification(user=receiver, type="mail", id_attach=id_mail, content=notify_content, img=user["avatar"])
            db.notification.insert(notification.__dict__)
        except:
            pass
        try:
            socketio.emit("new", {"type": "mail", "content": notify_content, "img": user["avatar"], "id_attach": str(id_mail)}, room=str(receiver))
        except:
            pass


def get_list_notification(id_user, list_showed):
    list_notify = list(db.notification.find({"user": id_user, "_id": {"$not": {"$in": list_showed}}}, {"user": 0}).sort([("_id", -1)]).limit(10))
    db.notification.update_many({"_id": {"$in": [notify["_id"] for notify in list_notify]}}, {"$set": {"read": True}})
    for notify in list_notify:
        notify["id_attach"] = str(notify["id_attach"])
        notify["_id"] = str(notify["_id"])
    return list_notify
