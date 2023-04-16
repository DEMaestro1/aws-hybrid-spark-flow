import datetime
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from pathlib import Path
import configparser

#Getting rds and s3 configurations from the configuration.conf file, usually secrets/keys are stored in secret management tools.
parser = configparser.ConfigParser()
p = Path(__file__).with_name('configuration.conf')
parser.read(p.absolute())

rdsEndPoint = parser.get('rds_config', 'rdsEndPoint')
rdsDB = parser.get('rds_config', 'rdsDB')
rdsDBDriver = parser.get('rds_config', 'rdsDBDriver')
rdsDBName = parser.get('rds_config', 'rdsDBName')
rdsTable = parser.get('rds_config', 'rdsTable')
rdsUser = parser.get('rds_config', 'rdsUser')
rdsPass = parser.get('rds_config', 'rdsPass')

s3Bucket = parser.get('s3_config', 's3Bucket')

#Jar required to store data in postgres DB or your choice of DB
dbJar = '/opt/bitnami/spark/jars/postgresql-42.6.0.jar'

#File paths
filePath = '/usr/local/files'
fileName = 'Business_Licenses.csv'
filePath = f'{filePath}/{fileName}'
s3RawSink = f'raw/{fileName}'
s3StageSink = f'stage/{fileName}'
sparkFilepaths = '/opt/bitnami/spark/tasks/'


# DAG arguments
defaultArgs = {
    'owner': 'DEMaestro1',
    'depends_on_past': False,
    'start_date': datetime.datetime(2023, 1, 1),
    'retries': 0
}

# DAG definition
with DAG('load_data_RDS',
         schedule_interval ='@daily',
         default_args = defaultArgs,
         catchup = False) as dag:

    #simple curl command to grab a file     
    getFile = BashOperator(
        task_id = 'getFile',
        bash_command = f"""curl -o {filePath} https://data.cityofchicago.org/api/views/uupf-x98q/rows.csv?accessType=DOWNLOAD"""
    )

    #uploading the file to s3
    loadFileToS3 = BashOperator(
        task_id = 'loadFileToS3',
        bash_command = f"""cd /opt/bitnami/spark/tasks; python -c 'import loadFileToS3;loadFileToS3.upload_file("{filePath}", "{s3Bucket}", "{s3RawSink}")'"""
    )

    #General transformation process on the dataset
    transformData = SparkSubmitOperator(
        task_id = 'transformData',
        application = f'{sparkFilepaths}/transformData.py', 
        name = 'transformData',
        conn_id = 'spark_default',
        jars = dbJar,
        driver_class_path = dbJar,
        application_args = [s3Bucket, s3RawSink, s3StageSink]
        )
     
    #Passing the postgres jar as well as the configurations for rds and s3  
    loadFiletoRDS = SparkSubmitOperator(
        task_id = 'loadFiletoRDS',
        application = f'{sparkFilepaths}/loadToRDS.py', 
        name = 'loadFiletoRDS',
        conn_id = 'spark_default',
        jars = dbJar,
        driver_class_path = dbJar,
        application_args = [s3Bucket, s3StageSink, rdsEndPoint, rdsDB, rdsDBDriver, rdsDBName, rdsTable, rdsUser, rdsPass]
        )     


    # set tasks relations (the order the tasks are executed)
    getFile >> loadFileToS3 >> transformData >> loadFiletoRDS