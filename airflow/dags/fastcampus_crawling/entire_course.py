from fastcampus_selenium_driver import *
from course_items import *
from logger import *
import os
import json
from datetime import datetime

def save_json(path, file_name, data):
    if not os.path.exists(path):
        os.makedirs(path)
    with open(f"{path}/{file_name}", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# 로그 디렉토리 생성
log_dir = "entire_logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

start_time = datetime.now()
formatted_time = start_time.strftime("%y%m%d%H%M")
output_formatted = start_time.strftime("%y%m%d")
LOG_NAME = f"{formatted_time}_fastcampus.log"
OUTPUT_NAME = f"{output_formatted}_fastcampus_entire"

# 로깅 설정
logger = setup_logging(log_dir, LOG_NAME)

logging.info("Crawl Entire Courses Start")
###################################################################################################################

driver = FastcampusSeleniumDriver("https://fastcampus.co.kr/categories")
# 메뉴 버튼 클릭
driver.wait_click_until_located(10, By.CLASS_NAME, "header-new__mobile-menu-icon")
# 대분류/소분류 정보 수집
category_url = driver.parse_category()
# 내보낼 데이터
output = FastcampusItem()
# 소분류 페이지로 이동
for category in list(category_url.keys()):
    # CategoryItem 생성
    category_item = CategoryItem(category)
    for sub_category, sub_url in category_url[category]:
        # SubcategoryItem 생성
        subcategory_item = SubCategoryItem(sub_category)
        driver.driver.get(sub_url)
        logging.info(
            "========================================================================================================"
        )
        logging.info(f"{category}: {sub_category} Start")
        count_contents = driver.infinite_scroll()
        logging.info(f"{category}: {sub_category} Count-{count_contents}")

        # 강의 요소들
        courses = driver.driver.find_elements(
            By.CSS_SELECTOR, ".infinity-course .course-card__container"
        )
        for course in courses:
            course_item = CourseItem()
            # 강의 뱃지 (전체오픈, 사전예약 등등..)
            course_badge = driver.parse_course_badge(course)
            course_item.badge = course_badge
            # 강의 제목
            course_title, course_intro = driver.parse_course_title_intro(course)
            course_item.title = course_title
            course_item.intro = course_intro
            # 강의 태그
            course_tags = driver.parse_course_tags(course)
            course_item.tags = course_tags
            # 강의 이미지 URL
            course_img = driver.parse_course_img(course)
            course_item.course_img = course_img
            # 강의 세부 페이지 URL
            course_url = driver.parse_course_url(course)
            course_item.course_url = course_url
            # SubcategoryItem에 현재 Course 추가
            subcategory_item.courses.append(course_item)
        # 각 강의별 상세 페이지 이동
        for course in subcategory_item.courses:
            logging.info(f"{category}: {sub_category} - {course.title} Start")
            driver.navigate_course_detail(course.course_url)
            # 가격
            regular_price, sale_price = driver.parse_course_price()
            course.regular_price = regular_price
            course.sale_price = sale_price
            # 강의 요약 및 간단 소개
            course_summary = driver.parse_course_summary()
            course.summary = course_summary
            # 강의 Part 정보
            course_parts = driver.parse_course_parts()
            course.parts = course_parts
            # 강의 기본 정보, 특징, 커리큘럼 등의 정보
            course_accordion = driver.parse_course_accordion()
            course.accordion = course_accordion
        # CategoryItem에 SubCategory 정보 추가
        category_item.sub_categories.append(subcategory_item)

    # # 카테고리 json 저장
    # save_json(
    #     f"entire_outputs",
    #     f"{OUTPUT_NAME}_{category_item.category_name.replace('/', '_')}.json",
    #     category_item.to_dict(),
    # )
    # logging.info(
    #     f"Save Json 'entire_outputs/{category_item.category_name}/{OUTPUT_NAME}_{category_item.category_name}.json'"
    # )
    logging.info(
        "========================================================================================================"
    )
    # 최종 데이터에 category_item 추가
    output.categories.append(category_item)
###################################################################################################################

# 파일 저장
save_json("~/data/fastcampus/entire/raw", f"{OUTPUT_NAME}.json", output.to_dict())
logging.info(f"Save Json '~/data/fastcampus/entire/raw/{OUTPUT_NAME}_all.json'")

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

driver.driver.quit()
