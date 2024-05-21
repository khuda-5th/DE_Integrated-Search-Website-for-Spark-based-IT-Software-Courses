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

def crawl_and_save(driver, url):
    try:
        driver.get(url)
        wait_until_page_loaded(driver)
        close_popup_if_exists(driver)

        try:
            # tag 존재 여부 확인
            special_element_exists = False
            try:
                tag = driver.find_element(By.XPATH, '//*[@id="header"]/div/div[1]/div[2]/div').text
                special_element_exists = True
            except Exception as e:
                tag = ""

            title = driver.find_element(By.XPATH, '//*[@id="header"]/div/div[1]/div[3]/p[1]').text
            lecture_num = driver.find_element(By.XPATH, '//*[@id="header"]/div/div[2]/div[1]/div[2]/div/div').text
            summary = driver.find_element(By.XPATH, '//*[@id="header"]/div/div[1]/div[3]/p[2]').text
            difficulty = driver.find_element(By.XPATH, '//*[@id="header"]/div/div[2]/div[2]/div[2]/div').text
            time = driver.find_element(By.XPATH, '//*[@id="header"]/div/div[2]/div[3]/div[2]/div/div').text
            curriculum = driver.find_element(By.XPATH, '//*[@id="curriculum"]/div[2]/div[2]').text

            # 로드맵 존재 여부 확인
            special_element_exists = False
            try:
                roadmap_e = driver.find_elements(By.CLASS_NAME, 'CommonExploreItem_container__EhGmI')
                roadmaps = []
                for r in roadmap_e:
                    roadmaps.append(r.text)
                special_element_exists = True
            except Exception as e:
                roadmaps = ""

            # 추천 존재 여부 확인
            special_element_exists = False
            try:
                recommend_e = driver.find_elements(By.CLASS_NAME, 'TopicCommonCard_container__w89Rp')
                recommend = []
                for r in recommend_e:
                    recommend.append(r.text)
                special_element_exists = True
            except Exception as e:
                recommend = ""

        except Exception as e:
            print(f"강의 내 정보를 수집하는 중 오류 발생: {e}")
            return None

        lecture_data = {
            "tag": tag,
            "title": title,
            "summary": summary,
            "lecture_num": lecture_num,
            "difficulty": difficulty,
            "time": time,      
            "curriculum": curriculum,
            "roadmaps": roadmaps,
            "recommend": recommend
        }

        return lecture_data

    except Exception as e:
        print(f"URL을 로드하는 중 오류 발생: {e}")
        return None