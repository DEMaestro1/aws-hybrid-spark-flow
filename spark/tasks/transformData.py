from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import configparser
import sys
import os

#Creating file paths from passed system argument
s3Bucket = sys.argv[1]
s3RawSink = sys.argv[2]
s3StageSink = sys.argv[3]

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

#Reading the csv file from s3 bucket   
df = spark.read.option('header', True)\
                .option('inferSchema', 'true')\
                .csv(f's3a://{s3Bucket}/{s3RawSink}')

#Filtering for required columns and data
tDf = df.select(col('LEGAL NAME').alias('LGL_NM'), col('APPLICATION TYPE').alias('APP_TYP'), col('CONDITIONAL APPROVAL').alias('COND_APRV'))\
        .filter((col('APP_TYP') == 'ISSUE') & (col('COND_APRV') == 'Y'))

#Writing into the sink location in s3 as a parquet
tDf.write \
   .mode('overwrite') \
   .parquet(f's3a://{s3Bucket}/{s3StageSink}')
 

