from fastcampus_selenium_driver import *
from course_items import *
from logger import *
import os


def save_json(path, file_name, data):
    if not os.path.exists(path):
        os.makedirs(path)
    with open(f"{path}/{file_name}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


log_dir = "new_logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

start_time = datetime.now()
formatted_time = start_time.strftime("%y%m%d%H%M")
LOG_NAME = f"{formatted_time}_fastcampus_new.log"
OUTPUT_NAME = f"{formatted_time}_fastcampus_new"

# 로깅 설정
logger = setup_logging(log_dir, LOG_NAME)
logging.info("Crawl New Courses Start")
###################################################################################################################
url = "https://fastcampus.co.kr/new"
driver = FastcampusSeleniumDriver(url)

# 신규 강의들
time.sleep(10)
new_courses_elements = driver.parse_new_courses()
new_course_items = NewCourseItems()
cnt = 0
for new_course_element in new_courses_elements:
    new_course_item = NewCourseItem()
    try:
        course_url = new_course_element.find_element(By.TAG_NAME, "a").get_attribute(
            "href"
        )
        new_course_img = new_course_element.find_element(
            By.TAG_NAME, "img"
        ).get_attribute("src")
        # 강의 이외의 요소 예외 처리
        if "category" not in course_url and "new" not in course_url:
            # CourseItem에 데이터 추가
            new_course_item.course_url = course_url
            new_course_item.new_course_img = new_course_img
            # NewCourseItems에 데이터 추가
            new_course_items.new_courses.append(new_course_item)
            cnt += 1
            logging.info(f"New Course: {cnt}. {course_url} Found")
        else:
            pass
    except:
        pass

cnt = 1
for course in new_course_items.new_courses:
    # 강의 세부 페이지 이동
    driver.driver.get(course.course_url)
    logging.info(f"New Course {cnt}. {course.course_url} Start")
    # 제목
    try:
        course_title = driver.driver.find_element(By.CLASS_NAME, "product-title").text
        course.title = course_title
    except:
        try:
            course_title = driver.driver.find_element(By.TAG_NAME, "b").text
            course.title = course_title
        except:
            course_title = ""
            logging.info("Course Title NOT FOUNDED")
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
    cnt += 1

# 강의 제목으로 검색
cnt = 1
for course in new_course_items.new_courses:
    course_title = course.title
    search_keyword = course_title
    search_url = f"https://fastcampus.co.kr/search?keyword={search_keyword}."

    driver.driver.get(search_url)
    logging.info(f"Search Course {cnt}. {course_title}")
    time.sleep(5)
    target_course = driver.driver.find_element(By.CLASS_NAME, "course-card__container")
    # 혹시 몰라서 강의 제목 다시 지정 (소개글 포함)
    course_title, course_intro = driver.parse_course_title_intro(target_course)
    # 강의 뱃지
    course_badge = driver.parse_course_badge(target_course)
    # 강의 이미지
    course_img = driver.parse_course_img(target_course)
    # 강의 태그들
    course_tags = driver.parse_course_tags(target_course)
    # Item에 추가
    course.badge = course_badge
    course.tags = course_tags
    course.title = course_title
    course.intro = course_intro
    course.course_img = course_img
    cnt += 1


###################################################################################################################
save_json("new_outputs", OUTPUT_NAME, new_course_items.to_dict())

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
