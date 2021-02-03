from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from model import Applicant, CV
from controller import db
import json
import datetime
import time

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_options.add_argument('window-size=1920x1080')
chrome_options.add_argument("disable-gpu")

driver = webdriver.Chrome("C:/Users/hvhai/Downloads/chromedriver_win32/chromedriver.exe")

list_hashtag = [d["name"] for d in list(db.hashtag.find({}, {"_id": 0, "name": 1}))]
list_place = [p["name"] for p in list(db.place.find({}, {"_id": 0, "name": 1}))]


def crawl_cv(url, applicant):
    driver.execute_script("window.open('" + url + "');")
    driver.switch_to.window(driver.window_handles[1])

    gender=""

    try:
        gender=driver.find_element(By.XPATH, "//span[@id='cvo-profile-gender']").text.strip()
    except:
        pass

    if gender.lower() in ["female", "nữ"]:
        applicant.gender=True
    else:
        applicant.gender=False

    try:
        str_date=driver.find_element(By.XPATH, "//span[@id='cvo-profile-dob']").text.strip()

        for form in ["%b %d, %Y", "%d/%m/%Y"]:
            try:
                applicant.dob=datetime.datetime.strptime(str_date, form)
            except ValueError:
                continue
            break
    except:
        pass

    cv=CV()
    cv.url=url
    text=driver.find_element_by_tag_name("body").text

    for hashtag in list_hashtag:
        if hashtag.lower() in text.lower():
            if hashtag not in cv.hashtag:
                cv.hashtag.append(hashtag)

    applicant.list_CV.append(cv.id())
    applicant.main_CV=cv.id()

    driver.get(url[:-12])

    url_pdf=driver.find_element(By.XPATH, "//div[@class='btn-download-cv-private']").find_element_by_tag_name("a").get_attribute("href")

    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def crawl_list_cv():
    driver.get("https://tuyendung.topcv.vn/chien-dich-tim-kiem-ung-vien/128124")

    print("Handle captcha...", end="")
    input()

    driver.find_element(By.XPATH, "//input[@id='keyword']").send_keys("Lập trình viên")
    driver.find_element(By.XPATH, "//button[@class='btn btn-block btn-primary']").click()

    time.sleep(2)

    candidate_list=driver.find_element(By.XPATH, "//div[@class='candidate-list']").find_elements(By.XPATH, ".//div[@class='candidate']")

    for candidate in candidate_list:
        applicant=Applicant()
        applicant.name=candidate.find_element(By.XPATH, ".//a[@class='name']").text.strip()
        applicant.avatar=candidate.find_element_by_tag_name("img").get_attribute("src")
        place=candidate.find_element(By.XPATH, ".//div[@class='location']").text.strip()[10:]
        if place in list_place:
            applicant.place=place
        candidate.find_element(By.XPATH, ".//a[@class='name']").click()

        time.sleep(2)

        url = driver.find_element(By.XPATH, "//iframe[@id='iframe-view-candidate']").get_attribute("src")



        driver.find_element(By.XPATH, ".//a[text()=' Đóng lại']").click()


def login():
    driver.get("https://tuyendung.topcv.vn/login")

    with open("topcv_account.json") as json_file:
        account = json.load(json_file)
        email = account["email"]
        password = account["password"]

    driver.find_element(By.XPATH, "//input[@name='email']").send_keys(email)
    driver.find_element(By.XPATH, "//input[@name='password']").send_keys(password)

    driver.find_element(By.XPATH, "//input[@name='password']").send_keys(Keys.ENTER)


if __name__=="__main__":
    # login()
    # crawl_list_cv()
    crawl_cv("https://www.topcv.vn/private/93b3de08706153190caede9e10e0f448?token=5d2e8fd3c1e179b26f1b8aae11d019df&al=2&sig=eyJkYXRhIjp7InByaXZhdGVfa2V5IjoiOTNiM2RlMDg3MDYxNTMxOTBjYWVkZTllMTBlMGY0NDgifSwiZXhwaXJlQXQiOiIyMDIxLTAyLTAzIDIxOjI5OjM4Iiwic2lnbmF0dXJlIjoiMzE4MjE3ZWE2YWZkMjg2ZTNjMWM4ZDcyYmNhOTU5YTgifQ%3D%3D&iframe=true",
             applicant=Applicant())