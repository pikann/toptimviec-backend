from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from model import Post, Employer
from controller import db
import json
import datetime

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_options.add_argument('window-size=1920x1080')
chrome_options.add_argument("disable-gpu")

driver = webdriver.Chrome("C:/Users/hvhai/Downloads/chromedriver_win32/chromedriver.exe", options=chrome_options)

list_hashtag = [d["name"] for d in list(db.hashtag.find({}, {"_id": 0, "name": 1}))]
list_place = [p["name"] for p in list(db.place.find({}, {"_id": 0, "name": 1}))]


def crawl_employer(url):
    print("Crawling employer: " + url)

    employer_db = db.employer.find_one({"url": url}, {"_id": 1})
    if employer_db is not None:
        return employer_db["_id"]

    driver.get(url)

    employer = Employer()
    employer.url = url

    employer.name = driver.find_element(By.XPATH,
                                        "//h1[@class='company-detail-name text-highlight']").text.strip()
    employer.bio = driver.find_element(By.XPATH,
                                       "//div[@class='box box-white']").text
    employer.avatar = driver.find_element(By.XPATH,
                                          "//div[@id='company-logo']").find_element_by_tag_name("img").get_attribute(
        "src")
    db.employer.insert_one(employer.__dict__)
    return employer.id()


def crawl_post(url, place):
    print("Crawling post: " + url)

    post_db = db.post.find_one({"url": url}, {"_id": 1})
    if post_db is not None:
        return

    driver.execute_script("window.open('" + url + "');")
    driver.switch_to.window(driver.window_handles[1])

    post = Post()
    post.url = url

    try:
        post.title = driver.find_element(By.XPATH,
                                         "//h1[@class='job-title text-highlight bold text-uppercase']").text.strip()
    except:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return

    content = driver.find_element(By.XPATH, "//div[@id='col-job-left']")
    list_h2 = content.find_elements_by_tag_name("h2")
    list_content_tab = content.find_elements(By.XPATH, ".//div[@class='content-tab']")

    for i, h2 in enumerate(list_h2):
        if h2.text.strip() == "MÔ TẢ CÔNG VIỆC":
            post.description = list_content_tab[i].text
        elif h2.text.strip() == "YÊU CẦU ỨNG VIÊN":
            post.request = list_content_tab[i].text
        elif h2.text.strip() == "QUYỀN LỢI ĐƯỢC HƯỞNG":
            post.benefit = list_content_tab[i].text
        elif h2.text.strip() == "CÁCH THỨC ỨNG TUYỂN":
            text_date = list_content_tab[i].find_elements_by_tag_name("p")[-1].text[15:].strip()
            post.deadline = datetime.datetime.strptime(text_date, '%d/%m/%Y')
        else:
            break

    for hashtag in list_hashtag:
        if hashtag.lower() in post.title.lower() or hashtag.lower() in post.description.lower() or hashtag.lower() in post.request.lower():
            if hashtag not in post.hashtag:
                post.hashtag.append(hashtag)

    if len(post.hashtag) == 0:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return

    list_info = driver.find_element(By.XPATH, "//div[@id='box-info-job']").find_elements(By.XPATH,
                                                                                         ".//div[@class='job-info-item']")

    for info in list_info:
        if info.find_element_by_tag_name("strong").text.strip() == "Mức lương:":
            post.salary = info.find_element_by_tag_name("span").text.strip()

    post.place = place

    employer_url = driver.find_element(By.XPATH,
                                       "//div[@class='company-logo-wraper text-center']").find_element_by_tag_name(
        "a").get_attribute("href")
    post.employer = crawl_employer(employer_url)

    db.post.insert_one(post.__dict__)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def crawl_employer_brand(url):
    print("Crawling employer: " + url)

    employer_db = db.employer.find_one({"url": url}, {"_id": 1})
    if employer_db is not None:
        return employer_db["_id"]

    driver.get(url)

    employer = Employer()
    employer.url = url

    employer.name = driver.find_element(By.XPATH,
                                        "//div[@id='company-name']").find_element_by_tag_name("h1").text.strip()
    employer.bio = driver.find_element(By.XPATH,
                                       "//div[@class='intro-content']").text.strip()
    employer.avatar = driver.find_element(By.XPATH,
                                          "//div[@id='company-logo']").find_element_by_tag_name("img").get_attribute(
        "src")
    db.employer.insert_one(employer.__dict__)
    return employer.id()


def crawl_post_brand(url, place):
    print("Crawling post: " + url)

    post_db = db.post.find_one({"url": url}, {"_id": 1})
    if post_db is not None:
        return

    driver.execute_script("window.open('" + url + "');")
    driver.switch_to.window(driver.window_handles[1])

    post = Post()
    post.url = url

    try:
        post.title = driver.find_element(By.XPATH,
                                         "//h2[@class='job-name text-premium']").text.strip()
    except:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return

    content = driver.find_element(By.XPATH, "//div[@class='job-data']")
    list_h2 = content.find_elements(By.XPATH, ".//p[@class='heading']")
    list_content_tab = content.find_elements_by_tag_name("div")

    for i, h2 in enumerate(list_h2):
        if h2.text.strip() == "MÔ TẢ CÔNG VIỆC":
            post.description = list_content_tab[i].text
        elif h2.text.strip() == "YÊU CẦU ỨNG VIÊN":
            post.request = list_content_tab[i].text
        elif h2.text.strip() == "QUYỀN LỢI ĐƯỢC HƯỞNG":
            post.benefit = list_content_tab[i].text
        else:
            break

    for hashtag in list_hashtag:
        if hashtag.lower() in post.title.lower() or hashtag.lower() in post.description.lower() or hashtag.lower() in post.request.lower():
            if hashtag not in post.hashtag:
                post.hashtag.append(hashtag)

    if len(post.hashtag) == 0:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return

    post.salary = driver.find_element(By.XPATH, "//span[@data-original-title='Mức lương']").text.strip()

    post.place = place

    employer_url = driver.find_element(By.XPATH, "//a[text()='Giới thiệu']").get_attribute("href")
    post.employer = crawl_employer_brand(employer_url)

    db.post.insert_one(post.__dict__)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def crawl_list_post():
    path_url = "https://www.topcv.vn/tim-viec-lam-it-phan-mem-c10026?salary=0&exp=0&company_field=0&page="
    i = 0
    while True:
        i += 1
        print("Crawling page " + str(i))
        driver.get(path_url + str(i))

        list_box = driver.find_element(By.XPATH, "//div[@class='job-list search-result']").find_elements(By.XPATH,
                                                                                                         "//div[@class='row job']")
        if len(list_box) == 0:
            return
        for box in list_box:
            place = []
            url = box.find_element(By.XPATH, ".//h4[@class='job-title']").find_element_by_tag_name("a").get_attribute(
                "href")
            try:
                text_places = box.find_element(By.XPATH, ".//span[@class='address']").text.strip()[9:]
                for text_place in text_places.split(","):
                    if text_place.strip() in list_place:
                        place.append(text_place.strip())
            except:
                pass
            if len(place) == 0:
                place.append("Toàn quốc")

            if "https://www.topcv.vn/brand/" in url:
                crawl_post_brand(url, place)
            elif "https://www.topcv.vn/viec-lam/" in url:
                crawl_post(url, place)


def login():
    driver.get("https://www.topcv.vn/login")

    with open("topcv_account.json") as json_file:
        account = json.load(json_file)
        email = account["email"]
        password = account["password"]

    driver.find_element(By.XPATH, "//input[@name='email']").send_keys(email)
    driver.find_element(By.XPATH, "//input[@name='password']").send_keys(password)

    driver.find_element(By.XPATH, "//input[@name='password']").send_keys(Keys.ENTER)


if __name__ == "__main__":
    login()
    # crawl_post_brand("https://www.topcv.vn/brand/vnpay/tuyen-dung/lap-trinh-vien-ios-tp-ho-chi-minh-j337466.html", ["Hà Nội"])
    crawl_list_post()
    # crawl_post("https://www.topcv.vn/viec-lam/lap-trinh-vien-java-fis-egp/343808.html")
