from model import CV, CV_Block, CV_Row
import datetime
import random
from controller import list_hashtag, db

for step in range(10000):
    print(step)
    cv=CV()
    cv.name="Nguyễn Văn A"
    cv.gender = bool(random.getrandbits(1))
    cv.avatar = "https://res.cloudinary.com/pikann22/image/upload/v1615044354/toptimviec/TCM27Jw1N8ESc1V0Z3gfriuG1NjS_hXXIww7st_jZ0bFz3xGRjKht7JXzfLoU_ZelO4KPiYFPi-ZBVZcR8wdQXYHnwL5SDFYu1Yf7UBT4jhd9d8gj0lCFBA5VbeVp9SveFfJVKRcLON-OyFX_kxrs3f.png"
    cv.position = "Developer"
    cv.dob = datetime.datetime.strptime("1/1/1999", "%d/%m/%Y")
    cv.address = "Liên Chiểu, Đà Nẵng"
    cv.email = "abc@gmail.com"
    cv.phone = "0123456789"
    cv.place = "Đà Nẵng"
    rand_hashtags=[]
    for i in range(5):
        rand_hashtag=random.choice(list_hashtag)
        while rand_hashtag in rand_hashtags:
            rand_hashtag = random.choice(list_hashtag)
        rand_hashtags.append(rand_hashtag)
    for i in range(5):
        cv.skill.append({"skill": rand_hashtags[i], "rate": random.randint(1, 5)})
    cv.hashtag = rand_hashtags

    block=CV_Block()

    block.title="MỤC TIÊU NGHỀ NGHIỆP"
    row=CV_Row()
    row.detail="Là người có tư duy logic và khả năng sáng tạo tốt, tôi mong muốn trở thành một trong những lập trình viên chủ chốt của công ty để mang lại những giải pháp công nghệ tối ưu cho khách hàng. Đồng thời, tôi muốn được nâng cao trình độ chuyên môn và năng lực nghề nghiệp thông qua môi trường làm việc chuyên nghiệp của công ty."
    block.content.append(row.__dict__.copy())
    cv.content.append(block.__dict__.copy())

    block.title="HỌC VẤN"
    block.content=[]
    row.title="ĐẠI HỌC BÁCH KHOA"
    row.time="1/2010 - 1/2014"
    row.position="Chuyên ngành: Công nghệ thông tin"
    row.detail=""
    block.content.append(row.__dict__.copy())
    cv.content.append(block.__dict__.copy())

    block.title="KINH NGHIỆM LÀM VIỆC"
    block.content=[]
    row.title="CÔNG TY TOPTIMVIEC"
    row.time="01/2015 - HIỆN TẠI"
    row.position="Product Developer"
    row.detail="- UX/ UI Direction\n- Xây dựng các ứng dụng web\n- Xây dựng ứng dụng mobile"
    block.content.append(row.__dict__.copy())
    cv.content.append(block.__dict__.copy())

    block.title="HOẠT ĐỘNG"
    block.content=[]
    row.title="CÂU LẠC BỘ TIMTIMVIEC"
    row.time="01/2013 - 01/2014"
    row.position="Thành viên"
    row.detail="Tham gia các cuộc thi Coding Contest, xây dựng một số sản phẩm phục vụ Coding Contest"
    block.content.append(row.__dict__.copy())
    cv.content.append(block.__dict__.copy())

    block.title="CHỨNG CHỈ"
    block.content=[]
    row.title="GIẢI NHẤT TÀI NĂNG TOPTIMVIEC"
    row.time="2013"
    row.position=""
    row.detail=""
    block.content.append(row.__dict__.copy())
    cv.content.append(block.__dict__.copy())

    block.title="GIẢI THƯỞNG"
    block.content=[]
    row.title="NHÂN VIÊN XUẤT SẮC NĂM CÔNG TY TOPTIMVIEC"
    row.time="2014"
    row.position=""
    row.detail=""
    block.content.append(row.__dict__.copy())
    cv.content.append(block.__dict__.copy())

    cv.interests = ["Chơi game", "Đọc truyện"]

    db.cv.insert_one(cv.__dict__)