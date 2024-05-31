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

DATA_PATH = "datasets/2405180024_fastcampus_all.json"
# Spark 세션 초기화
spark = SparkSession.getActiveSession()
if spark is not None:
    spark.stop()
spark = SparkSession.builder.appName("JsonFileRead").getOrCreate()
data = spark.read.option("multiline", "true").json(DATA_PATH)

# category 배열 확장
# category 내 sub_category 배열 확장
# sub_category 내 courses 배열 확장
# course에서 필요한 필드 선택
df = (
    data.select(explode("categories").alias("categories"))
    .select(
        col("categories.category_name"),
        explode("categories.sub_categories").alias("sub_categories"),
    )
    .select(
        col("category_name"),
        col("sub_categories.sub_category_name"),
        explode("sub_categories.courses").alias("courses"),
    )
    .select(
        col("category_name"),
        col("sub_category_name"),
        col("courses.title"),
        col("courses.intro"),
        col("courses.badge"),
        col("courses.tags"),
        col("courses.course_img"),
        col("courses.course_url"),
        col("courses.regular_price"),
        col("courses.sale_price"),
        col("courses.accordion"),
        col("courses.parts"),
    )
)

# 정가 str -> int
df = df.withColumn(
    "regular_price", regexp_replace(col("regular_price"), "[^0-9]", "").cast("int")
)
# 할인가 str -> int
df = df.withColumn(
    "sale_price", regexp_replace(col("sale_price"), "[^0-9]", "").cast("int")
)

# 태그 정리
spark = SparkSession.builder.appName("Tags KMeans Clustering").getOrCreate()

df_combined = df.select(col("tags"))

final_words_per_row = process_tags(df_combined, spark)

# 새로운 DataFrame 생성
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
    col("category_name"),
    col("sub_category_name"),
    col("title").alias("course_title"),
    col("intro").alias("summary"),
    col("course_url").alias("url"),
    col("course_img").alias("img"),
    col("regular_price").alias("reg_price"),
    col("sale_price").alias("dis_price"),
    col("final_words").alias("tags"),
    col("parts"),
    col("accordion"),
)

COURSE = df.select(
    col("category_name"),
    col("sub_category_name").alias("subcategory_name"),
    col("course_title"),
    col("summary"),
    col("url"),
    col("img"),
    col("reg_price"),
    col("dis_price"),
)

TAG = df.select(
    col("course_title"),
    col("tags").alias("tag"),
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

# 각 course_title 내에서 count가 변할 때마다 PARTS의 section_num을 증가시키도록 설정
df_accordion_exploded = df_accordion_exploded.withColumn(
    "id", monotonically_increasing_id()
)
window_spec = Window.partitionBy("course_title").orderBy("id")

# count 플래그 추가
df_accordion_exploded = df_accordion_exploded.withColumn(
    "section_change", when(col("subsection_num") == 1, lit(1)).otherwise(lit(0))
)

# 누적 합계를 사용하여 section_num 생성
window_spec_acc = (
    Window.partitionBy("course_title")
    .orderBy("id")
    .rowsBetween(Window.unboundedPreceding, Window.currentRow)
)
df_accordion_exploded = df_accordion_exploded.withColumn(
    "section_num_increment", sum("section_change").over(window_spec_acc)
)

# PARTS와 ACCORDION 조인
df_combined = df_accordion_exploded.join(
    df_parts_exploded,
    (df_accordion_exploded.course_title == df_parts_exploded.course_title)
    & (df_accordion_exploded.section_num_increment == df_parts_exploded.section_num),
)

# 중복 제거를 위해 필요한 컬럼 선택
df_combined = df_combined.select(
    df_accordion_exploded.course_title,
    df_parts_exploded.section_num,
    df_parts_exploded.section_name,
    df_accordion_exploded.subsection_num,
    df_accordion_exploded.subsection_name,
).distinct()

# 결과 정렬 및 출력
SECTION_SUBSECTION = df_combined.orderBy(
    col("course_title"), col("section_num"), col("subsection_num")
)

unique_category = COURSE.select("category_name").distinct()
unique_subcategory = COURSE.select("subcategory_name", "category_name").distinct()

# DB 파트
spark = (
    SparkSession.builder.appName("postgresql session")
    .config("spark.jars.packages", "org.postgresql:postgresql:42.2.18")
    .getOrCreate()
)

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
    CATEGORY_LOADED = spark.read.jdbc(
    url=db_url, table=get_category_query, properties=db_props
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

subcategory_ids = [
    row.subcategory_id
    for row in SUBCATEGORY_LOADED.select("subcategory_id").distinct().collect()
    ]
# 해당 플랫폼의 SUBCATEGORY 테이블이 비었을 경우 현재 카테고리들 삽입 후 다시 가져옴
if not subcategory_ids:
    unique_subcategory.foreachPartition(
        lambda partition: insert_new_subcategories(partition, db_props, db_url)
    )
    SUBCATEGORY_LOADED = spark.read.jdbc(
    url=db_url, table=get_subcategory_query, properties=db_props
    )
    subcategory_ids = [
        row.subcategory_id
        for row in SUBCATEGORY_LOADED.select("subcategory_id").distinct().collect()
    ]

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

# COURSE 테이블에서 course_title과 course_id 불러오기
ID_TITLE_FROM_COURSE = spark.read.jdbc(
    url=db_url, table="COURSE", properties=db_props
).select("course_id", "course_title")

# TAG DataFrame과 NEW_COURSE DataFrame을 조인하여 course_id 매핑
TAG_WITH_ID = TAG.join(ID_TITLE_FROM_COURSE, on="course_title", how="inner").drop(
    "course_title"
)
TAG_WITH_ID = TAG_WITH_ID.withColumn(
    "tag", substring(col("tag"), 1, 30)
)  # 길이 30 제한

# TAG 테이블에 삽입
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
