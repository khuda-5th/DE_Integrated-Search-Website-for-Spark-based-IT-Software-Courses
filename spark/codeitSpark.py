!pip install pandas
!pip install sumy
!pip install pyspark

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, trim, regexp_extract, col, regexp_replace, split, lit, row_number, rand
from pyspark.sql.window import Window
from dotenv import load_dotenv

# Spark 세션 초기화
spark = SparkSession.builder \
    .appName("DF to DB") \
    .getOrCreate()

df = spark.read.option("multiline", "true").json("codeit_final.json")

# CATEGORY 테이블에 삽입할 정보를 담은 df
df_category = df.select(col("big_categ").alias("category_name")) \
                .withColumn("platform_id", lit(3)) \
                .dropna()

# SUBCATEGORY 테이블에 삽입할 정보를 담은 df
df_subcategory = df.withColumn("sub_categs", explode(col("sub_categs"))) \
                .select(
                    col("big_categ").alias("category_name"),
                    col("sub_categs.sub_categ").alias("subcategory_name")
                ) \
                .dropna()

# COURSE 테이블에 삽입할 정보를 담은 df
df_course = df.withColumn("sub_categs", explode(col("sub_categs"))) \
                .withColumn("lectures", explode(col("sub_categs.lectures"))) \
                .select(
                    col("sub_categs.sub_categ").alias("subcategory_name"),
                    col("lectures.title").alias("course_title"),
                    col("lectures.summary").alias("summary"),
                    col("lectures.lecture_num").alias("num_of_lecture"),
                    col("lectures.link").alias("url")
                ) \
                .dropna()
df_course = df_course.withColumn("num_of_lecture", regexp_extract(col("num_of_lecture"), "\\d+", 0).cast("int")) 
df_course = df_course.dropDuplicates(["url"])

# df_category.show()
# df_subcategory.show()
# df_course.show()

# .env 파일 로드
load_dotenv()

db_url = os.getenv("DB_URL")
db_properties = {
    "driver": os.getenv("DB_DRIVER"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

# df_category, df_subcategory 준비
df_category = spark.read.jdbc(url=db_url, table="CATEGORY", properties=db_properties)

df_subcategory = df_subcategory.join(df_category, df_subcategory.category_name == df_category.category_name, "left_outer") \
    .select(df_subcategory["*"], df_category.category_id.alias("category_id"))
df_subcategory = df_subcategory.select("category_id", "subcategory_name")
# df_subcategory.show()

# 데이터베이스에 CATEGORY, SUBCATEGORY 정보 삽입
df_category.write.jdbc(url=db_url, table="CATEGORY", mode="ignore", properties=db_properties)
df_subcategory.write.jdbc(url=db_url, table="SUBCATEGORY", mode="ignore", properties=db_properties)

spark.read.jdbc(url=db_url, table="CATEGORY", properties=db_properties).show()
spark.read.jdbc(url=db_url, table="SUBCATEGORY", properties=db_properties).show()


# df_course 준비
df_subcategory = spark.read.jdbc(url=db_url, table="SUBCATEGORY", properties=db_properties)
df_course = df_course.join(df_subcategory, df_course.subcategory_name == df_subcategory.subcategory_name, "left_outer") \
    .select(df_course["*"], df_subcategory.subcategory_id.alias("subcategory_id"))

all_columns = df_course.columns
columns_to_select = [col for col in all_columns if col != "subcategory_name"]
df_course = df_course.select(*columns_to_select)

# 데이터베이스에 COURSE 정보 삽입
df_course.write.jdbc(url=db_url, table="COURSE", mode="ignore", properties=db_properties)

# spark.read.jdbc(url=db_url, table="COURSE", properties=db_properties).show()

# section, review에 course_id 매핑
df_course_DB = spark.read.jdbc(url=db_url, table="COURSE", properties=db_properties).select("course_id", "url")


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

df_sectionInfo_withID = df_sectionInfo.join(df_course_DB, on="url", how="inner").drop("url").distinct()
df_reviewInfo_withID = df_reviewInfo.join(df_course_DB, on="url", how="inner").drop("url").distinct()

# df_sectionInfo_withID.show(truncate=True)
# df_reviewInfo_withID.show()

# df_section, df_subsection 준비
df_sectionInfo_withID = df_sectionInfo_withID.withColumn(
    "curriculum",
    regexp_replace(col("curriculum"), r'^\n+', '')
)

df_parsed = df_sectionInfo_withID.withColumn(
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
    col("course_id"),
    col("section_num").cast("int"),
    col("section_title").alias("section_name"),
    col("subsection").alias("subsection_name")
).orderBy("course_id", "section_num")

windowSpec = Window.partitionBy("course_id", "section_num").orderBy("subsection_name")

df_result_with_subsection_num = df_result.withColumn(
    "subsection_num",
    row_number().over(windowSpec)
)

df_section = df_result_with_subsection_num.select("course_id", "section_num", "section_name").distinct()
df_subsection = df_result_with_subsection_num.select("course_id", "section_num", "subsection_num", "subsection_name")

# df_section.show(truncate=True)
# df_subsection.show(truncate=True)

# 데이터베이스에 SECTION, SUBSECTION 정보 삽입
df_section.write.jdbc(url=db_url, table="SECTION", mode="ignore", properties=db_properties)
df_subsection.write.jdbc(url=db_url, table="SUBSECTION", mode="ignore", properties=db_properties)

# spark.read.jdbc(url=db_url, table="SECTION", properties=db_properties).show()
# spark.read.jdbc(url=db_url, table="SUBSECTION", properties=db_properties).show()

# df_review 준비
df_reviews_split = df_reviewInfo_withID.withColumn(
    "review",
    explode(split(col("review_info"), r'\n(?=\w+\n)'))
).filter(trim(col("review")) != "")

df_reviews_cleaned = df_reviews_split.withColumn(
    "review_text",
    regexp_extract(col("review"), r'^\w+\n(.*)', 1)
).filter(trim(col("review_text")) != "")

df_reviews_result = df_reviews_cleaned.select(
    col("course_id"),
    col("review_text").alias("summary")
).orderBy("course_id")

window_spec = Window.partitionBy("course_id").orderBy(rand())

df_review = df_reviews_result.withColumn(
    "rank",
    row_number().over(window_spec)
).filter(col("rank") <= 3).drop("rank").distinct()

# df_review.show(truncate=False)

# 데이터베이스에 REVIEW_SUMMARY 정보 삽입
df_review.write.jdbc(url=db_url, table="REVIEW_SUMMARY", mode="ignore", properties=db_properties)
# spark.read.jdbc(url=db_url, table="REVIEW_SUMMARY", properties=db_properties).show()

# Spark 세션 종료
spark.stop()