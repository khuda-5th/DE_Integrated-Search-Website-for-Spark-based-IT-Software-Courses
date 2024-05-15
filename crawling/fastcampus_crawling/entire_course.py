from utilities import *
from course_items import *

start_time = datetime.now()
formatted_time = start_time.strftime("%y%m%d%H%M")
LOG_NAME = f"{formatted_time}_fastcampus.log"
JSON_NAME = f"{formatted_time}_fastcampus.json"

logging.basicConfig(
    level=logging.INFO,
    filename=f"logs/{LOG_NAME}",
    filemode="w",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logging.info("Crawl Entire Courses Start")
###############################################################################################

driver = start_selenium("https://fastcampus.co.kr/categories")
# 메뉴 버튼 클릭
wait_click_until_located(driver, 1, By.CLASS_NAME, "header-new__mobile-menu-icon")
# 대분류/소분류 정보 수집
category_url = parse_category(driver)
# 내보낼 데이터
output = {"categories": []}
# 소분류 페이지로 이동
for category in list(category_url.keys()):
    # CategoryItem 생성
    category_item = CategoryItem(category)
    for sub_category, sub_url in category_url[category]:
        # SubcategoryItem 생성
        subcategory_item = SubCategoryItem(sub_category)
        driver.get(sub_url)
        logging.info(
            "========================================================================================================"
        )
        logging.info(f"{category}: {sub_category} Start")
        count_contents = infinite_scroll(driver)
        logging.info(f"{category}: {sub_category} Count-{count_contents}")

        # 강의 요소들
        courses = driver.find_elements(
            By.CSS_SELECTOR, ".infinity-course .course-card__container"
        )
        for course in courses:
            course_item = CourseItem()
            # 강의 뱃지 (전체오픈, 사전예약 등등..)
            course_badge = parse_course_badge(driver, course)
            course_item.badge = course_badge
            # 강의 제목
            course_title, course_intro = parse_course_title_intro(driver, course)
            course_item.title = course_title
            course_item.intro = course_intro
            # 강의 태그
            course_tags = parse_course_tags(driver, course)
            course_item.tags = course_tags
            # 강의 이미지 URL
            course_img = parse_course_img(driver, course)
            course_item.course_img = course_img
            # 강의 세부 페이지 URL
            course_url = parse_course_url(driver, course)
            course_item.course_url = course_url
            # SubcategoryItem에 현재 Course 추가
            subcategory_item.courses.append(course_item)
        # 각 강의별 상세 페이지 이동
        cnt = 0
        for course in subcategory_item.courses:
            cnt += 1
            logging.info(f"{category}: {sub_category} {cnt}. {course.title} Start")
            navigate_course_detail(driver, course.course_url)
            # 가격
            regular_price, sale_price = parse_course_price(driver)
            course.regular_price = regular_price
            course.sale_price = sale_price
            # 강의 요약 및 간단 소개
            course_summary = parse_course_summary(driver)
            course.summary = course_summary
            # 강의 Part 정보
            course_parts = parse_course_parts(driver)
            course.parts = course_parts
            # 강의 기본 정보, 특징, 커리큘럼 등의 정보
            course_accordion = parse_course_accordion(driver)
            course.accordion = course_accordion
        # CategoryItem에 SubCategory 정보 추가
        category_item.sub_categories.append(subcategory_item)

        """   테스트용 임시저장   """
        sub_category_json = sub_category.replace("/", "_")
        with open(f"tmp/{sub_category_json}.json", "w", encoding="utf-8") as file:
            json.dump(subcategory_item.to_dict(), file, ensure_ascii=False, indent=4)
        """                   """
    # 최종 데이터에 category_item 추가
    output["categories"].append(category_item.to_dict())

# 파일 출력
with open(f"outputs/{JSON_NAME}", "w", encoding="utf-8") as file:
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
