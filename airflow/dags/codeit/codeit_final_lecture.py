from selenium import webdriver 
from selenium.webdriver.common.by import By  
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
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
            review_num = driver.find_element(By.XPATH,'//*[@id="header"]/div/div[1]/div[3]/div/span').text
            review = driver.find_element(By.CLASS_NAME, 'Carousel_items__xcN45').text

            curriculum = ""
            section_index = 1
            while True:
                try:
                    # 번호와 섹션의 XPath 동적으로 생성
                    number_xpath = f'//*[@id="curriculum"]/div[2]/div[2]/div[{section_index}]/div[1]/div/div[1]/div[1]/span'
                    section_xpath = f'//*[@id="curriculum"]/div[2]/div[2]/div[{section_index}]/div[1]/div/div[1]/div[2]/p[1]'
                    
                    # 요소 찾기
                    number_element = driver.find_element(By.XPATH, number_xpath)
                    section_element = driver.find_element(By.XPATH, section_xpath)
                    
                    # 텍스트 추출
                    number_text = number_element.text
                    section_text = section_element.text
                    
                    curriculum += number_text + "\n"
                    curriculum += section_text +"\n"

                    # 서브섹션 탐색
                    subsection_index = 1
                    while True:
                        try:
                            # 서브섹션의 XPath 동적으로 생성
                            subsection_xpath = f'//*[@id="curriculum"]/div[2]/div[2]/div[{section_index}]/div[2]/div/a[{subsection_index}]/div[2]/p[1]'
                            
                            # 서브섹션 요소 찾기
                            subsection_element = driver.find_element(By.XPATH, subsection_xpath)
                            
                            # 서브섹션 텍스트 추출
                            subsection_text = subsection_element.text
                            
                            # 데이터 저장
                            curriculum += subsection_text +"\n"
                            
                            subsection_index += 1
                        
                        except Exception as e:
                            # 더 이상 서브섹션이 없으면 루프 종료
                            break
                    
                    section_index += 1
                except Exception as e:
                    # 더 이상 섹션이 없으면 루프 종료
                    break
                        


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
            "review_num": review_num,  
            "review": review,
            "curriculum": curriculum,
            "roadmaps": roadmaps,
            "recommend": recommend,
            "link": url
        }

        return lecture_data

    except Exception as e:
        print(f"URL을 로드하는 중 오류 발생: {e}")
        return None