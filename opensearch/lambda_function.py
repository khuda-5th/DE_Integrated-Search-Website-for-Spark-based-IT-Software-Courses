import json
import boto3
import io
from datetime import datetime
import traceback
from opensearchpy import OpenSearch, RequestsHttpConnection

# Settings for access S3
ACCESS_KEY = {ACCESS_KEY}
SECRET_KEY = {SECRET_KEY}
s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

# Settings for access OpenSearch
host = {host}  # host URL of opensearch instance without https
opensearch_auth = ({ID}, {PASSWORD}) # auth for opensearch
client = OpenSearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = opensearch_auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    pool_maxsize = 20,
)

# Define Exception Classes
class HTTPException(Exception):
    def __init__(self, status_code, message):
        Exception.__init__(self)
        self.message = json.dumps(
            {
                'statusCode': status_code,
                f'{self.__class__.__name__}' : message
            }
        )

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message
    
class InternalServerException(HTTPException):
    def __init__(self,message):
        HTTPException.__init__(self, 500, message)

def http_response(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
            result = {
                'statusCode': 200,
                'body': json.dumps('Success for lambda execution')
            }
        except HTTPException as e:
            result = str(e)
        except Exception as e:
            print(f'[ERROR] {datetime.now()} {e}')
            print(traceback.format_exc())
            result = str(InternalServerException('Internal Server Error'))
        return result
    return wrapper

@http_response
def lambda_handler(event, context):
    records = event['Records']
        
    for record in records:
        region = record['awsRegion']
        bucket_name = record['s3']['bucket']['name']
        file_name = record['s3']['object']['key']
            
        obj = s3.get_object(Bucket=bucket_name, Key = file_name)
            
        file_content = obj['Body'].read().decode('utf-8')
            
        if file_name.find('inflearn') != -1:
            inflearn_doc_create(file_content)
        elif file_name.find('fastcampus') != -1:
            fastcampus_doc_create(file_content)
        elif file_name.find('codeit') != -1:
            codeit_document_create(file_content)

def inflearn_doc_create(file_content):
    try :
        lines = file_content.splitlines() # 한줄씩 문자열 읽기 
        for line in lines:
                data = json.loads(line)
                # 필요한 정보 추출
                category_name = data['category'][0]['category_name']
                sub_category_name = data['category'][0]['sub_category']['sub_category_name']
                course_title = data['category'][0]['sub_category']['courses'][0]['title']
                course_link = data['category'][0]['sub_category']['courses'][0]['course_link']
                course_tag = data['category'][0]['sub_category']['courses'][0]['tag']
                course_text = data['category'][0]['sub_category']['courses'][0]['text']
                
                # preprocess for course_text
                cleaned_course_text = ''.join([word.strip() for word in course_text if word.strip()])
                
                document = {
                    "category_name": category_name,
                    "sub_category_name": sub_category_name,
                    "course_title": course_title ,
                    "course_tag": course_tag,
                    "course_text" : cleaned_course_text,
                    "course_link" : course_link
                }
                # POST to ES
                upload_document(client = client, index_name = "inflearn", json_data = document, course_title = document["course_title"])

    except :
        raise InternalServerException("Failed to process inflearn data as json") 

def fastcampus_doc_create(file) :
    try: 
        data = json.loads(file)
        for category in data['categories'] :
            for sub_category in category['sub_categories']:
                for course in sub_category['courses']:
                    title = course['title']
                    description = course['intro']
                    tags = course['tags']
                    url = course['course_url']
                    summary = course['summary']
                    parts = course['parts']
                    accordion = course['accordion']

                    doc = {
                            "lectureTitle" : title,
                            "lectureDescription" : description,
                            "lectureTag" : tags,
                            "lectureURL" : url,
                            "lectureSummary" : summary,
                            "lecutreParts" : parts,
                            "lectureAccordion" : accordion,
                    }
                    # POST to ES
                    upload_document(client = client, index_name = "fastcampus", json_data = doc, course_title = doc["lectureTitle"])
    
    except :
        raise InternalServerException("Failed to process fastcampus data as json")   

def codeit_document_create(file) :
    try :
        data = json.loads(file)
        for bigcategory in data :
            categoryName = bigcategory['big_categ']
            for subcategory in bigcategory['sub_categs'] :
                subcategoryName = subcategory['sub_categ']
                for lecture in subcategory['lectures'] :
                    if lecture == None :
                        continue
                    doc = {
                            "lectureCategory" : categoryName,
                            "lectrueSubCategory" : subcategoryName,
                            "lectureTitle" : lecture['title'],
                            "lectureSummary" : lecture['summary'],
                            "lectrueDifficulty" : lecture['difficulty'],
                            "lectureCurriculum" : lecture['curriculum'],
                            "lectureRoadmap" : lecture['roadmaps'],
                            "lectureRecommend" : lecture['recommend'],
                            "lectureLink" : lecture['link']
                    }
                    # POST to ES
                    upload_document(client = client, index_name = "codeit", json_data = doc, course_title = doc["lectureTitle"])
    except  :
        raise InternalServerException("Failed to process codeit data as json")
              
def upload_document(client, index_name, json_data, course_title):
    try :
        response = client.index(
            index = index_name,
            body = json_data,
            id = course_title,
            refresh = True
        )
    except :
        raise InternalServerException('Failed to upload document in OpenSearch')