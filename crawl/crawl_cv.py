from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
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
    except NoSuchElementException:
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
    except NoSuchElementException:
        pass

    cv=CV()
    cv.url=url
    cv.gender=applicant.gender
    cv.dob=applicant.dob

    try:
        cv.name=driver.find_element(By.XPATH, "//span[@id='cvo-profile-fullname']").text.strip()
    except NoSuchElementException:
        pass

    try:
        cv.avatar=driver.find_element(By.XPATH, "//img[@id='cvo-profile-avatar']").get_attribute("src")
    except NoSuchElementException:
        pass

    try:
        cv.address=driver.find_element(By.XPATH, "//span[@id='cvo-profile-address']").text.strip()
    except NoSuchElementException:
        pass

    try:
        cv.position=driver.find_element(By.XPATH, "//span[@id='cvo-profile-title']").text.strip()
    except NoSuchElementException:
        pass

    text=driver.find_element_by_tag_name("body").text

    for hashtag in list_hashtag:
        if hashtag.lower() in text.lower().split():
            if hashtag not in cv.hashtag:
                cv.hashtag.append(hashtag)

    applicant.list_CV.append(cv.id())
    applicant.main_CV=cv.id()

    content=[]
    blocks=driver.find_elements(By.XPATH, "//div[@class='cvo-block']")

    for block in blocks:
        col_id=block.find_element(By.XPATH, "..").find_element(By.XPATH, "..").get_attribute("id")
        col_id2=block.find_element(By.XPATH, "..").get_attribute("id")
        if col_id=="col-left" or col_id2=="group-col-left" or col_id2=="group-left":
            col="left"
        elif col_id=="col-right" or col_id2=="group-col-right" or col_id2=="group-right":
            col="right"
        else:
            col=""
        try:
            title=block.find_element(By.XPATH, ".//div[contains(@class, 'cvo-block-title') or contains(@class, 'cvo-block-header')]").text.strip()
            try:
                list_skill_element=block.find_element(By.XPATH, ".//div[@id='skillrate-table']").find_elements(By.XPATH, ".//div[@class='row']")
                skill=[]
                for skill_element in list_skill_element:
                    skill.append({"skill": skill_element.find_element(By.XPATH, ".//span[contains(@class,'cvo-skillrate-title')]").text.strip(),
                                  "rate": int(skill_element.find_element(By.XPATH, ".//div[@class='cvo-skillrate-bar']").get_attribute("rate-value"))})
                content.append({"title": title, "skill": skill, "col": col})
                continue
            except NoSuchElementException:
                pass

            try:
                rows=[]
                row_title_elements = block.find_elements(By.XPATH, ".//div[contains(@class, 'wraper') and not(contains(@class, 'title')) and not(contains(@class, 'time'))]")
                for row_title_element in row_title_elements:
                    row_element=row_title_element.find_element(By.XPATH, "..")
                    row={}
                    try:
                        try:
                            row["title"]=row_title_element.text.strip()
                        except NoSuchElementException:
                            pass
                        try:
                            row["time"]=row_element.find_element(By.XPATH, ".//div[contains(@class, 'time')]").text.strip()
                        except NoSuchElementException:
                            pass
                        try:
                            position=row_element.find_element(By.XPATH, ".//span[contains(@class, 'title') or contains(@class, 'position')]").text.strip()
                            if len(position)>0:
                                row["position"]=position
                        except NoSuchElementException:
                            pass
                    except NoSuchElementException:
                        pass
                    try:
                        row["details"] = row_element.find_element(By.XPATH, ".//div[@class='row-details']").text.strip()
                        try:
                            row["details"]=row["details"].replace(row["position"]+"\n", "").strip()
                        except:
                            pass
                    except NoSuchElementException:
                        try:
                            row["details"] = row_element.find_element(By.XPATH, ".//div[contains(@class, 'details')]").text.strip()
                        except NoSuchElementException:
                            try:
                                row["details"] = row_element.find_element(By.XPATH, "..").find_element(By.XPATH, ".//div[@class='row-details']").text.strip()
                                if row_element.find_element(By.XPATH, "..").find_element(By.XPATH, "..").get_attribute("class")=="row":
                                    row["time"] = row_element.find_element(By.XPATH, "..").find_element(By.XPATH, "..").find_element(By.XPATH, ".//div[contains(@class, 'time')]").text.strip().replace("\n\n", "-")
                            except NoSuchElementException:
                                pass
                    if len(row)==1:
                        rows.append(row_element.text.strip())
                    else:
                        rows.append(row)
                if len(rows)>0:
                    content.append({"title": title, "content": rows, "col": col})
                else:
                    try:
                        content.append({"title": title, "content": block.text.strip()[len(title):].strip(), "col": col})
                    except NoSuchElementException:
                        pass
            except NoSuchElementException:
                try:
                    content.append({"title": title, "content": block.text.strip()[len(title):].strip(), "col": col})
                except NoSuchElementException:
                    pass
        except NoSuchElementException:
            pass

    cv.content=content
    print(cv.__dict__)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def crawl_list_cv():
    driver.get("https://tuyendung.topcv.vn/chien-dich-tim-kiem-ung-vien/131142")

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
    crawl_cv("https://www.topcv.vn/private/36abbc41d539ccbb63bb73707a1e20ff?token=1030834adc7f0fe642ee19c9525bff07&al=2&sig=eyJkYXRhIjp7InByaXZhdGVfa2V5IjoiMzZhYmJjNDFkNTM5Y2NiYjYzYmI3MzcwN2ExZTIwZmYifSwiZXhwaXJlQXQiOiIyMDIxLTAzLTAxIDIxOjU3OjU2Iiwic2lnbmF0dXJlIjoiY2I2MDNjMzY4YWNmYjg1ZmM0YzFmNjA3OWNmMjU0ZmQifQ%3D%3D&iframe=true",
             applicant=Applicant())