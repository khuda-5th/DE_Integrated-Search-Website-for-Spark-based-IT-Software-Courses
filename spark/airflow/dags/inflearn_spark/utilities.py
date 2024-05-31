from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from pyspark.sql.functions import explode, col
import re
import psycopg2

PLATFORM_ID = 1
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