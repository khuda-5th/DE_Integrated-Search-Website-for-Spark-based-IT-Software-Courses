from opensearchpy import OpenSearch, RequestsHttpConnection
import os

host = os.getenv("OPENSEARCH_HOST")
region = os.getenv("OPENSEARCH_REGION")

service = os.getenv("OPENSEARCH_SERVICE")
opensearch_auth = os.getenv("OPENSEARCH_AUTH")
opensearch_url = os.getenv("OPENSEARCH_HOST")
opensearch_auth = os.getenv("OPENSEARCH_AUTH")


def get_opensearch_client():
    return OpenSearch(
        hosts=[
            {
                "host": opensearch_url,
                "port": 443,
            }
        ],
        http_auth=opensearch_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        # pool_maxsize=20,
    )


async def perform_search(client, index, query, filter_path, link_field):
    try:
        response = client.search(
            body=query,
            index=index,
            filter_path=filter_path,
        )
        return [
            {"link": hit["_source"][link_field], "score": hit["_score"]}
            for hit in response.get("hits", {}).get("hits", [])
        ]
    except Exception as e:
        print(f"Error searching {index}: {e}")
        return []


async def search_all_platforms(keyword):
    client = get_opensearch_client()

    fastcampus_query = {
        "query": {
            "multi_match": {
                "query": keyword,
                "fields": [
                    "lectureTitle^3",
                    "lectureDescription",
                    "lectureTag^2",
                    "lectureSummary",
                    "lecutreParts",
                    "lectureAccordion",
                ],
            }
        },
        "size": 15,
    }
    codeit_query = {
        "query": {
            "multi_match": {
                "query": keyword,
                "fields": [
                    "lectureCategory",
                    "lectrueSubCategory^2",
                    "lectureTitle^3",
                    "lectureSummary",
                    "lectrueDifficulty",
                    "lectureCurriculum",
                    "lectureRoadmap",
                    "lectureRecommend",
                ],
            }
        },
        "size": 15,
    }
    inflearn_query = {
        "query": {
            "multi_match": {
                "query": keyword,
                "fields": [
                    "category_name",
                    "sub_category_name",
                    "course_title^3",
                    "course_tag^2",
                    "course_text",
                ],
            }
        }
        # "size": 15,
    }

    inflearn_results = await perform_search(
        client,
        "inflearn",
        inflearn_query,
        ["hits.hits._source.course_link", "hits.hits._score"],
        "course_link",
    )

    fastcampus_results = await perform_search(
        client,
        "fastcampus",
        fastcampus_query,
        ["hits.hits._source.lectureURL", "hits.hits._score"],
        "lectureURL",
    )
    codeit_results = await perform_search(
        client,
        "codeit",
        codeit_query,
        ["hits.hits._source.lectureLink", "hits.hits._score"],
        "lectureLink",
    )

    # 클라이언트 종료
    client.transport.close()
    return fastcampus_results + codeit_results + inflearn_results
