from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.trigger_rule import TriggerRule
from modules import *

import sys, os
sys.path.append(os.getcwd())

from modules import *

default_args = {
    'owner': 'khudade',
    'depends_on_past': False,
    'email': ['dbgpwl34@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=30),
}

dag_args = dict(
    dag_id='entire-course-crawling-upload',
    default_args=default_args,
    description='KHUDA 5th de-project DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime.today(),
    tags=['entire-course'],
)


# 전체 강의 크롤링
with DAG( **dag_args ) as dag:
    # Running three EC2 instances
    start_ec2 = PythonOperator(
        task_id = 'start-crawling-instance',
        python_callable = start_crawl_spark_ec2_instance
    )

    # Obtaining instance IP
    get_instance_ip_task = PythonOperator(
        task_id = 'get-instance-ip',
        provide_context=True,
        python_callable = get_instance_ip
    )

    #make_env = BashOperator(
    #    task_id = 'make-environment-variable',
    #    bash_command = 'echo "instance_ip1={{ ti.xcom_pull(task_ids=\'get-instance-ip\', key=\'instance_ip\') }}"[0] > ./.env && echo "instance_ip2={{ ti.xcom_pull(task_ids=\'get-instance-ip\', key=\'instance_ip\') }}"[1] > ./.env && echo "instance_ip3={{ ti.xcom_pull(task_ids=\'get-instance-ip\', key=\'instance_ip\') }}"[2] > ./.env'
    #)

    # get crawling command
    get_run_crawl_cmd = PythonOperator(
        task_id = 'get-run-crawl-cmd',
        provide_context=True,
        python_callable = run_command
    )

    # run command - inflearn
    inflearn_task = BashOperator(
        task_id = 'inflearn-crawling',
        bash_command = inflearn_cmd,
        execution_timeout=timedelta(hours=3)
    )

    # run command - fastcampus
    fastcampus_task = BashOperator(
        task_id = 'fastcampus-crawling',
        bash_command = fastcampus_cmd,
        execution_timeout=timedelta(hours=3)
    )

    # run command - codeit
    codeit_task = BashOperator(
        task_id = 'codeit-crawling',
        bash_command = codeit_cmd,
        execution_timeout=timedelta(hours=3)
    )

    # inflearn file sensor
    inflearn_chk_task = FileSensor(
        task_id = 'file-sense-inflearn',
        filepath = f'/opt/airflow/data/inflearn/entire/raw/{datetime.today().strftime("%y%m%d")}_inflearn_entire.json',
        mode = 'reschedule',
        poke_interval = 60,
        timeout = 600,
        trigger_rule=TriggerRule.ALL_DONE
    )

    # fastcampus file sensor
    fastcampus_chk_task = FileSensor(
        task_id = 'file-sense-fastdcampus',
        filepath = f'/opt/airflow/data/fastcampus/entire/raw/{datetime.today().strftime("%y%m%d")}_fastcampus_entire.json',
        mode = 'reschedule',
        poke_interval = 60,
        timeout = 600,
        trigger_rule=TriggerRule.ALL_DONE
    )
    
    # codeit file sensor
    codeit_chk_task = FileSensor(
        task_id = 'file-sense-codeit',
        filepath = f'/opt/airflow/data/codeit/entire/raw/{datetime.today().strftime("%y%m%d")}_codeit_entire.json',
        mode = 'reschedule',
        poke_interval = 60,
        timeout = 600,
        trigger_rule=TriggerRule.ALL_DONE
    )

    # Midterm check
    midterm_check = BashOperator(
        task_id = 'Midterm-check',
        bash_command = "echo 'file detection completed'",
        trigger_rule=TriggerRule.ALL_DONE
    )

    # upload raw json to s3
    upload_to_s3 = PythonOperator(
        task_id='upload-raw-data-to-s3',
        python_callable=upload_to_s3,
    )

    # email 
    send_task_status_email = PythonOperator(
        task_id = 'send-email',
        python_callable = send_email_on_completion,
        provide_context=True,
    )

    




    # stop three EC2 instances
    #stop_ec2 = PythonOperator(
    #    task_id = 'stop-crawling-instance',
    #    python_callable = stop_crawl_spark_instance
    #)



    # spark operator 
    # → docker-compose.yaml 파일에 Airflow 환경변수로 connections 설정 -> cluster 모드
    #submit_spark_job = SparkSubmitOperator(
    #    task_id='submit_spark_pipeline',
    #    application='/path/to/your/spark_application.py',  # Spark 애플리케이션의 경로
    #    conn_id='spark_default',  # Spark 연결 ID, Airflow UI에서 설정 가능
    #    conf={
    #        'spark.master': 'spark://your_spark_master:7077',
    #        'spark.executor.memory': '2g',
    #        'spark.executor.cores': '2',
    #        'spark.executor.instances': '4'  # 이 옵션으로 여러 노드에서 실행을 제어
    #    }
    #)

    start_ec2 >> get_instance_ip_task >> get_run_crawl_cmd >> [inflearn_task, fastcampus_task, codeit_task]
    inflearn_task >> inflearn_chk_task
    fastcampus_task >> fastcampus_chk_task
    codeit_task >> codeit_chk_task
    [inflearn_chk_task, fastcampus_chk_task, codeit_chk_task] >> midterm_check
    midterm_check >> [upload_to_s3, send_task_status_email]

