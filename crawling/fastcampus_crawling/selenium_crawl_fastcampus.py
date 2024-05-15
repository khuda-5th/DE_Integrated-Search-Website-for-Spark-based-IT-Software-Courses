from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import logging
from datetime import datetime

start_time = datetime.now()
formatted_time = start_time.strftime("%y%m%d%H%M")
log_file_name = f"{formatted_time}_fastcampus.log"
json_file_name = f"{formatted_time}_fastcampus.json"
logging.basicConfig(
    level=logging.INFO,
    filename=f"logs/{log_file_name}",
    filemode="w",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

options = webdriver.ChromeOptions()
options.add_argument("--window-size=400,1200")
options.add_argument("--headless")  # 브라우저 UI 없이 실행
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
)  # 에이전트 지정

# 버전에 맞는 크롬드라이버 설치 후 실행
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()), options=options
)

url = "https://fastcampus.co.kr/categories"
driver.get(url)

# 메뉴 버튼 클릭
menu_button = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CLASS_NAME, "header-new__mobile-menu-icon"))
)
menu_button.click()

# 대분류/소분류 정보 수집
category_url = {}  # {대분류: (소분류: 소분류URL)}
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CLASS_NAME, "mobile-main-menu__selector"))
)
categories = driver.find_elements(By.CLASS_NAME, "mobile-main-menu__selector")
for c in categories:
    WebDriverWait(driver, 10).until(
        lambda x: c.text != ""
    )  # 카테고리의 텍스트가 로딩될 때까지 대기
    category_url[c.text] = []
    c.click()
    time.sleep(0.2)
    sub_menus = driver.find_elements(By.CLASS_NAME, "mobile-sub-menu__link")
    for s in sub_menus:
        sub_name = s.text
        url = s.get_attribute("href")
        if sub_name[-6:] == "전체보기 >":  # 카테고리별 전체보기 제외
            continue
        if "category" in url:  # 캠프 같은 요소들 수집 제외
            category_url[c.text].append((sub_name, url))

output = {"category": []}  # 내보낼 데이터
for category in list(category_url.keys()):
    sub_data_info_list = []
    for sub_category, sub_url in category_url[category]:
        sub_data = {"sub_category_name": sub_category, "courses": []}
        driver.get(sub_url)  # 소분류 페이지로 이동
        logging.info(
            "========================================================================================================"
        )
        logging.info(f"{category}: {sub_category} Start")

        # 무한 스크롤 시작
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            count_contents = len(
                driver.find_elements(
                    By.CSS_SELECTOR, ".infinity-course .course-card__container"
                )
            )
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # 요소가 로드될 때까지 대기 (로딩 스피너가 사라질 때까지)
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element((By.CSS_SELECTOR, ".loading-spinner"))
            )
            """
            # 스크롤 이벤트 후에 새 높이를 측정
            time.sleep(1)  # 잠시 대기 후 새 높이 측정
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            """
            time.sleep(2)
            new_count_contents = len(  # headless모드에서는 loading-spinner 기능 못함. 존재하는 강의 컨텐츠의 개수를 기준으로 스크롤.
                driver.find_elements(
                    By.CSS_SELECTOR, ".infinity-course .course-card__container"
                )
            )
            if count_contents == new_count_contents:
                break
            count_contents = new_count_contents
        # 무한 스크롤 끝
        logging.info(f"{category}: {sub_category} Count-{count_contents}")

        # 강의 요소들
        courses = driver.find_elements(
            By.CSS_SELECTOR, ".infinity-course .course-card__container"
        )
        # 강의 뱃지 (전체오픈, 사전예약 등등...)

        # 소분류 내 개별 강의들
        for course in courses:
            course_info = {}
            try:  # 뱃지가 없는 항목들 고려
                course_badge = course.find_element(
                    By.CLASS_NAME, "course-card__badge"
                ).text
            except:
                course_badge = ""
            # 강의 제목, 소개글
            course_text_element = course.find_element(
                By.CLASS_NAME, "course-card__text"
            )
            try:
                course_title = course_text_element.find_element(
                    By.CLASS_NAME, "course-card__title"
                ).text
            except:
                course_title = ""
                logging.info("Course Title NOT FOUNDED")
            try:
                # 소개글이 화면에 바로 안 보이고 가려져 있어 보이도록 설정하고 텍스트 추출
                course_content_element = course_text_element.find_element(
                    By.CLASS_NAME, "course-card__content"
                )
                driver.execute_script(
                    "arguments[0].style.display='block';", course_content_element
                )
                course_content = course_content_element.text
            except:
                course_content = ""
                logging.info("Course Content NOT FOUNDED")
            # 강의 태그: 해상도에 따라 보이지 않는 태그들까지 추출
            try:
                course_tags_elements = course.find_elements(
                    By.CSS_SELECTOR, ".course-card__labels li"
                )
                course_tags = [
                    driver.execute_script("return arguments[0].textContent;", element)
                    for element in course_tags_elements
                ]
            except:
                course_tags = []
                logging.info("Course Tags NOT FOUNDED")

            # 강의 이미지 URL
            try:
                course_img = course.find_element(
                    By.CLASS_NAME, "course-card__image"
                ).get_attribute("src")
            except:
                course_img = ""
                logging.info("Course Image URL NOT FOUNDED")
            # 강의 상세 페이지 URL

            try:
                course_detail_url = course.get_attribute("href")
            except:
                course_detail_url = ""
                logging.info("Course Detail URL NOT FOUNDED")
            course_info = {
                "title": course_title,
                "intro": course_content,
                "badge": course_badge,
                "tags": course_tags,
                "course_img": course_img,
                "course_url": course_detail_url,
                # "regular_price": regular_price,
                # "sale_price": sale_price,
                # "summary": accordion_list,
            }
            sub_data["courses"].append(course_info)

        for i in range(len(sub_data["courses"])):
            # 현재 소분류 강의들 상세 페이지로 이동
            driver.get(sub_data["courses"][i]["course_url"])
            logging.info(
                f"{category}: {sub_category} {i+1}. {sub_data['courses'][i]['title']}"
            )
            try:
                WebDriverWait(driver, 30).until(  # 페이지 로딩 대기
                    EC.presence_of_element_located((By.CLASS_NAME, "container"))
                )
            except:
                sub_data["courses"][i]["regular_price"] = ""
                sub_data["courses"][i]["sale_price"] = ""
                sub_data["courses"][i]["summary"] = ""
                logging.info("Course Detail Page Loading Fail")
                continue

            # 가격
            try:  # 출시가 안 돼서 가격 정보가 없는 강의들이 있음

                price_card = (
                    WebDriverWait(driver, 7)
                    .until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div.hbox.payment-card.has-installment")
                        )
                    )
                    .text.split("\n")
                )
                regular_price = ""
                sale_price = ""
                for j in range(len(price_card)):
                    if price_card[j] == "정가":
                        regular_price = price_card[j + 1]
                    elif price_card[j] == "현재 판매가":
                        sale_price = price_card[j + 1]
            except:
                regular_price = ""
                sale_price = ""
                logging.info("Price Info NOT FOUNDED")

            # 강의 요약/간단 소개 같은 거
            summary_list = []
            try:  # 미출시 강의 고려
                summaries = driver.find_elements(By.CLASS_NAME, "fc-list__item")

                for summary in summaries:
                    summary_list.append(summary.text)
            except:
                logging.info("summary[fc-list__item] NOT FOUNDED")
            # 강의 기본 정보, 강의 특징, 커리큘럼 순서 등의 내용들
            # 얘네는 강의별로 항목이 없거나, 다른 속성의 내용을 담고 있을 수도 있음. 강의별로 확인 필요

            try:  ## 미출시 강의 고려
                accordion_titles = driver.find_elements(
                    By.CLASS_NAME, "accordion-tab__title"
                )
                accordion_contents = driver.find_elements(
                    By.CLASS_NAME, "accordion-tab__content"
                )
                accordion_list = []

                if len(accordion_titles) == len(accordion_contents):
                    for j in range(len(accordion_titles)):
                        # 감춰져 있는 content 드러내기
                        driver.execute_script(
                            "arguments[0].style.display='block';", accordion_contents[j]
                        )
                        accordion_list.append(
                            (
                                accordion_titles[j].text,
                                accordion_contents[j].text,
                            )
                        )
                else:
                    logging.info(
                        "Error: Length of accordion title and contents are not same"
                    )
                # 강의 커리큘럼에서, Part1, Part2, 등등 얘네들을 뽑을 방법이 안보임. <- 01, 02, 03, 01 ... 이렇게 구분되는 거로 자체 처리하면 될 듯 싶음
            except:
                accordion_list = []
                logging.info("Accordions NOT FOUNDED")

            # 커리큘럼 Part 정보
            parts = []
            try:
                parts_related = driver.find_elements(
                    By.CLASS_NAME, "container__text-content"
                )
                for e in parts_related:
                    if e.text[:4] == "Part":
                        parts.append(e.text)
            except:
                logging.info("Curriculum Parts Info NOT FOUNDED")

            """ 강의 상세페이지 전체 text
            entire_text_elements = driver.find_elements(By.CLASS_NAME, 'container')
            for i in range(len(entire_text_elements)):
                logging.info(entire_text_elements[i].text)
            """
            sub_data["courses"][i]["regular_price"] = regular_price
            sub_data["courses"][i]["sale_price"] = sale_price
            sub_data["courses"][i]["summary"] = accordion_list
            sub_data["courses"][i]["parts"] = parts
            sub_data_info_list.append(sub_data)

        # 테스트용 임시저장
        sub_category_json = sub_category.replace("/", "_")
        with open(f"tmp/{sub_category_json}.json", "w", encoding="utf-8") as file:
            json.dump(sub_data, file, ensure_ascii=False, indent=4)
        #################

    output["category"].append(
        {"category_name": category, "sub_category": sub_data_info_list}
    )

with open(f"outputs/{json_file_name}", "w", encoding="utf-8") as file:
    json.dump(output, file, ensure_ascii=False, indent=4)

end_time = datetime.now()
time_spent = end_time - start_time

minutes = time_spent.seconds // 60
hours = minutes // 60
minutes = minutes % 60

if hours > 0:
    time_str = f"{hours}h {minutes}min"
else:
    time_str = f"{minutes}min"

logging.info(f"Completed at {end_time.strftime('%y%m%d%H%M')}")
logging.info(f"Total {time_str}")
