from pyspark.sql import SparkSession
import configparser
import sys
import os

#Grabbing creds and paths from passed system argument
s3Bucket = sys.argv[1]
s3StageSink = sys.argv[2]
rdsEndPoint = sys.argv[3]
rdsDB = sys.argv[4]
rdsDBDriver = sys.argv[5]
rdsDBName = sys.argv[6]
rdsTable = sys.argv[7]
rdsUser = sys.argv[8]
rdsPass = sys.argv[9]

parser = configparser.ConfigParser()
parser.read(os.path.expanduser('/opt/bitnami/spark/.aws/credentials'))

#configuring spark-s3 connection
spark = SparkSession \
        .builder \
        .appName('Spark-aws')\
        .config('spark.hadoop.fs.s3a.access.key', parser.get('default', 'aws_access_key_id'))\
        .config('spark.hadoop.fs.s3a.secret.key', parser.get('default', 'aws_secret_access_key'))\
        .config('spark.hadoop.fs.s3a.impl', 'org.apache.hadoop.fs.s3a.S3AFileSystem')\
        .getOrCreate()

#Reading the parquet file from s3 bucket
df = spark.read.option('header', True)\
                .option('inferSchema', 'true')\
                .parquet(f's3a://{s3Bucket}/{s3StageSink}')

#Writing the data into a table 
df.write.mode('overwrite')\
        .format('jdbc')\
        .option('url', f'jdbc:{rdsDB}://{rdsEndPoint}/{rdsDBName}')\
        .option('driver', rdsDBDriver)\
        .option('dbtable', rdsTable)\
        .option('user', rdsUser)\
        .option('password', rdsPass)\
        .save()
