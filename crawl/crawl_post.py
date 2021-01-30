from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from model import Post
from controller import db
import json
import datetime

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_options.add_argument('window-size=1920x1080')
chrome_options.add_argument("disable-gpu")

driver = webdriver.Chrome("C:/Users/hvhai/Downloads/chromedriver_win32/chromedriver.exe")


def crawl_post(url):
    driver.execute_script("window.open('" + url + "');")
    driver.switch_to.window(driver.window_handles[1])

    post = Post()

    post.title = driver.find_element(By.XPATH,
                                     "//h1[@class='job-title text-highlight bold text-uppercase']").text.strip()

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

    list_info = driver.find_element(By.XPATH, "//div[@id='box-info-job']").find_elements(By.XPATH,
                                                                                         ".//div[@class='job-info-item']")

    for info in list_info:
        if info.find_element_by_tag_name("strong").text.strip() == "Mức lương:":
            post.salary = info.find_element_by_tag_name("span").text.strip()
        elif info.find_element_by_tag_name("strong").text.strip() == "Địa điểm làm việc:":
            list_place = info.find_elements_by_tag_name("a")
            for place in list_place:
                name_place = place.text.strip()
                db.place.update_one({"name": name_place}, {"$set": {"name": name_place}}, upsert=True)
                post.place.append(name_place)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])


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
    crawl_post("https://www.topcv.vn/viec-lam/lap-trinh-vien-java-fis-egp/343808.html")
