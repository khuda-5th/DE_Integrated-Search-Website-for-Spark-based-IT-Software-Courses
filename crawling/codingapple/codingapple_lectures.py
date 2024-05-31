from selenium import webdriver 
from selenium.webdriver.common.by import By  
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

def wait_until_page_loaded(driver):
    timeout = 30
    WebDriverWait(driver, timeout).until(
        lambda x: x.execute_script("return document.readyState == 'complete'")
    )
    print("*************페이지 로드 완료***************")

def crawl_and_save(driver, url):
    driver.get(url)
    wait_until_page_loaded(driver)
    
    try:
        categ = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="item-header-content"]/ul/li[3]/span/a'))
        ).text
    except:
        categ = None
    try:
        title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="item-header-content"]/h1'))
        ).text
    except:
        title = None
    try:
        review_num = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="item-meta"]/strong[2]'))
        ).text
    except:
        review_num = None
    try:
        star = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="course-reviews"]/div[1]/div[1]/div/h2'))
        ).text
    except:
        star = None
    try:
        students = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="item-meta"]/div'))
        ).text
    except:
        students = None
    try:
        price = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="course-pricing"]/div[1]/ul/li[1]'))
        ).text
    except:
        price = None
    try:
        img = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'img'))
                ).get_attribute('src')
    except:
        img = None
    try:
        summary = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="course-home"]/div'))
        ).text
    except:
        summary = None
    try:
        curriculum = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'course_curriculum.accordion'))
        ).text
    except:
        curriculum = None
    try:
        review = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'reviewlist.commentlist'))
        ).text
    except:
        review = None

    course_data = {
        "categ": categ,
        "title": title,
        "review_num": review_num,
        "star": star,
        "students": students,
        "price": price,
        "img": img,
        "summary": summary,
        "curriculum": curriculum,
        "review": review
    }

    return course_data

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

lectures_url = "https://codingapple.com/all-courses/"
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
driver.get(lectures_url)

wait_until_page_loaded(driver)

lectures = driver.find_elements(By.CSS_SELECTOR, "div > div.col-md-8.col-sm-8 > div > div.item-title > a")
hrefs = [l.get_attribute("href") for l in lectures]

all_courses_data = []

for url in hrefs:
    course_data = crawl_and_save(driver, url)
    all_courses_data.append(course_data)

driver.quit()

# JSON 파일로 저장
with open('codingapple.json', 'w', encoding='utf-8') as f:
    json.dump(all_courses_data, f, ensure_ascii=False, indent=4)

print("데이터가 codingapple.json 파일로 저장되었습니다.")
