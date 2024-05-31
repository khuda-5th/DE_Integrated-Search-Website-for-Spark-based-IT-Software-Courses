from codeit_lecture import *
from selenium import webdriver 
from selenium.webdriver.common.by import By  
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import json
import time

global all_data
all_data = []

def parseLectures(driver, sub, big_categ):
    category_data = {
        "big_categ": big_categ,
        "sub_categs": []
    }

    for s, element_xpath in sub:
        try:
            sub_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, element_xpath))
            )
        
            # JavaScript를 사용하여 클릭하기
            driver.execute_script("arguments[0].click();", sub_btn)
            print("소분류 클릭 완료")

            time.sleep(2)  # 강의가 로드될 시간
            
            # href 속성을 저장할 리스트
            hrefs = []

            while True:
                elems = driver.find_elements(By.XPATH, '//*[@id="root"]/div[1]/div[3]/div/div[3]/div[2]/div/div[4]/div/a')
                hrefs.extend([e.get_attribute("href") for e in elems])

                try:
                    next_button = driver.find_element(By.CLASS_NAME, 'Pagination_next__2ITxI')
                    if "Pagination_disabled__3lKZz" in next_button.get_attribute("class"):
                        break
                    driver.execute_script("arguments[0].click();", next_button)
                    print("페이지 버튼 클릭 완료")
                    time.sleep(2)
                except NoSuchElementException:
                    break

            sub_categ_data = {
                "sub_categ": s,
                "lectures": []
            }
            
            for url in hrefs:
                lecture_data = crawl_and_save(driver, url)
                sub_categ_data["lectures"].append(lecture_data)
                print("******소분류 내 강의 적재 완료********")

            # 서브 카테고리 데이터를 상위 카테고리 데이터에 추가
            category_data["sub_categs"].append(sub_categ_data)
            driver.get(lectures_url)

        except NoSuchElementException as e:
            print(f"Element not found for sub-category: {s} with xpath: {element_xpath}")
            continue

    # 전체 데이터에 추가
    all_data.append(category_data)
    print("********대분류 데이터 적재 완료********")

    # JSON 파일에 저장
    with open('codeit_retry2.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("*********JSON 저장 완료**********")

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

lectures_url = "https://www.codeit.kr/explore"

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
driver.get(lectures_url)
wait_until_page_loaded(driver)

big_categ = "웹 개발"
sub = []
l = 1
while True:
    try:
        element_xpath = f'//*[@id="root"]/div[1]/div[3]/div/div[3]/div[1]/div/form/div[3]/div/div[3]/div/div[2]/div/div[{l}]'
        time.sleep(1)
        element = driver.find_element(By.XPATH, element_xpath)
        sub.append((element.text, element_xpath))
        l+=1
    except NoSuchElementException:
        break
parseLectures(driver, sub, big_categ)

big_categ = "데이터 사이언스"
sub = []
l = 1
while True:
    try:
        element_xpath = f'//*[@id="root"]/div[1]/div[3]/div/div[3]/div[1]/div/form/div[3]/div/div[3]/div/div[3]/div/div[{l}]'
        time.sleep(1)
        element = driver.find_element(By.XPATH, element_xpath)
        sub.append((element.text, element_xpath))
        l+=1
    except NoSuchElementException:
        break
parseLectures(driver, sub, big_categ)


big_categ = "컴퓨터 사이언스"
sub = []
l = 1
while True:
    try:
        element_xpath = f'//*[@id="root"]/div[1]/div[3]/div/div[3]/div[1]/div/form/div[3]/div/div[3]/div/div[4]/div/div[{l}]'
        time.sleep(1)
        element = driver.find_element(By.XPATH, element_xpath)
        sub.append((element.text, element_xpath))
        l+=1
    except NoSuchElementException:
        break
parseLectures(driver, sub, big_categ)


big_categ = "프로그래밍 언어"
sub = []
l = 1
while True:
    try:
        element_xpath = f'//*[@id="root"]/div[1]/div[3]/div/div[3]/div[1]/div/form/div[3]/div/div[3]/div/div[5]/div/div[{l}]'
        time.sleep(1)
        element = driver.find_element(By.XPATH, element_xpath)
        sub.append((element.text, element_xpath))
        l+=1
    except NoSuchElementException:
        break  
parseLectures(driver, sub, big_categ)


big_categ = "기타"
sub = []
l = 1
while True:
    try:
        element_xpath = f'//*[@id="root"]/div[1]/div[3]/div/div[3]/div[1]/div/form/div[3]/div/div[3]/div/div[6]/div/div[{l}]'
        time.sleep(1)
        element = driver.find_element(By.XPATH, element_xpath)
        sub.append((element.text, element_xpath))
        l+=1
    except NoSuchElementException:
        break
parseLectures(driver, sub, big_categ)


driver.quit()