from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql.functions import (
    explode,
    col,
    regexp_replace,
    monotonically_increasing_id,
    udf,
    size,
    when,
    lit,
    sum,
    array,
    substring,
    regexp_replace,
    row_number,
)
from pyspark.sql.types import ArrayType
from pyspark.sql.window import Window
from dotenv import load_dotenv
import os
import psycopg2

from utilities import *

load_dotenv()

PLATFORM_ID = 2  # 패캠 platform_id
# 데이터베이스 정보 설정
db_props = {
    "driver": "org.postgresql.Driver",
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}
# 데이터베이스 URL 설정
db_url = os.getenv("DB_URL")

DATA_PATH = "datasets/2405181308_fastcampus_new.json"
# Spark 세션 초기화
spark = SparkSession.getActiveSession()
if spark is not None:
    spark.stop()
spark = SparkSession.builder.appName("JsonFileRead").getOrCreate()
spark.sparkContext.setLogLevel("INFO")
data = spark.read.option("multiline", "true").json(DATA_PATH)

# 배열 필드를 explode하여 개별 행으로 확장
df = data.select(explode("new_courses").alias("new_course"))

# 필요한 필드만 선택 -> 전체 필드 선택
df = df.select(
    col("new_course.title"),
    col("new_course.intro"),
    col("new_course.badge"),
    col("new_course.tags"),
    col("new_course.course_img"),
    col("new_course.new_course_img"),
    col("new_course.course_url"),
    col("new_course.regular_price"),
    col("new_course.sale_price"),
    col("new_course.summary"),
    col("new_course.parts"),
    col("new_course.accordion"),
)

df = df.withColumn(
    "regular_price", regexp_replace(col("regular_price"), "[^0-9]", "").cast("int")
)

df = df.withColumn(
    "sale_price", regexp_replace(col("sale_price"), "[^0-9]", "").cast("int")
)


# 태그 정리
spark = SparkSession.getActiveSession()
if spark is not None:
    spark.stop()
spark = SparkSession.builder.appName("Process tag").getOrCreate()
spark.sparkContext.setLogLevel("INFO")

# 'tags' 컬럼만 추출
df_combined = df.select(col("tags"))

final_words_per_row = process_tags(df_combined, spark)

df_with_final_words = spark.createDataFrame(
    final_words_per_row, ["tags", "final_words"]
)

# 고유 인덱스 추가
df = (
    df.rdd.zipWithIndex()
    .toDF()
    .withColumnRenamed("_2", "id")
    .select(col("_1.*"), col("id"))
)
df_with_final_words = (
    df_with_final_words.rdd.zipWithIndex()
    .toDF()
    .withColumnRenamed("_2", "id")
    .select(col("_1.*"), col("id"))
)

# 데이터프레임 조인
df3 = df.join(df_with_final_words, "id", "left").drop("id")

# 필요한 필드만 선택
df = df3.select(
    col("title").alias("course_title"),
    col("intro").alias("summary"),
    col("course_url").alias("url"),
    col("course_img").alias("img"),
    col("new_course_img").alias("new_img"),
    col("regular_price").alias("reg_price"),
    col("sale_price").alias("dis_price"),
    col("final_words").alias("tag"),
    col("parts"),
    col("accordion"),
)

COURSE = df.select(
    col("course_title"),
    col("summary"),
    col("url"),
    col("img"),
    col("new_img"),
    col("reg_price"),
    col("dis_price"),
)

TAG = df.select(
    col("course_title"),
    col("tag"),
)

TAG = TAG.withColumn("tag", explode(col("tag")))

# 정규 표현식을 사용하여 accordion에서 숫자와 제목을 추출하는 UDF
extract_subsection_number_and_title_udf = udf(
    lambda x: extract_subsection_number_and_title(x),
    ArrayType(
        StructType(
            [
                StructField("subsection_num", IntegerType(), True),
                StructField("subsection_name", StringType(), True),
            ]
        )
    ),
)

extract_subsection_number_and_title_udf = udf(
    lambda x: extract_subsection_number_and_title(x),
    ArrayType(
        StructType(
            [
                StructField("subsection_num", IntegerType(), True),
                StructField("subsection_name", StringType(), True),
            ]
        )
    ),
)

# accordion 배열을 개별 행으로 확장하고 숫자와 제목을 추출
df_accordion_exploded = (
    df.withColumn("accordion", explode(col("accordion")))
    .withColumn(
        "accordion_info", extract_subsection_number_and_title_udf(col("accordion"))
    )
    .select(
        col("course_title"), explode(col("accordion_info")).alias("subsection_info")
    )
    .select(
        col("course_title"),
        col("subsection_info.subsection_num").alias("subsection_num"),
        col("subsection_info.subsection_name"),
    )
)

# 정규 표현식을 사용하여 Part 번호와 제목을 추출하는 UDF
extract_part_number_and_title_udf = udf(
    extract_part_number_and_title,
    StructType(
        [
            StructField("section_num", IntegerType(), True),
            StructField("section_name", StringType(), True),
        ]
    ),
)

extract_part_number_and_title_udf = udf(
    extract_part_number_and_title,
    StructType(
        [
            StructField("section_num", IntegerType(), True),
            StructField("section_name", StringType(), True),
        ]
    ),
)

# parts가 빈 배열인 경우 처리
df_with_default_parts = df.withColumn(
    "parts", when(size(col("parts")) == 0, array(lit(""))).otherwise(col("parts"))
)

# parts 배열을 개별 행으로 확장하고 Part 번호와 제목을 추출
df_parts_exploded = (
    df_with_default_parts.withColumn("part", explode(col("parts")))
    .withColumn("part_info", extract_part_number_and_title_udf(col("part")))
    .select(
        col("course_title"),
        when(col("part") == "", lit(-1))
        .otherwise(col("part_info.section_num"))
        .alias("section_num"),
        when(col("part") == "", lit(""))
        .otherwise(col("part_info.section_name"))
        .alias("section_name"),
    )
)

# num_of_section 컬럼 추가
df_with_num_of_section = df.withColumn("num_of_section", size(col("parts")))

# 최종 데이터프레임 생성 (num_of_section 컬럼 포함)
df_parts_exploded = df_parts_exploded.join(
    df_with_num_of_section.select("course_title", "num_of_section"), on="course_title"
)

# 각 course_title 내에서 순서 부여
df_accordion_exploded = df_accordion_exploded.withColumn(
    "id", monotonically_increasing_id()
)
window_spec = Window.partitionBy("course_title").orderBy("id")
df_accordion_exploded = df_accordion_exploded.withColumn(
    "row_id", row_number().over(window_spec)
)

# count 플래그 추가
df_accordion_exploded = df_accordion_exploded.withColumn(
    "section_change", when(col("subsection_num") == 1, lit(1)).otherwise(lit(0))
)

# 누적 합계를 사용하여 section_num 생성
window_spec_acc = (
    Window.partitionBy("course_title")
    .orderBy("row_id")
    .rowsBetween(Window.unboundedPreceding, Window.currentRow)
)
df_accordion_exploded = df_accordion_exploded.withColumn(
    "section_num_increment", sum("section_change").over(window_spec_acc)
)

# 기존 PARTS와 조인
df_combined = (
    df_accordion_exploded.alias("a")
    .join(
        df_parts_exploded.alias("p"),
        (col("a.course_title") == col("p.course_title"))
        & (col("a.section_num_increment") == col("p.section_num")),
    )
    .select(
        col("a.course_title"),
        col("p.section_num"),
        col("p.section_name"),
        col("a.subsection_num"),
        col("a.subsection_name"),
    )
)

# 결과 정렬 및 출력
SECTION_SUBSECTION = df_combined.orderBy(
    col("course_title"), col("section_num"), col("subsection_num")
)

COURSE = COURSE.withColumn("subcategory_id", lit(-1))

# 카테고리: new_course라 id -1로 삽입
insert_category_query = f"""
INSERT INTO CATEGORY (platform_id, category_name, category_id)
VALUES ({PLATFORM_ID}, 'None', -1)
ON CONFLICT (category_id) DO NOTHING;
"""
execute_sql_query(insert_category_query, db_url, db_props)

# 서브카테고리: new_course라 id -1로 삽입
insert_subcategory_query = """
INSERT INTO SUBCATEGORY (category_id, subcategory_id, subcategory_name)
VALUES (-1, -1, 'None')
ON CONFLICT (subcategory_id) DO NOTHING;
"""
execute_sql_query(insert_subcategory_query, db_url, db_props)

# COURSE 테이블에 먼저 삽입 (같은 course에 대한 COURSE와 NEW_COURSE의 course_id를 동일하게 가져가기 위함)
COURSE.drop("new_img").foreachPartition(
    lambda partition: insert_course_partition(partition, "COURSE", db_props, db_url)
)


# course_id를 COURSE 테이블에서 조회하여 url을 기준으로 조인하는 함수
def add_course_id(df, db_props, db_url):
    conn = psycopg2.connect(
        dbname=db_url.split("/")[-1],
        user=db_props["user"],
        password=db_props["password"],
        host=db_url.split("//")[1].split(":")[0],
        port=db_url.split(":")[-1].split("/")[0],
    )
    cursor = conn.cursor()

    course_data = []
    for row in df.collect():
        query = "SELECT course_id, url FROM COURSE WHERE url = %s"
        cursor.execute(query, (row.url,))
        result = cursor.fetchone()
        if result:
            course_data.append((result[1], result[0]))  # (url, course_id)
        else:
            course_data.append((row.url, None))

    cursor.close()
    conn.close()

    schema = df.schema.add("course_id", IntegerType(), True)
    course_id_df = spark.createDataFrame(course_data, ["url", "course_id"])

    return df.join(course_id_df, "url", "left")


# course_id를 추가한 DataFrame 생성
course_with_id_df = add_course_id(COURSE, db_props, db_url)

# NEW_COURSE 테이블에 삽입
course_with_id_df.foreachPartition(
    lambda partition: insert_new_course_partition(
        partition, "NEW_COURSE", db_props, db_url
    )
)

# COURSE 테이블에서 course_title과 course_id 불러오기
ID_TITLE_FROM_COURSE = spark.read.jdbc(
    url=db_url, table="COURSE", properties=db_props
).select("course_id", "course_title")

# TAG DataFrame과 NEW_COURSE DataFrame을 조인하여 course_id 매핑
TAG_WITH_ID = TAG.join(ID_TITLE_FROM_COURSE, on="course_title", how="inner").drop(
    "course_title"
)
# 태그 DB 삽입
TAG_WITH_ID.foreachPartition(
    lambda partition: insert_tag_partition(partition, "TAG", db_props, db_url)
)

UNIQUE_SECTION = SECTION_SUBSECTION.dropDuplicates(["course_title", "section_num"])
SECTION_WITH_ID = UNIQUE_SECTION.join(
    ID_TITLE_FROM_COURSE, on="course_title", how="inner"
).drop("course_title")
SECTION = SECTION_WITH_ID.select(["course_id", "section_num", "section_name"])
# SECTION 테이블에 삽입
SECTION.foreachPartition(
    lambda partition: insert_section_partition(partition, "SECTION", db_props, db_url)
)

SUBSECTION_WITH_ID = SECTION_SUBSECTION.join(
    ID_TITLE_FROM_COURSE, on="course_title", how="inner"
).drop("course_title")
SUBSECTION = SUBSECTION_WITH_ID.select(
    ["course_id", "section_num", "subsection_num", "subsection_name"]
)
# SUBSECTION 테이블에 삽입
SUBSECTION.foreachPartition(
    lambda partition: insert_subsection_partition(
        partition, "SUBSECTION", db_props, db_url
    )
)

spark.stop()
