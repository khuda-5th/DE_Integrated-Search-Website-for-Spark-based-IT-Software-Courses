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


def start_selenium(url):
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
    driver.get(url)
    return driver


# 타겟 요소 찾을 때까지 OR 일정 시간까지 대기 후 클릭
def wait_click_until_located(driver, time, element_type, element):
    WebDriverWait(driver, time).until(
        EC.presence_of_element_located((element_type, element))
    )
    driver.find_element(element_type, element).click()


# 소분류/대분류 정보 수집
def parse_category(driver):
    category_url = {}
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "mobile-main-menu__selector"))
    )
    categories = driver.find_elements(By.CLASS_NAME, "mobile-main-menu__selector")
    for c in categories:
        # 카테고리의 텍스트가 로딩될 때까지 대기
        WebDriverWait(driver, 10).until(lambda x: c.text != "")
        category_url[c.text] = []
        logging.info(f"Category '{c.text}' Found")
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
                logging.info(f"Category '{c.text}: SubCategory '{sub_name}' Found")
    return category_url


# 무한 스크롤
def infinite_scroll(driver):
    while True:
        len_contents = len(
            driver.find_elements(
                By.CSS_SELECTOR, ".infinity-course .course-card__container"
            )
        )
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(driver, 2)
        # headless모드에서는 loading-spinner 기능 못함. 존재하는 강의 컨텐츠의 개수를 기준으로 스크롤.
        new_len_contents = len(
            driver.find_elements(
                By.CSS_SELECTOR, ".infinity-course .course-card__container"
            )
        )
        if len_contents == new_len_contents:
            break
        len_contents = new_len_contents
        return len_contents


# 강의 뱃지
def parse_course_badge(driver, course):
    try:
        course_badge = course.find_element(By.CLASS_NAME, "course-card__badge").text
    except:
        course_badge = ""
    return course_badge


# 강의 제목, 소개글
def parse_course_title_intro(driver, course):
    course_text_element = course.find_element(By.CLASS_NAME, "course-card__text")
    # 제목
    try:
        course_title = course_text_element.find_element(
            By.CLASS_NAME, "course-card__title"
        ).text
    except:
        course_title = ""
        logging.info("Course Title NOT FOUNDED")
    try:
        # 소개글이 화면에 바로 안 보이고 가려져 있어 보이도록 설정하고 추출
        course_intro_element = course_text_element.find_element(
            By.CLASS_NAME, "course-card__content"
        )
        driver.execute_script(
            "arguments[0].style.display='block';", course_intro_element
        )
        course_intro = course_intro_element.text
    except:
        course_intro = ""
        logging.info("Course intro NOT FOUNDED")
    return course_title, course_intro


def parse_course_tags(driver, course):
    try:
        course_tags_elements = course.find_elements(
            By.CSS_SELECTOR, ".course-card__labels li"
        )
        # 해상도에 따라 보이지 않는 태그들까지 추출
        course_tags = [
            driver.execute_script("return arguments[0].textContent;", element)
            for element in course_tags_elements
        ]
    except:
        course_tags = []
        logging.info("Course Tags NOT FOUNDED")
    return course_tags


def parse_course_img(driver, course):
    try:
        course_img = course.find_element(
            By.CLASS_NAME, "course-card__image"
        ).get_attribute("src")
    except:
        course_img = ""
        logging.info("Course Image URL NOT FOUNDED")
    return course_img


def parse_course_url(driver, course):
    try:
        course_detail_url = course.get_attribute("href")
    except:
        course_detail_url = ""
        logging.info("Course Detail URL NOT FOUNDED")
    return course_detail_url


def navigate_course_detail(driver, url):
    driver.get(url)
    try:
        WebDriverWait(driver, 30).until(  # 페이지 로딩 대기
            EC.presence_of_element_located((By.CLASS_NAME, "container"))
        )
    except:
        logging.info("Course Detail Page Loading Fail")


def parse_course_price(driver):
    try:
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
    return regular_price, sale_price


def parse_course_summary(driver):
    summary_list = []
    try:  # 미출시 강의 고려
        summaries = driver.find_elements(By.CLASS_NAME, "fc-list__item")

        for summary in summaries:
            summary_list.append(summary.text)
    except:
        logging.info("Course Summary[fc-list__item] NOT FOUNDED")
    return summary_list


def parse_course_parts(driver):
    parts = []
    try:
        parts_related = driver.find_elements(By.CLASS_NAME, "container__text-content")
        for e in parts_related:
            if e.text[:4] == "Part":
                parts.append(e.text)
    except:
        logging.info("Curriculum Parts Info NOT FOUNDED")
    return parts


def parse_course_accordion(driver):
    accordion_list = []
    try:  ## 미출시 강의 고려
        accordion_titles = driver.find_elements(By.CLASS_NAME, "accordion-tab__title")
        accordion_contents = driver.find_elements(
            By.CLASS_NAME, "accordion-tab__content"
        )

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
            logging.info("Error: Length of accordion title and contents are not same")
    except:
        logging.info("Accordions NOT FOUNDED")
    return accordion_list
