import pandas as pd
from pyspark.sql.window import Window
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    udf,
    coalesce,
    lit,
    substring,
    trim,
    regexp_replace,
    col,
    explode,
    format_number,
    regexp_extract,
    concat_ws,
    lit,
    when,
    split,
)
from pyspark.sql.types import StringType, IntegerType, StructType, StructField
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
import re
import json
from pyspark.sql import Window
from pyspark.sql.types import (
    ArrayType,
    StructType,
    StructField,
    StringType,
    IntegerType,
)
import re
from pyspark.sql.functions import length, col

from utilities import *
from dotenv import load_dotenv
import os


load_dotenv()
PLATFORM_ID = 1
db_props = {
    "driver": "org.postgresql.Driver",
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}
db_url = os.getenv("DB_URL")

FILE_PATH = "datasets/test03-06.json"

spark = SparkSession.builder.appName("JSON to DataFrame").getOrCreate()

with open(FILE_PATH, encoding="utf8", errors="ignore") as f:
    lines = f.read().splitlines()

valid_lines = []
for line in lines:
    try:
        parsed_line = json.loads(line)
        valid_lines.append(parsed_line)
    except json.JSONDecodeError as e:
        pass

df = pd.DataFrame(valid_lines)

categories_expanded = df.explode("category").reset_index(drop=True)

# sub_category 데이터 추출 및 category_name 추가
structured_df = categories_expanded.assign(
    category_name=categories_expanded["category"].apply(
        lambda x: x["category_name"] if "category_name" in x else None
    ),
    sub_category_name=categories_expanded["category"].apply(
        lambda x: (
            x["sub_category"]["sub_category_name"]
            if "sub_category" in x and "sub_category_name" in x["sub_category"]
            else None
        )
    ),
    courses=categories_expanded["category"].apply(
        lambda x: (
            x["sub_category"]["courses"]
            if "sub_category" in x and "courses" in x["sub_category"]
            else None
        )
    ),
)

# Spark DataFrame으로 변환
spark_df = spark.createDataFrame(structured_df)

exploded_df = spark_df.select(
    "category_name", "sub_category_name", explode("courses").alias("course")
)

courses_df = exploded_df.select(
    col("category_name"),
    col("sub_category_name"),
    trim(regexp_replace(regexp_replace(col("course.title"), "\n", ""), ",", " ")).alias(
        "course_name"
    ),
    regexp_extract(
        trim(
            regexp_replace(
                regexp_replace(col("course.num_of_lecture"), "[\n,]", ""), "\s+", " "
            )
        ),
        r"(\d+)개",
        1,
    )
    .cast("int")
    .alias("num_of_lecture"),
    trim(
        regexp_replace(regexp_replace(col("course.instructor"), "\n", ""), ",", " ")
    ).alias("instructor"),
    split(
        trim(
            regexp_replace(
                regexp_replace(col("course.tag"), "[\[\]]", ""), "\s*,\s*", ","
            )
        ),
        ",",
    ).alias("tag"),
    format_number(
        coalesce(
            regexp_extract(col("course.star"), r"(\d+\.\d+)", 1).cast("float"), lit(0.0)
        ),
        1,
    ).alias("star"),
    trim(
        regexp_replace(
            regexp_replace(
                regexp_replace(col("course.num_of_stud"), "[명\[\]\n,]", ""), ",", ""
            ),
            "\s+",
            " ",
        )
    )
    .cast("integer")
    .alias("num_of_stud"),
    trim(
        regexp_replace(regexp_replace(col("course.img"), "[\n,]", ""), "\s+", " ")
    ).alias("img"),
    when(col("course.price").rlike("무료"), "free")
    .otherwise(
        trim(
            regexp_replace(
                regexp_replace(
                    regexp_replace(
                        regexp_extract(col("course.price"), r".*?원", 0), "원", ""
                    ),
                    ",",
                    "",
                ),
                "\s+",
                "",
            )
        )
    )
    .alias("price_raw"),
    trim(
        regexp_replace(
            regexp_replace(
                regexp_replace(
                    regexp_replace(col("course.text"), "[\n,]", ""), "\s+", " "
                ),
                r"있습니다\b",
                "있습니다.",
            ),
            r"\.\.",
            ".",
        )
    ).alias("text"),
    trim(
        regexp_replace(
            regexp_replace(concat_ws(", ", col("course.review")), "[\[\]\n]", ""),
            ",",
            " ",
        )
    ).alias("review"),
    trim(
        regexp_replace(regexp_replace(col("course.curri"), "[\n,]", ""), "\s+", " ")
    ).alias("curri"),
    trim(
        regexp_replace(
            regexp_replace(col("course.course_link"), "\s+", ""), "[\n,]", ""
        )
    ).alias("course_link"),
)

# 'price_raw' 컬럼을 처리하여 'free'를 제외한 나머지를 정수형으로 변환합니다.
courses_df = courses_df.withColumn(
    "price",
    when(col("price_raw") == "free", lit(0)).otherwise(col("price_raw").cast("int")),
).drop("price_raw")

# 'course.price' 열을 가공하여 'price_raw', 'dis_price' 열을 생성
courses_df = courses_df.withColumn(
    "price_raw",
    when(col("price").rlike("무료"), 0).otherwise(
        trim(
            regexp_replace(
                regexp_replace(regexp_replace(col("price"), "[\n,]", ""), "\s+", " "),
                " ",
                "",
            )
        )
    ),
)

# 'dis_price'와 'price' 열 생성
courses_df = (
    courses_df.withColumn(
        "dis_price",
        when(
            col("price_raw").rlike("%"),
            regexp_extract(col("price_raw"), r"%(\d+)원", 1).cast("int"),
        ).otherwise(lit(None)),
    )
    .withColumn(
        "price",
        when(
            col("price_raw").rlike("%"),
            regexp_extract(col("price_raw"), r"(\d+)원.*(\d+)원", 2).cast("int"),
        ).otherwise(
            when(col("price_raw") == "free", lit("free")).otherwise(
                col("price_raw").cast("int")
            )
        ),
    )
    .drop("price_raw")
)

courses_df = courses_df.select(
    "category_name",
    "sub_category_name",
    "course_name",
    "num_of_lecture",
    "instructor",
    "tag",
    "star",
    "num_of_stud",
    "img",
    "price",
    "dis_price",
    "text",
    "review",
    "curri",
    "course_link",
)

curri_df = exploded_df.select("course.curri")


cleaned_curri_df = exploded_df.select(
    regexp_replace(
        regexp_replace(
            regexp_replace(
                regexp_replace(
                    regexp_replace(
                        regexp_replace(col("course.curri"), r"\s+", " "), r"\n", ""
                    ),
                    r" ,",
                    "",
                ),
                r", 미리보기",
                "",
            ),
            r" ∙ ",
            ",",
        ),
        r"강의 이벤트 진행중,",
        "",
    ).alias("curri")
)


def extract_durations(data_str):
    # 시간과 분에 대한 정규 표현식 패턴을 정의합니다.
    pattern = r"(\d+시간\s*\d*분|\d+시간|\d+분|\d+:\d+)"

    # 정규 표현식을 사용하여 모든 duration_str을 찾습니다.
    durations = re.findall(pattern, data_str)

    return durations


def format_duration(duration_str):
    # 시간과 분에 대한 정규 표현식 패턴을 정의합니다.
    hour_pattern = r"(\d+)\s*시간"
    minute_pattern = r"(\d+)\s*분"
    colon_pattern = r"(\d+):(\d+)"

    # 입력 문자열에서 시간과 분을 찾습니다.
    hours_match = re.search(hour_pattern, duration_str)
    minutes_match = re.search(minute_pattern, duration_str)
    colon_match = re.search(colon_pattern, duration_str)

    # 결과를 초기화합니다.
    result = ""

    # 시간이 존재하면 처리합니다.
    if hours_match:
        hours = hours_match.group(1)
        result += f"{hours} hours"

    # 분이 존재하면 처리합니다.
    if minutes_match:
        minutes = int(minutes_match.group(1))
        if minutes > 0:
            if result:
                result += " "
            result += f"{minutes} minutes"

    if colon_match:
        hours = colon_match.group(1)
        minutes = int(colon_match.group(2))
        result += f"{int(hours)} hours"
        if minutes > 0:
            result += f" {minutes} minutes"

    return result


def parse_curri(curri):
    sections = re.split(r"섹션 \d+\.", curri)
    section_indices = re.findall(r"섹션 (\d+)", curri)
    results = []
    for idx, section in zip(section_indices, sections[1:]):  # 첫 번째 빈 섹션 제외
        parts = re.split(r",\s*", section.strip())
        if len(parts) < 4:
            continue

        # '1 강, 8분'을 '1 강'과 '8분'으로 나눔
        for i in range(len(parts)):
            if re.match(r"\d+\s*강,\s*\d+분", parts[i]):
                split_parts = re.split(r",\s*", parts[i])
                parts[i : i + 1] = split_parts

        section_name = parts[0]
        num_of_section = 0
        num_match = re.search(r"(\d+) 강", section)
        if num_match:
            num_of_section = int(num_match.group(1))

        duration_candidates = extract_durations(section)
        section_time = format_duration(
            duration_candidates[0].strip() if duration_candidates else ""
        )

        # 서브섹션 정보 추출
        subsection_infos = parts[3:]  # 첫 3개 이후 정보부터
        subsection_names = []
        subsection_times = []

        # 서브섹션 이름과 시간을 추출
        temp_name = ""
        for info in subsection_infos:
            if re.match(r"\d+:\d+", info):
                subsection_times.append(info.strip())
                subsection_names.append(temp_name.strip())
                temp_name = ""
            else:
                temp_name += " " + info.strip()

        subsection_num = 1
        for sub_name, sub_time in zip(subsection_names, subsection_times):
            formatted_time = format_duration(sub_time)
            results.append(
                {
                    "section_num": int(idx),
                    "section_name": section_name,
                    "num_of_section": num_of_section,
                    "section_time": section_time,
                    "subsection_num": subsection_num,
                    "subsection_name": sub_name,
                    "subsection_time": formatted_time,
                }
            )
            subsection_num += 1

    return results


# UDF 등록
schema = ArrayType(
    StructType(
        [
            StructField("section_num", IntegerType()),
            StructField("section_name", StringType()),
            StructField("num_of_section", IntegerType()),
            StructField("section_time", StringType()),
            StructField("subsection_num", IntegerType()),
            StructField("subsection_name", StringType()),
            StructField("subsection_time", StringType()),
        ]
    )
)

parse_curri_udf = udf(parse_curri, schema)

# DataFrame에 UDF 적용
cleaned_curri_df = exploded_df.select(
    regexp_replace(
        regexp_replace(
            regexp_replace(
                regexp_replace(
                    regexp_replace(col("course.curri"), r"\s+", " "), r"\n", ""
                ),
                r" ,",
                "",
            ),
            r", 미리보기",
            "",
        ),
        r" ∙ ",
        ",",
    ).alias("curri"),
    col("course.course_link").alias("course_link"),  # course_link 추가
)

parsed_curri_df = cleaned_curri_df.withColumn("parsed_curri", parse_curri_udf("curri"))

# 결과를 열별로 분리하여 DataFrame 생성
section_df = parsed_curri_df.select(
    explode("parsed_curri").alias("parsed"), "course_link"
).select(
    col("parsed.section_num").alias("section_num"),
    col("parsed.section_name").alias("section_name"),
    col("parsed.num_of_section").alias("num_of_section"),
    col("parsed.section_time").alias("section_time"),
    col("parsed.subsection_num").alias("subsection_num"),
    col("parsed.subsection_name").alias("subsection_name"),
    col("parsed.subsection_time").alias("subsection_time"),
    col("course_link"),  # course_link 유지
)

# COURSE_ID를 section_df에 추가하기 위해 조인
section_df = section_df.join(
    courses_df.select("course_name", "course_link"), on="course_link", how="left"
)


# 중요한 문장 1개 추출
def text_summary(text):
    if not isinstance(text, str):
        return None
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
    n = len(sentences)
    if n == 0:
        return None
    else:
        return sentences[n // 2]  # 중간 문장만 반환


extract_udf = udf(text_summary, StringType())

# 새로운 DataFrame에 중요한 문장 추가
result_df = courses_df.withColumn("text_summary", extract_udf(col("text")))

# 필요한 컬럼만 선택하여 result_df 생성
result_df = result_df.select("course_name", "text_summary")


def review_summary(review):
    try:
        if not review:
            return []
        sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", review)
        n = len(sentences)
        if n == 0:
            return []
        if n == 1:
            return [sentences[0]]
        if n == 2:
            return [sentences[0], sentences[1]]
        else:
            # 첫 번째 문장, 중간 문장, 마지막 문장 추출
            return [sentences[0], sentences[n // 2], sentences[-1]]
    except Exception as e:
        # 예외 발생 시 빈 리스트 반환
        return []


extract_udf = udf(review_summary, ArrayType(StringType()))

# 새로운 DataFrame에 중요한 문장 추가
review_df = courses_df.withColumn("review_summary", extract_udf(col("review")))

# 결과 출력
review_df = review_df.select("course_name", "review_summary")

# 데이터 캐싱
courses_df2 = (
    courses_df.dropDuplicates(["course_name"]).repartition("course_link").cache()
)
result_df2 = (
    result_df.dropDuplicates(["course_name"]).repartition("course_name").cache()
)

# courses_df와 result_df 조인
final_df = courses_df2.join(result_df2, on="course_name", how="left")

# 필요한 컬럼만 선택하여 COURSE 데이터프레임 생성
COURSE = final_df.select(
    col("category_name"),
    col("sub_category_name").alias("subcategory_name"),
    col("tag"),
    col("course_name").alias("course_title"),
    col("course_link").alias("url"),
    col("text_summary").alias("summary"),
    col("num_of_lecture"),
    col("num_of_stud"),
    col("star").alias("rate"),
    col("img"),
    col("instructor"),
    col("price").alias("reg_price"),
    col("dis_price").alias("dis_price"),
)

# TAG 데이터프레임 생성
TAG = courses_df.select("course_name", explode("tag").alias("tag")).select(
    col("course_name").alias("course_title"), col("tag")
)

REVIEW_SUMMARY = review_df.select(
    col("course_name").alias("course_title"), col("review_summary")
)

# 필요한 컬럼만 선택하여 SECTION 데이터프레임 생성 + (course_name, section_num)에 대하여 중복 제거
SECTION = section_df.select(
    col("course_name").alias("course_title"),
    col("section_num"),
    col("section_name"),
    col("num_of_section").alias("num_of_lecture"),
    col("section_time").alias("running_time"),
).dropDuplicates(["course_title", "section_num"])

# SUBSECTION 데이터프레임 생성
SUBSECTION = section_df.select(
    col("course_name").alias("course_title"),
    col("subsection_num"),
    col("subsection_name"),
    col("section_num"),
    col("subsection_time").alias("running_time"),
)

# DB 파트
unique_category = COURSE.select("category_name").distinct()
unique_subcategory = COURSE.select("subcategory_name", "category_name").distinct()

# spark = SparkSession.getActiveSession()
# if spark is not None:
#     spark.stop()
spark = (
    SparkSession.builder.appName("postgresql session")
    .config("spark.jars.packages", "org.postgresql:postgresql:42.2.18")
    .getOrCreate()
)

PLATFORM_ID = 1
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

# spark.stop()# category_id, subcategory_name으로 식별하여 기존에 없던 subcategory만 남긴다.
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

SECTION_WITH_ID = SECTION.join(
    ID_TITLE_FROM_COURSE, on="course_title", how="inner"
).drop("course_title")
SECTION = SECTION_WITH_ID.select(["course_id", "section_num", "section_name"])

# SECTION 테이블에 삽입
SECTION.foreachPartition(
    lambda partition: insert_section_partition(partition, "SECTION", db_props, db_url)
)

SUBSECTION_WITH_ID = SUBSECTION.join(
    ID_TITLE_FROM_COURSE, on="course_title", how="inner"
).drop("course_title")
SUBSECTION = SUBSECTION_WITH_ID.withColumn(
    "subsection_name", substring(col("subsection_name"), 1, 100)
).select(["course_id", "section_num", "subsection_num", "subsection_name"])

# SUBSECTION 테이블에 삽입
SUBSECTION.foreachPartition(
    lambda partition: insert_subsection_partition(
        partition, "SUBSECTION", db_props, db_url
    )
)
