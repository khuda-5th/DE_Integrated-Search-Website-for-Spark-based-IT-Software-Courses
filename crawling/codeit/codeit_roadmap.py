from selenium import webdriver 
from selenium.webdriver.common.by import By  
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

def close_popup_if_exists(driver):
    try:
        popup_close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'PopupCloseBtn__CloseIcon-ch-front__sc-14jjsiy-0'))
        )
        popup_close_button.click()
        print("첫 번째 팝업 창을 닫았습니다.")
    except Exception as e:
        print("첫 번째 팝업 창이 없습니다. 또는 팝업 창을 닫는 중 오류 발생:", str(e))
    
    try:
        popup_close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'InnerIconstyled__Icon-ch-front__sc-197h5bb-0'))
        )
        popup_close_button.click()
        print("두 번째 팝업 창을 닫았습니다.")
    except Exception as e:
        print("두 번째 팝업 창이 없습니다. 또는 팝업 창을 닫는 중 오류 발생:", str(e))

def wait_until_page_loaded(driver):
    timeout = 30
    WebDriverWait(driver, timeout).until(
        lambda x: x.execute_script("return document.readyState == 'complete'")
    )
    print("*************페이지 로드 완료***************")

def crawl_and_save(url, big_categ_name):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get(url)

    wait_until_page_loaded(driver)
    close_popup_if_exists(driver)

    try:
        title = driver.find_element(By.XPATH, '//*[@id="roadmapDetailContainer"]/div[1]/div/div/div/div[1]/h1').text
        avg_time = driver.find_element(By.XPATH, '//*[@id="roadmapDetailContainer"]/div[1]/div/div/div/div[2]/div[3]').text
        lecture_num = driver.find_element(By.XPATH, '//*[@id="roadmapDetailContainer"]/div[1]/div/div/div/div[2]/div[1]').text
        summary = driver.find_element(By.XPATH, '//*[@id="introduce"]/div[2]/div/div[1]/div/p[1]').text
        appeal_e = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'RoadmapAppeals_contents__eMl4t')))
        appeal = appeal_e.text
        who_e = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'RoadmapTargets_targets__oUHBG')))
        who = who_e.text
        example_e = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'RoadmapProjectIntroduce_projects__jW1J5')))
        example = example_e.text
        star = driver.find_element(By.XPATH, '//*[@id="reviews"]/div/div[1]/p[1]').text
        review_element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'RoadmapBestReviews_reviews__1g1rx')))
        review = review_element.text
        section_e = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'RoadmapDetailCurriculum_steps__qoFzf')))
        section = section_e.text
    except Exception as e:
        print(f"정보를 수집하는 중 오류 발생: {e}")
        driver.quit()
        return None

    course_data = {
        "title": title,
        "avg_time": avg_time,
        "lecture_num": lecture_num,
        "summary": summary,
        "appeal": appeal,
        "who": who,
        "example": example,
        "star": star,
        "section": section,
        "review": review
    }

    driver.quit()
    return course_data
