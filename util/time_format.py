import datetime


def time_sub_format(time):
    sub_time = datetime.datetime.utcnow() - time

    if (sub_time.days > 365):
        return str(sub_time.days // 365) + " năm trước"
    elif (sub_time.days > 30):
        return str(sub_time.days // 30) + " tháng trước"
    elif (sub_time.days > 7):
        return str(sub_time.days // 7) + " tuần trước"
    elif (sub_time.days >= 1):
        return str(sub_time.days) + " ngày trước"
    elif (sub_time.seconds >= 3600):
        return str(sub_time.seconds // 3600) + " giờ trước"
    elif (sub_time.seconds >= 60):
        return str(sub_time.seconds // 60) + " phút trước"
    elif (sub_time.seconds >= 1):
        return str(sub_time.seconds) + " giây trước"
    else:
        return "Vừa xong"


def time_vietnam_format(time):
    return (time + datetime.timedelta(hours=7)).strftime("%d-%m-%Y %H:%M")
