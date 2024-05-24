!pip install pandas
!pip install sumy
!pip install pyspark

from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, col, regexp_extract, lit, monotonically_increasing_id, lag, when, split
from pyspark.sql.window import Window
from pyspark.sql.types import StringType, IntegerType

# Spark 세션 초기화
spark = SparkSession.builder \
    .appName("DF to DB") \
    .getOrCreate()

# JSON 파일 읽기
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

# Spark 세션 초기화
spark = SparkSession.builder \
    .appName("JSON to DataFrame") \
    .getOrCreate()
db_properties = {
    "driver": "org.postgresql.Driver",
    "user": "khudade",
    "password": "khudade"
}
db_url = "jdbc:postgresql://54.180.100.57:5432/lecture_db"

# df_category, df_subcategory 준비
df_category = spark.read.jdbc(url=db_url, table="CATEGORY", properties=db_properties)

df_subcategory = df_subcategory.join(df_category, df_subcategory.category_name == df_category.category_name, "left_outer") \
    .select(df_subcategory["*"], df_category.category_id.alias("category_id"))
df_subcategory = df_subcategory.select("category_id", "subcategory_name")
df_subcategory.show()

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

spark.read.jdbc(url=db_url, table="COURSE", properties=db_properties).show()

# df_section 준비
df_course_DB = spark.read.jdbc(url=db_url, table="COURSE", properties=db_properties).select("course_id", "url")

df_sectionInfo = df.withColumn("sub_categs", explode(col("sub_categs"))) \
                .withColumn("lectures", explode(col("sub_categs.lectures"))) \
                .select(
                    col("lectures.link").alias("url"),
                    col("lectures.curriculum").alias("curriculum")
                ) \
                .dropna()
df_sectionInfo_withID = df_sectionInfo.join(df_course_DB, on="url", how="inner").drop("url")
df_split = df_sectionInfo_withID.withColumn("curriculum", explode(split(col("curriculum"), "\n")))
df_split = df_split.withColumn("id", monotonically_increasing_id())
windowSpec = Window.partitionBy("course_id").orderBy("id")
df_split = df_split.withColumn("prev_value", lag("curriculum", 1).over(windowSpec))

df_section_num = df_split.filter(col("curriculum").rlike("^[0-9]+$"))
df_section_title = df_split.filter(~col("curriculum").rlike("^[0-9]+$"))

df_section_num = df_section_num.select("course_id", col("curriculum").alias("section_num"))
df_section_title = df_section_title.select("course_id", col("prev_value").alias("section_num"), col("curriculum").alias("section_name"))

df_section = df_section_title.join(df_section_num, on=["course_id", "section_num"])
df_section = df_section.select("course_id", col("section_num").cast("int"), "section_name").distinct()
df_section = df_section.orderBy("course_id", "section_num")

df_section = df_section.write.jdbc(url=db_url, table="SECTION", mode="ignore", properties=db_properties)

spark.read.jdbc(url=db_url, table="SECTION", properties=db_properties).show()

# Spark 세션 종료
spark.stop()