from selenium import webdriver
from selenium.webdriver.common.by import By
from controller import db

driver = webdriver.Chrome("C:/Users/hvhai/Downloads/chromedriver_win32/chromedriver.exe")

driver.get("https://www.topcv.vn/")
driver.find_element(By.XPATH, "//span[@id='select2-city-container']").click()

list_option=driver.find_element(By.XPATH, "//ul[@id='select2-city-results']").find_elements_by_tag_name("li")[1:]
for option in list_option:
    print(option.text.strip())
    db.place.update_one({"name": option.text.strip()}, {"$set": {"name": option.text.strip()}}, upsert=True)