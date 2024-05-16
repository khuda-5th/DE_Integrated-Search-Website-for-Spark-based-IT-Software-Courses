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


class FastcampusSeleniumDriver:
    def __init__(self, url):
        self.url = url
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--window-size=400,1200")
        # self.options.add_argument("--headless")  # 브라우저 UI 없이 실행
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        )  # 에이전트 지정
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=self.options
        )
        self.driver.get(self.url)

    def wait_until_located(self, time, element_type, element):
        WebDriverWait(self.driver, time).until(
            EC.presence_of_element_located((element_type, element))
        )

    def wait_click_until_located(self, time, element_type, element):
        WebDriverWait(self.driver, time).until(
            EC.presence_of_element_located((element_type, element))
        )
        self.driver.find_element(element_type, element).click()

    def parse_category(self):
        category_url = {}
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "mobile-main-menu__selector")
            )
        )
        categories = self.driver.find_elements(
            By.CLASS_NAME, "mobile-main-menu__selector"
        )
        for c in categories:
            WebDriverWait(self.driver, 10).until(lambda x: c.text != "")
            category_url[c.text] = []
            logging.info(f"Category '{c.text}' Found")
            c.click()
            time.sleep(0.2)
            sub_menus = self.driver.find_elements(
                By.CLASS_NAME, "mobile-sub-menu__link"
            )
            for s in sub_menus:
                sub_name = s.text
                url = s.get_attribute("href")
                if sub_name[-6:] == "전체보기 >":
                    continue
                if "category" in url:
                    category_url[c.text].append((sub_name, url))
                    logging.info(f"Category '{c.text}: SubCategory '{sub_name}' Found")
        return category_url

    def infinite_scroll(self):
        len_contents = len(
            self.driver.find_elements(
                By.CSS_SELECTOR, ".infinity-course .course-card__container"
            )
        )
        while True:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(2)
            new_len_contents = len(
                self.driver.find_elements(
                    By.CSS_SELECTOR, ".infinity-course .course-card__container"
                )
            )
            if len_contents == new_len_contents:
                break
            len_contents = new_len_contents
        return len_contents

    def parse_course_badge(self, course):
        try:
            course_badge = course.find_element(By.CLASS_NAME, "course-card__badge").text
        except:
            course_badge = ""
        return course_badge

    def parse_course_title_intro(self, course):
        course_text_element = course.find_element(By.CLASS_NAME, "course-card__text")
        try:
            course_title = course_text_element.find_element(
                By.CLASS_NAME, "course-card__title"
            ).text
        except:
            course_title = ""
            logging.info("Course Title NOT FOUNDED")
        try:
            course_intro_element = course_text_element.find_element(
                By.CLASS_NAME, "course-card__content"
            )
            self.driver.execute_script(
                "arguments[0].style.display='block';", course_intro_element
            )
            course_intro = course_intro_element.text
        except:
            course_intro = ""
            logging.info("Course intro NOT FOUNDED")
        return course_title, course_intro

    def parse_course_tags(self, course):
        try:
            course_tags_elements = course.find_elements(
                By.CSS_SELECTOR, ".course-card__labels li"
            )
            course_tags = [
                self.driver.execute_script("return arguments[0].textContent;", element)
                for element in course_tags_elements
            ]
        except:
            course_tags = []
            logging.info("Course Tags NOT FOUNDED")
        return course_tags

    def parse_course_img(self, course):
        try:
            course_img = course.find_element(
                By.CLASS_NAME, "course-card__image"
            ).get_attribute("src")
        except:
            course_img = ""
            logging.info("Course Image URL NOT FOUNDED")
        return course_img

    def parse_course_url(self, course):
        try:
            course_detail_url = course.get_attribute("href")
        except:
            course_detail_url = ""
            logging.info("Course Detail URL NOT FOUNDED")
        return course_detail_url

    def navigate_course_detail(self, url):
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "container"))
            )
        except:
            logging.info("Course Detail Page Loading Fail")

    def parse_course_price(self):
        try:
            price_card = (
                WebDriverWait(self.driver, 7)
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

    def parse_course_summary(self):
        summary_list = []
        try:
            summaries = self.driver.find_elements(By.CLASS_NAME, "fc-list__item")
            for summary in summaries:
                summary_list.append(summary.text)
        except:
            logging.info("Course Summary[fc-list__item] NOT FOUNDED")
        return summary_list

    def parse_course_parts(self):
        parts = []
        try:
            parts_related = self.driver.find_elements(
                By.CLASS_NAME, "container__text-content"
            )
            for e in parts_related:
                if e.text[:4] == "Part":
                    parts.append(e.text)
        except:
            logging.info("Curriculum Parts Info NOT FOUNDED")
        return parts

    def parse_course_accordion(self):
        accordion_list = []
        try:
            accordion_titles = self.driver.find_elements(
                By.CLASS_NAME, "accordion-tab__title"
            )
            accordion_contents = self.driver.find_elements(
                By.CLASS_NAME, "accordion-tab__content"
            )
            if len(accordion_titles) == len(accordion_contents):
                for j in range(len(accordion_titles)):
                    self.driver.execute_script(
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
        except:
            logging.info("Accordions NOT FOUNDED")
        return accordion_list

    def parse_new_courses(self):
        new_courses = self.driver.find_elements(By.CLASS_NAME, "container__column")
        return new_courses
