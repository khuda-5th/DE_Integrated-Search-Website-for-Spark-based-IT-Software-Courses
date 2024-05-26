import boto3
from datetime import datetime
from airflow.hooks.S3_hook import S3Hook
from airflow.utils.email import send_email
import os

session = boto3.Session(
    aws_access_key_id='{access_key}',
    aws_secret_access_key='{secret_access_key}',
    region_name='ap-northeast-2'
)
ec2 = session.resource('ec2', region_name='ap-northeast-2')
# 인프런, 패스트캠퍼스, 코드잇 순서
instance_ids = ['i-0ebaf5f5d9222de5d', 'i-0dd6a1691784a86ca', 'i-0e2c82f4730912f6f']
PEM_KEY_FILE_PATH = "C:/Users/dbgpw/Downloads/khuda5th-de.pem"
TODAY = datetime.now().strftime("%y%m%d")

# 크롤링/스파크 인스턴스 실행 - 3개
def start_crawl_spark_ec2_instance():
    # 인스턴스 시작
    instances = ec2.instances.filter(InstanceIds=instance_ids)
    for instance in instances:
        instance.start()
        print(f"Starting EC2 instance: {instance.id}")
    # 모든 인스턴스가 시작 완료까지 대기
    for instance in instances:
        instance.wait_until_running()
        print(f"EC2 instance {instance} is running")

# 크롤링/스파크 인스턴스 중단 - 3개
def stop_crawl_spark_instance():
    instances = ec2.instances.filter(InstanceIds=instance_ids)
    instances.stop()

    for instance in instances:
        instance.wait_until_stopped()
        print(f"Instance {instance.id} is now stopped")

# 인스턴스 IP 획득
def get_instance_ip(**kwargs):
    instances = ec2.instances.filter(InstanceIds=instance_ids)
    ips = []
    for instance in instances:
        ips.append(instance.public_ip_address)
    kwargs['ti'].xcom_push(key='inflearn_ip', value=ips[0])
    kwargs['ti'].xcom_push(key='fastcampus_ip', value=ips[1])
    kwargs['ti'].xcom_push(key='codeit_ip', value=ips[2])
    
# def run_command(**kwargs):
#     inflearn_cmd = f"""
#     export ip_inflearn="{{ ti.xcom_pull(task_ids='get-run-crawl-cmd', key='inflearn_ip') }}" && \
#             ssh -o StrictHostKeyChecking=no -i ~/airflow/khuda5th-de.pem ubuntu@$ip_inflearn 'mkdir -p ~/.ssh && echo $(cat ~/.ssh/id_rsa.pub) >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys' && ssh -i /home/ubuntu/.ssh/id_rsa ubuntu@$ip_inflearn && cd /home/ubuntu/Inflearn && scrapy crawl inflearn && exit && scp ubuntu@$ip_inflearn:/home/ubuntu/Inflearn/{TODAY}_inflearn_entire.json ./data/inflearn/entire/raw/{TODAY}_inflearn_entire.json
#             """
#     kwargs['ti'].xcom_push(key='inflearn_cmd', value=inflearn_cmd)

#     fastcampus_cmd = f"""
#     export ip_fastcampus="{{ ti.xcom_pull(task_ids='get-run-crawl-cmd', key='fastcampus_ip') }}" && \
#     ssh -o StrictHostKeyChecking=no -i /home/ubuntu/airflow/khuda5th-de.pem ubuntu@$ip_fastcampus 'mkdir -p ~/.ssh && echo $(cat ~/.ssh/id_rsa.pub) >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys' && ssh -i /home/ubuntu/.ssh/id_rsa ubuntu@$ip_fastcampus && cd /home/ubuntu/fastcampus_crawling &&  python3 ./entire_course.py && exit && scp ubuntu@$ip_fastcampus:/home/ubuntu/data/fastcampus/entire/raw/{TODAY}_fastcampus_entire.json/ ./data/inflearn/entire/raw/{TODAY}_fastcampus_entire.json
#             """
#     kwargs['ti'].xcom_push(key='fastcampus_cmd', value=fastcampus_cmd)
    
#     codeit_cmd = f"""
#     export ip_codeit="{{ ti.xcom_pull(task_id='get-run-crawl-cmd', key='codeit_ip') }}"&& \
#     ssh -o StrictHostKeyChecking=no -i /home/ubuntu/airflow/khuda5th-de.pem ubuntu@$ip_codeit 'mkdir -p ~/.ssh && echo $(cat ~/.ssh/id_rsa.pub) >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys' && ssh -i /home/ubuntu/.ssh/id_rsa ubuntu@$ip_codeit && cd /home/ubuntu/codeit && python3 ./codeit_lectures.py && exit && scp ubuntu@$ip_codeit:/home/ubuntu/data/codeit/entire/raw/{TODAY}_codeit_entire.json ./data/inflearn/entire/raw/{TODAY}_codeit_entire.json
#             """
#     kwargs['ti'].xcom_push(key='codeit_cmd', value=codeit_cmd)

inflearn_cmd = f"""
export ip_inflearn="{{ ti.xcom_pull(task_ids='get-run-crawl-cmd', key='inflearn_ip') }}" 
ssh -o StrictHostKeyChecking=no -i ~/airflow/khuda5th-de.pem ubuntu@$ip_inflearn << 'EOF'
mkdir -p ~/.ssh
echo $(cat ~/.ssh/id_rsa.pub) >> ~/.ssh/authorized_keys 
chmod 600 ~/.ssh/authorized_keys
EOF

ssh -i /home/ubuntu/.ssh/id_rsa ubuntu@$ip_inflearn << "EOF"
cd /home/ubuntu/Inflearn
scrapy crawl inflearn
exit
EOF

scp ubuntu@$ip_inflearn:/home/ubuntu/Inflearn/{TODAY}_inflearn_entire.json ./data/inflearn/entire/raw/{TODAY}_inflearn_entire.json
"""

fastcampus_cmd = f"""
export ip_fastcampus="{{ ti.xcom_pull(task_ids='get-run-crawl-cmd', key='fastcampus_ip') }}"
ssh -o StrictHostKeyChecking=no -i ~/airflow/khuda5th-de.pem ubuntu@$ip_fastcampus << 'EOF'
mkdir -p ~/.ssh && echo $(cat ~/.ssh/id_rsa.pub) >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys'
EOF

ssh -i /home/ubuntu/.ssh/id_rsa ubuntu@$ip_fastcampus << "EOF"
cd /home/ubuntu/fastcampus_crawling
python3 ./entire_course.py
exit

scp ubuntu@$ip_fastcampus:/home/ubuntu/data/fastcampus/entire/raw/{TODAY}_fastcampus_entire.json/ ./data/inflearn/entire/raw/{TODAY}_fastcampus_entire.json
"""

codeit_cmd = f"""
export ip_codeit="{{ ti.xcom_pull(task_id='get-run-crawl-cmd', key='codeit_ip') }}"
ssh -o StrictHostKeyChecking=no -i /home/ubuntu/airflow/khuda5th-de.pem ubuntu@$ip_codeit << 'EOF'
mkdir -p ~/.ssh && echo $(cat ~/.ssh/id_rsa.pub) >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
EOF

ssh -i /home/ubuntu/.ssh/id_rsa ubuntu@$ip_codeit << "EOF"
cd /home/ubuntu/codeit
python3 ./codeit_lectures.py
exit

scp ubuntu@$ip_codeit:/home/ubuntu/data/codeit/entire/raw/{TODAY}_codeit_entire.json ./data/inflearn/entire/raw/{TODAY}_codeit_entire.json
"""



def upload_to_s3() :
    hook = S3Hook('aws_connection') # Airflow UI에서 aws connections 설정
    
    bucket_name = 'khudade-5th' # s3에서 버킷네임 설정
    filenames = {
        'fastcampus': f'/opt/khudade/data/fastcampus/entire/raw/{TODAY}_fastcampus_entire.json',
        'inflearn': f'/opt/khudade/data/inflearn/entire/raw/{TODAY}_inflearn_entire.json',
        'codeit': f'/opt/khudade/data/codeit/entire/raw/{TODAY}_codeit_entire.json',
    }

    s3_dirs = {
        'fastcampus': f"data/fastcampus/entire/raw/{TODAY}_fastcampus_entire.json",
        'inflearn': f"data/inflearn/entire/raw/{TODAY}_inflearn_entire.json",
        'codeit': f"data/codeit/entire/raw/{TODAY}_codeit_entire.json",
    }

    for key, filename in filenames.items():
        try:
            if os.path.isfile(filename):
                hook.load_file(filename=filename, key=s3_dirs[key], bucket_name=bucket_name, replace=True)
                print(f"Uploaded {filename} to S3 as {s3_dirs[key]}")
            else:
                print(f"File {filename} does not exist, skipping upload.")
        except Exception as e:
            print(f"An error occurred while uploading {filename} to S3: {e}")

# 각 task의 성공/실패 여부를 이메일로 받기 -> airflow smtp 환경변수 설정
def send_email_on_completion(**context):
    # Define the tasks and their statuses
    tasks = {
        'inflearn_chk_task': 'inflearn-crawling',
        'fastcampus_chk_task': 'fastcampus-crawling',
        'codeit_chk_task': 'codeit-crawling',
    }
    # Fetch and determine the status of each task
    status_summary = {}
    for task_id, task_name in tasks.items():
        status = context['ti'].xcom_pull(task_ids=task_id, key='return_value')
        status_summary[task_name] = "Success" if status == 0 else "Failed"

    # Create email subject and body
    subject = "[Entire] Airflow Task Completion Status"
    body = "Entire Course Crawling Task Completion Summary:\n\n"
    for task_name, status in status_summary.items():
        body += f"{task_name}: {status}\n"

    # Send email
    send_email(to='dbgpwl34@gmail.com', subject=subject, html_content=body)
