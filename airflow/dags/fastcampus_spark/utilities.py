from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from pyspark.sql.functions import explode, col
import re
import psycopg2

PLATFORM_ID = 2


def process_tags(df, spark):
    # 각 행마다 단어를 분리하고, 단어 빈도를 계산하여 결과를 저장할 리스트
    final_words_per_row = []

    # 각 행에 대해 반복 처리
    for row in df.collect():
        tags = row.tags

        if not tags:  # tags가 빈 배열인 경우
            final_words = []  # 빈 배열로 처리
        else:
            df_row = spark.createDataFrame([(tags,)], ["tags"])
            df_exploded = df_row.withColumn("word", explode(col("tags")))
            df_word_counts = (
                df_exploded.groupBy("word").count().orderBy(col("count").desc())
            )

            # 단어 리스트 생성
            words = [r["word"] for r in df_word_counts.collect()]

            if len(words) > 1:
                # 단어 임베딩 생성 (예: TF-IDF 사용)
                vectorizer = TfidfVectorizer(
                    tokenizer=lambda x: x, preprocessor=lambda x: x, token_pattern=None
                )
                word_vectors = vectorizer.fit_transform(words).toarray()

                # KMeans 클러스터링
                num_clusters = min(5, len(words))  # 최대 5개의 클러스터
                kmeans = KMeans(n_clusters=num_clusters, random_state=0, n_init=10).fit(
                    word_vectors
                )

                # 클러스터링 결과에서 대표 단어 선택
                clusters = {}
                for word, label in zip(words, kmeans.labels_):
                    if label not in clusters:
                        clusters[label] = []
                    clusters[label].append(word)

                # 각 클러스터에서 대표 단어 선택 (여기서는 첫 번째 단어 선택)
                representative_words = [cluster[0] for cluster in clusters.values()]

                # 최대 5개의 단어 선택
                final_words = representative_words[:5]
            else:
                final_words = words  # 단어가 1개일 경우 해당 단어 사용

        final_words_per_row.append((tags, final_words))
    return final_words_per_row


# 정규 표현식을 사용하여 accordion에서 숫자와 제목을 추출하는 UDF 정의
def extract_subsection_number_and_title(accordion):
    result = []
    for item in accordion:
        match = re.match(r"(\d+)\.?\s*(.*)", item)
        if match:
            result.append((int(match.group(1)), match.group(2)))
    return result


# 정규 표현식을 사용하여 Part 번호와 제목을 추출하는 UDF 정의
def extract_part_number_and_title(part):
    match = re.match(r"Part\s*?(\d+)\.\s*(.*)", part)
    if match:
        return (int(match.group(1)), match.group(2))
    return (None, part)


def insert_new_categories(rows, db_props, db_url):
    try:
        conn = psycopg2.connect(
            dbname=db_url.split("/")[-1],
            user=db_props["user"],
            password=db_props["password"],
            host=db_url.split("//")[1].split(":")[0],
            port=db_url.split(":")[-1].split("/")[0],
        )
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO CATEGORY (category_name, platform_id)
        VALUES (%s, %s);
        """

        for row in rows:
            cursor.execute(insert_query, (row.category_name, PLATFORM_ID))

        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()


def insert_new_subcategories(rows, db_props, db_url):
    try:
        conn = psycopg2.connect(
            dbname=db_url.split("/")[-1],
            user=db_props["user"],
            password=db_props["password"],
            host=db_url.split("//")[1].split(":")[0],
            port=db_url.split(":")[-1].split("/")[0],
        )
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO SUBCATEGORY (category_id, subcategory_name)
        VALUES (%s, %s);
        """

        for row in rows:
            cursor.execute(insert_query, (row.category_id, row.subcategory_name))

        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()


def insert_course_partition(rows, table_name, db_props, db_url):
    try:
        conn = psycopg2.connect(
            dbname=db_url.split("/")[-1],
            user=db_props["user"],
            password=db_props["password"],
            host=db_url.split("//")[1].split(":")[0],
            port=db_url.split(":")[-1].split("/")[0],
        )
        cursor = conn.cursor()

        insert_query = f"""
        INSERT INTO {table_name} (course_title, summary, url, img, reg_price, dis_price, subcategory_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url)
        DO UPDATE SET
            course_title = EXCLUDED.course_title,
            summary = EXCLUDED.summary,
            img = EXCLUDED.img,
            reg_price = EXCLUDED.reg_price,
            dis_price = EXCLUDED.dis_price,
            updated_at = NOW();
        """

        for row in rows:
            # 강제로 summary를 350자로 자르기
            summary = row.summary[:350] if row.summary else ""
            cursor.execute(
                insert_query,
                (
                    row.course_title,
                    summary,
                    row.url,
                    row.img,
                    row.reg_price,
                    row.dis_price,
                    row.subcategory_id,
                ),
            )

        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()


def insert_tag_partition(rows, table_name, db_props, db_url):
    try:
        conn = psycopg2.connect(
            dbname=db_url.split("/")[-1],
            user=db_props["user"],
            password=db_props["password"],
            host=db_url.split("//")[1].split(":")[0],
            port=db_url.split(":")[-1].split("/")[0],
        )
        cursor = conn.cursor()

        insert_query = f"""
        INSERT INTO {table_name} (course_id, tag)
        VALUES (%s, %s)
        ON CONFLICT (course_id, tag)
        DO UPDATE SET
            tag = EXCLUDED.tag,
            updated_at = NOW();
            
        """

        for row in rows:
            cursor.execute(insert_query, (row.course_id, row.tag))

        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()


def insert_section_partition(rows, table_name, db_props, db_url):
    try:
        conn = psycopg2.connect(
            dbname=db_url.split("/")[-1],
            user=db_props["user"],
            password=db_props["password"],
            host=db_url.split("//")[1].split(":")[0],
            port=db_url.split(":")[-1].split("/")[0],
        )
        cursor = conn.cursor()

        insert_query = f"""
        INSERT INTO {table_name} (course_id, section_num, section_name)
        VALUES (%s, %s, %s)
        ON CONFLICT (course_id, section_num)
        DO UPDATE SET
            section_num = EXCLUDED.section_num,
            section_name = EXCLUDED.section_name,
            updated_at = NOW();
        """

        for row in rows:
            cursor.execute(
                insert_query, (row.course_id, row.section_num, row.section_name)
            )

        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()


def insert_subsection_partition(rows, table_name, db_props, db_url):
    try:
        conn = psycopg2.connect(
            dbname=db_url.split("/")[-1],
            user=db_props["user"],
            password=db_props["password"],
            host=db_url.split("//")[1].split(":")[0],
            port=db_url.split(":")[-1].split("/")[0],
        )
        cursor = conn.cursor()

        insert_query = f"""
        INSERT INTO {table_name} (course_id, section_num, subsection_num, subsection_name)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (course_id, section_num, subsection_num)
        DO UPDATE SET
            subsection_num = EXCLUDED.subsection_num,
            subsection_name = EXCLUDED.subsection_name,
            updated_at = NOW();
        """

        for row in rows:
            cursor.execute(
                insert_query,
                (
                    row.course_id,
                    row.section_num,
                    row.subsection_num,
                    row.subsection_name,
                ),
            )

        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()


# 단순 SQL 쿼리 함수
def execute_sql_query(query, db_url, db_properties):
    connection = psycopg2.connect(
        dbname=db_url.split("/")[-1],
        user=db_properties["user"],
        password=db_properties["password"],
        host=db_url.split("//")[1].split(":")[0],
        port=db_url.split(":")[-1].split("/")[0],
    )
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


# NEW_COURSE테이블에 삽입
def insert_new_course_partition(rows, table_name, db_props, db_url):
    try:
        conn = psycopg2.connect(
            dbname=db_url.split("/")[-1],
            user=db_props["user"],
            password=db_props["password"],
            host=db_url.split("//")[1].split(":")[0],
            port=db_url.split(":")[-1].split("/")[0],
        )
        cursor = conn.cursor()

        insert_query = f"""
        INSERT INTO {table_name} (course_id, course_title, summary, url, img, new_img, reg_price, dis_price, subcategory_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url)
        DO UPDATE SET 
            course_id = EXCLUDED.course_id,
            course_title = EXCLUDED.course_title,
            summary = EXCLUDED.summary,
            url = EXCLUDED.url,
            img = EXCLUDED.img,
            new_img = EXCLUDED.new_img,
            reg_price = EXCLUDED.reg_price,
            dis_price = EXCLUDED.dis_price,
            updated_at = NOW();
        """

        for row in rows:
            cursor.execute(
                insert_query,
                (
                    row.course_id,
                    row.course_title,
                    row.summary,
                    row.url,
                    row.img,
                    row.new_img,
                    row.reg_price,
                    row.dis_price,
                    row.subcategory_id,
                ),
            )

        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()


# 태그 DB 삽입 함수
def insert_tag_partition(rows, table_name, db_props, db_url):
    try:
        conn = psycopg2.connect(
            dbname=db_url.split("/")[-1],
            user=db_props["user"],
            password=db_props["password"],
            host=db_url.split("//")[1].split(":")[0],
            port=db_url.split(":")[-1].split("/")[0],
        )
        cursor = conn.cursor()

        insert_query = f"""
        INSERT INTO {table_name} (course_id, tag)
        VALUES (%s, %s)
        ON CONFLICT (course_id, tag)
        DO UPDATE SET
            tag = EXCLUDED.tag,
            updated_at = NOW();
            
        """

        for row in rows:
            cursor.execute(insert_query, (row.course_id, row.tag))

        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
