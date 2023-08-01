from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import datetime as dt
from datetime import datetime, timedelta
import requests
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'daily_earthquakes',
    default_args=default_args,
    description='DAG to download, upload, and process daily earthquake data from USGS',
    schedule_interval='@daily',
    catchup=False,
)

# Defining variables to query USGS catalog
today = dt.datetime.today().strftime('%Y-%m-%d')
yesterday = (dt.datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime={yesterday}&endtime={today}"
destination_path = f"/home/kjal/zoomcamp_project/daily_events/{yesterday}_events.csv"

# Defining directory variables
bucket_name=os.environ.get("GCS_DAILY_BUCKET")
gs_bucket = f'gs://{bucket_name}'
spark_script_path = '/home/kjal/zoomcamp_project/daily_processing.py'

# Callable function to download files using a query
def daily_download(url, destination_path):

    def download_file(url, destination_path):
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            with open(destination_path, 'wb') as f:
                f.write(response.content)
            print(f"File downloaded successfully to: {destination_path}")
        else:
            print(f"Failed to download file from URL: {url}. Status Code: {response.status_code}")

    download_file(url, destination_path)

# Task to download the file using a bash script
download_task = PythonOperator(
    task_id='download_daily_events',
    python_callable=daily_download,  
    op_args=[url, destination_path],
    dag=dag,
)

# Task to upload the file to Google Cloud Storage
upload_task = BashOperator(
    task_id='upload_to_gcs',
    bash_command=f'gsutil cp -r {destination_path} {gs_bucket}',
    dag=dag
)

# Task to process the file using PySpark
process_task = BashOperator(
    task_id='process_daily_events',
    bash_command=f"python3 {spark_script_path}", 
    dag=dag,
)

# Defining task dependencies
download_task >> upload_task >> process_task
