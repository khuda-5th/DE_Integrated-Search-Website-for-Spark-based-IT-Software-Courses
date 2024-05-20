from codeit_function import *
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

roadmap_url = "https://www.codeit.kr/roadmaps"

options = Options()
driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
driver.get(roadmap_url)

# 전체 데이터를 저장할 리스트
all_data = []

for i in range(2, 3):
    big_categ = driver.find_element(By.XPATH, f'//*[@id="root"]/div[1]/div[3]/div/div[1]/div/div/div/div[{i}]')
    big_categ.click()
    big_categ_name = big_categ.text
    
    # 페이지 로딩 대기
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "CommonExploreItem_outline__mn3kc.CommonExploreItem_hoverable__9MoEj")))

    # 요소를 찾기 위해 XPath 사용
    lectures = driver.find_elements(By.XPATH, "//a[contains(@class, 'CommonExploreItem_outline__mn3kc') and contains(@class, 'CommonExploreItem_hoverable__9MoEj')]")

    hrefs = [l.get_attribute('href') for l in lectures]
    time.sleep(2)

    # 각 URL에 대해 크롤링하여 데이터를 수집
    category_data = {
        "categ": big_categ_name,
        "courses": []
    }
    for url in hrefs:
        course_data = crawl_and_save(url, big_categ_name)
        if course_data:
            category_data["courses"].append(course_data)
    
    # 카테고리 데이터를 전체 데이터에 추가
    all_data.append(category_data)

driver.quit()

# JSON 파일에 저장
with open('codeit_new.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=4)