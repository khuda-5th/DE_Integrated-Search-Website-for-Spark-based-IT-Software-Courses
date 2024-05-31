import subprocess

# pip install 명령어 실행
subprocess.run(["pip3", "install", "psycopg2-binary"])
subprocess.run(["pip3", "install", "pyspark"])
subprocess.run(["pip3", "install", "python-dotenv"])

from pyspark.sql.functions import explode, trim, regexp_extract, array_join, col, regexp_replace, concat_ws, split, udf, lower, size, lit, monotonically_increasing_id, lag, when, row_number, rand, substring
from pyspark.sql.window import Window
from pyspark.sql import SparkSession, Row
from utilities import *

from dotenv import load_dotenv
import os

import psycopg2

load_dotenv()

spark = (
    SparkSession.builder.appName("postgresql session")
    .config("spark.jars.packages", "org.postgresql:postgresql:42.2.18")
    .getOrCreate()
)

# JSON 파일 읽기
df = spark.read.option("multiline", "true").json("datasets/240524_codeit_final.json")

# COURSE 테이블에 삽입할 정보를 담은 df
df_course = df.withColumn("sub_categs", explode(col("sub_categs"))) \
                .withColumn("lectures", explode(col("sub_categs.lectures"))) \
                .select(
                col("big_categ").alias("category_name"),
                col("sub_categs.sub_categ").alias("subcategory_name"),
                col("lectures.title").alias("course_title"),
                col("lectures.summary").alias("summary"),
                col("lectures.lecture_num").alias("num_of_lecture"),
                col("lectures.link").alias("url")
                ) \
                .dropna()

# num_of_lecture에서 숫자 정보만 추출
df_course = df_course.withColumn("num_of_lecture", regexp_extract(col("num_of_lecture"), "\\d+", 0).cast("int")) 
df_course = df_course.dropDuplicates(["url"])

df_course.show()

# 데이터베이스 정보 설정
db_props = {
    "driver": "org.postgresql.Driver",
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}
# 데이터베이스 URL 설정
db_url = os.getenv("DB_URL")

# section, review에 course_id 매핑
df_sectionInfo = df.withColumn("sub_categs", explode(col("sub_categs"))) \
                .withColumn("lectures", explode(col("sub_categs.lectures"))) \
                .select(
                    col("lectures.link").alias("url"),
                    col("lectures.curriculum").alias("curriculum")
                ) \
                .dropna()

df_reviewInfo = df.withColumn("sub_categs", explode(col("sub_categs"))) \
                .withColumn("lectures", explode(col("sub_categs.lectures"))) \
                .select(
                    col("lectures.link").alias("url"),
                    col("lectures.review").alias("review_info")
                ) \
                .dropna()

df_sectionInfo.show(truncate=True)
df_reviewInfo.show()

# df
df_sectionInfo_withID = df_sectionInfo.withColumn(
    "curriculum",
    regexp_replace(col("curriculum"), r'^\n+', '')
)

df_parsed = df_sectionInfo.withColumn(
    "section_split",
    split(col("curriculum"), r'\n(?=\d+\n)')
)

df_exploded = df_parsed.withColumn(
    "section",
    explode(col("section_split"))
).filter(trim(col("section")) != "")

df_exploded = df_exploded.withColumn(
    "section_num",
    regexp_extract(col("section"), r'^(\d+)', 1)
).withColumn(
    "section_title",
    regexp_extract(col("section"), r'^\d+\n([^\n]+)', 1)
)

df_exploded = df_exploded.withColumn(
    "subsection",
    split(
        regexp_replace(col("section"), r'^\d+\n[^\n]+\n', ''),
        '\n'
    )
).withColumn(
    "subsection",
    explode(col("subsection"))
).filter(trim(col("subsection")) != "")

df_result = df_exploded.select(
    col("url"),
    col("section_num").cast("int"),
    col("section_title").alias("section_name"),
    col("subsection").alias("subsection_name")
).orderBy("url", "section_num")

windowSpec = Window.partitionBy("url", "section_num").orderBy("subsection_name")

df_result_with_subsection_num = df_result.withColumn(
    "subsection_num",
    row_number().over(windowSpec)
)

SECTION_SUBSECTION = df_result_with_subsection_num.select("url", "section_num", "section_name","subsection_num", "subsection_name")

SECTION_SUBSECTION.show(truncate=True)

# 리뷰 분리
df_reviews_split = df_reviewInfo.withColumn(
    "review_info",
    explode(split(col("review_info"), r'\n(?=\w+\n)'))
).filter(trim(col("review_info")) != "")

# 유저 이름과 리뷰 분리, 리뷰만 선택
df_reviews_cleaned = df_reviews_split.withColumn(
    "review_info",
    regexp_extract(col("review_info"), r'^\w+\n(.*)', 1)
).filter(trim(col("review_info")) != "")

# 필요한 컬럼 선택 및 정렬
df_reviews_result = df_reviews_cleaned.select(
    col("url"),
    col("review_info").alias("summary")
).orderBy("url")

# 윈도우 함수 정의
window_spec = Window.partitionBy("url").orderBy(rand())

# 각 course_id 당 3개의 랜덤한 리뷰 선택
REVIEW_SUMMARY = df_reviews_result.withColumn(
    "rank",
    row_number().over(window_spec)
).filter(col("rank") <= 3).drop("rank").distinct()


# 결과 출력
REVIEW_SUMMARY.show(truncate=False)

# DB 파트
COURSE = df_course

unique_category = COURSE.select("category_name").distinct()
unique_subcategory = COURSE.select("subcategory_name", "category_name").distinct()

# 데이터베이스 정보 설정
db_props = {
    "driver": "org.postgresql.Driver",
    "user": "khudade",
    "password": "khudade"
}

# 데이터베이스 URL 설정
db_url = "jdbc:postgresql://54.180.100.57:5432/lecture_db"

get_category_query = f"(SELECT platform_id, category_id, category_name FROM CATEGORY WHERE platform_id={PLATFORM_ID}) AS category_subquery"
CATEGORY_LOADED = spark.read.jdbc(
    url=db_url, table=get_category_query, properties=db_props
)

# 기존 CATEGORY 테이블에 패스트캠퍼스 플랫폼으로 존재하던 category_id만 가져오는 작업
category_ids = [
    row.category_id
    for row in CATEGORY_LOADED.select("category_id").distinct().collect()
]
# 해당 플랫폼의 CATEGORY 테이블이 비었을 경우 현재 카테고리들 삽입 후 다시 가져옴
if not category_ids:
    unique_category.foreachPartition(
        lambda partition: insert_new_categories(partition, db_props, db_url)
    )
    category_ids = [
        row.category_id
        for row in CATEGORY_LOADED.select("category_id").distinct().collect()
    ]


category_ids_str = ",".join([str(id) for id in category_ids])

# 위에서 조회한 category_id를 가진 subcateory들만 가져오기
get_subcategory_query = f"(SELECT subcategory_id, subcategory_name, category_id FROM SUBCATEGORY WHERE category_id IN ({category_ids_str})) AS subcategory_subquery"


SUBCATEGORY_LOADED = spark.read.jdbc(
    url=db_url, table=get_subcategory_query, properties=db_props
)

# platform_id가 같은 category만 불러온 테이블에서, category_name을 기준으로 식별하여 기존에 없던 category만 남긴다.
filtered_category = unique_category.join(
    CATEGORY_LOADED, on=["category_name"], how="leftanti"
)

# DB에 없던 카테고리 삽입
filtered_category.foreachPartition(
    lambda partition: insert_new_categories(partition, db_props, db_url)
)

# category_id, subcategory_name으로 식별하여 기존에 없던 subcategory만 남긴다.
unique_subcategory_with_id = unique_subcategory.join(
    CATEGORY_LOADED, on=["category_name"], how="left"
)
filtered_subcategory = unique_subcategory_with_id.join(
    SUBCATEGORY_LOADED, on=["subcategory_name", "category_id"], how="leftanti"
)

# DB에 없던 서브카테고리 삽입
filtered_subcategory.foreachPartition(
    lambda partition: insert_new_subcategories(partition, db_props, db_url)
)

# 최신화 된 SUBCATEGORY 테이블 로드
SUBCATEGORY_LOADED = spark.read.jdbc(
    url=db_url, table=get_subcategory_query, properties=db_props
)

COURSE_WITH_IDS = COURSE.join(SUBCATEGORY_LOADED, on="subcategory_name", how="left")
COURSE_WITH_IDS = COURSE_WITH_IDS.withColumn(
    "summary", substring(col("summary"), 1, 350)
)  # summary CHAR(350) 미만으로 되게

COURSE_WITH_IDS.foreachPartition(
    lambda partition: insert_course_partition(partition, "COURSE", db_props, db_url)
)

# COURSE 테이블에서 url과 course_id 불러오기
ID_TITLE_FROM_COURSE = spark.read.jdbc(
    url=db_url, table="COURSE", properties=db_props
).select("course_id", "url")

UNIQUE_SECTION = SECTION_SUBSECTION.dropDuplicates(["url", "section_num"])
SECTION_WITH_ID = UNIQUE_SECTION.join(
    ID_TITLE_FROM_COURSE, on="url", how="inner"
).drop("url")
SECTION = SECTION_WITH_ID.select(["course_id", "section_num", "section_name"])

# SECTION 테이블에 삽입
SECTION.foreachPartition(
    lambda partition: insert_section_partition(partition, "SECTION", db_props, db_url)
)

SUBSECTION_WITH_ID = SECTION_SUBSECTION.join(
    ID_TITLE_FROM_COURSE, on="url", how="inner"
).drop("url")
SUBSECTION = SUBSECTION_WITH_ID.select(
    ["course_id", "section_num", "subsection_num", "subsection_name"]
)

# SUBSECTION 테이블에 삽입
SUBSECTION.foreachPartition(
    lambda partition: insert_subsection_partition(
        partition, "SUBSECTION", db_props, db_url
    )
)

# REVIEW_SUMMARY 테이블에 삽입
UNIQUE_REVIEW = REVIEW_SUMMARY.dropDuplicates(["url", "summary"])
REVIEW_WITH_ID = UNIQUE_REVIEW.join(
    ID_TITLE_FROM_COURSE, on="url", how="inner"
).drop("url")
REVIEW_SUMMARY = REVIEW_WITH_ID.select(["course_id", "summary"])

REVIEW_SUMMARY.show()

REVIEW_SUMMARY.foreachPartition(
    lambda partition: insert_review_summary_partition(
        partition, "REVIEW_SUMMARY", db_props, db_url
    )
)

spark.read.jdbc(url=db_url, table="CATEGORY", properties=db_props).show()
spark.read.jdbc(url=db_url, table="SUBCATEGORY", properties=db_props).select("*").where(col("category_id") == 13).show()
spark.read.jdbc(url=db_url, table="COURSE", properties=db_props).select("*").where(col("subcategory_id") == 75).show()
spark.read.jdbc(url=db_url, table="SECTION", properties=db_props).select("*").where(col("course_id") == 3401).show()
spark.read.jdbc(url=db_url, table="SUBSECTION", properties=db_props).select("*").where(col("course_id") == 3401).show()
spark.read.jdbc(url=db_url, table="REVIEW_SUMMARY", properties=db_props).select("*").where(col("course_id") == 3401).show()

spark.stop()