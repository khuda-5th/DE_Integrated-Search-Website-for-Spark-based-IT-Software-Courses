from pyspark.sql.functions import explode, col
import re
import psycopg2

PLATFORM_ID = 3

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
        INSERT INTO {table_name} (course_title, summary, url, subcategory_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (url)
        DO UPDATE SET
            course_title = EXCLUDED.course_title,
            summary = EXCLUDED.summary,
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
                    row.subcategory_id,
                ),
            )

        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def insert_review_summary_partition(rows, table_name, db_props, db_url):
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
        INSERT INTO {table_name} (course_id, summary)
        VALUES (%s, %s)
        ON CONFLICT (course_id, summary)
        DO UPDATE SET
            summary = EXCLUDED.summary,
            updated_at = NOW();
        """

        for row in rows:
            cursor.execute(
                insert_query, (row.course_id, row.summary)
            )

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