from codeit_lecture import *
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time
import json

lectures_url = "https://www.codeit.kr/explore"

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
driver.get(lectures_url)

all_data = []

def parseLectures(sub, big_categ):
    global all_data
    category_data = {
        "big_categ": big_categ,
        "sub_categs": []
    }

    for s, element_xpath in sub:
        driver.find_element(By.XPATH, element_xpath).click()
        time.sleep(3)  # 페이지가 로드될 시간을 줍니다.
        
        # href 속성을 저장할 리스트
        hrefs = []

        while True:
            try:
                # 현재 페이지의 강의 링크들을 수집
                elems = driver.find_elements(By.XPATH, '//*[@id="root"]/div[1]/div[3]/div/div[3]/div[2]/div/div[4]/div/a') # div 더 추가하거나?
                hrefs.extend([e.get_attribute('href') for e in elems])
                
                # 다음 페이지 버튼 클릭
                next_button = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[3]/div/div[3]/div[2]/div/div[5]/div/div/button[last()]')
                if 'disabled' in next_button.get_attribute('class'):
                    break
                next_button.click()
                time.sleep(3)  # 페이지가 로드될 시간을 줍니다.
            except NoSuchElementException:
                break
        time.sleep(2)

        sub_categ_data = {
            "sub_categ": s,
            "lectures": []
        }
        
        for url in hrefs:
            lecture_data = crawl_and_save(driver, url)
            sub_categ_data["lectures"].append(lecture_data)
            print("적재 완료")

        
        # 서브 카테고리 데이터를 상위 카테고리 데이터에 추가
        category_data["sub_categs"].append(sub_categ_data)

    # 상위 카테고리 데이터를 전체 데이터에 추가
    all_data.append(category_data)
    print("카테고리 적재 완료:", category_data)

    # JSON 파일에 저장
    with open('codeit_lectures.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("전체 데이터 저장 완료")

for i in range(0,5):

    if i==4:
        big_categ = "기타"
        sub = []
        l = 1
        while True:
            try:
                element_xpath = f'//*[@id="root"]/div[1]/div[3]/div/div[3]/div[1]/div/form/div[3]/div/div[3]/div/div[6]/div/div[{l}]'
                element = driver.find_element(By.XPATH, element_xpath)
                sub.append((element.text, element_xpath))
                l+=1
            except NoSuchElementException:
                break
        parseLectures(sub, big_categ)
        time.sleep(2)

    if i==0 : 
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
        parseLectures(sub, big_categ)
        time.sleep(2)

    if i==1 : 
        big_categ = "데이터 사이언스"
        sub = []
        l = 1
        while True:
            try:
                element_xpath = f'//*[@id="root"]/div[1]/div[3]/div/div[3]/div[1]/div/form/div[3]/div/div[3]/div/div[3]/div/div[{l}]'
                element = driver.find_element(By.XPATH, element_xpath)
                sub.append((element.text, element_xpath))
                l+=1
            except NoSuchElementException:
                break
        parseLectures(sub, big_categ)
        time.sleep(2)

    if i==2 : 
        big_categ = "컴퓨터 사이언스"
        sub = []
        l = 1
        while True:
            try:
                element_xpath = f'//*[@id="root"]/div[1]/div[3]/div/div[3]/div[1]/div/form/div[3]/div/div[3]/div/div[4]/div/div[{l}]'
                element = driver.find_element(By.XPATH, element_xpath)
                sub.append((element.text, element_xpath))
                l+=1
            except NoSuchElementException:
                break
        parseLectures(sub, big_categ)
        time.sleep(2) 

    if i==3 : 
        big_categ = "프로그래밍 언어"
        sub = []
        l = 1
        while True:
            try:
                element_xpath = f'//*[@id="root"]/div[1]/div[3]/div/div[3]/div[1]/div/form/div[3]/div/div[3]/div/div[5]/div/div[{l}]'
                element = driver.find_element(By.XPATH, element_xpath)
                sub.append((element.text, element_xpath))
                l+=1
            except NoSuchElementException:
                break  
        parseLectures(sub, big_categ)
        time.sleep(2)

driver.quit()
