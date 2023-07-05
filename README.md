<h1 align="center">ETL Pipeline with Airflow, Spark, PostgreSQL and Docker</h1>

<p align="center">
  <a href="#about">About</a> •
  <a href="#scenario">Scenario</a> •
  <a href="#base-concepts">Base Concepts</a> •
  <a href="#prerequisites">Prerequisites</a> •
  <a href="#set-up">Set-up</a> •
  <a href="#installation">Installation</a> •
  <a href="#airflow-interface">Airflow Interface</a> •
  <a href="#spark-interface">Airflow Interface</a> •
  <a href="#pipeline-task-by-task">Pipeline Task by Task</a> •
  <a href="#shut-down-and-restart-airflow">Shut Down and Restart Airflow and Spark</a> 
</p>

## About

This is a project showcasing how to build an ETL workload using Airflow, Spark and AWS with Docker and Terraform being used for deployment.

A file is downloaded from a public url using curl command, pushed into an s3 location, transformed using Spark and loaded into an AWS RDS Postgres database. 

The project is built in Python and Spark and it has 4 main parts that determine the flow of the pipeline:-

  1. The Airflow DAG file, [**dagRun.py**](https://github.com/DEMaestro1/aws-hybrid-spark-flow/blob/main/dags/dagRun.py), which orchestrates the data pipeline tasks. The data is downloaded using a normal bash/curl command located in the dagRun.py file itself.
  2. The S3 data loading script is located in [**loadFileToS3.py**](https://github.com/DEMaestro1/aws-hybrid-spark-flow/blob/main/spark/tasks/loadFileToS3.py)
  3. The data transformation/processing script which uses Spark is located in [**transformData.py**](https://github.com/DEMaestro1/aws-hybrid-spark-flow/blob/main/spark/tasks/transformData.py)
  4. The script that loads the data to AWS RDS using Spark can be found in [**loadToRDS.py**](https://github.com/DEMaestro1/aws-hybrid-spark-flow/blob/main/spark/tasks/loadToRDS.py)

## Scenario

The business license data which can be found on https://data.cityofchicago.org, it contains data about business license renewals and new grants in the city of Chicago, the data is updated periodically.

We are only looking for businesses that were newly issued a business license based on conditional approvals.

## Base concepts

 - [ETL (Extract, Transform, Load)](https://en.wikipedia.org/wiki/Extract,_transform,_load)
 - [Pipeline](https://en.wikipedia.org/wiki/Pipeline_(computing))
 - [Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/index.html) ([wikipedia page](https://en.wikipedia.org/wiki/Apache_Airflow))
 - [Apache Spark](https://spark.apache.org/docs/latest/)
 - [Airflow DAG](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html#dags)
 - [AWS](https://docs.aws.amazon.com/)
 - [PostgreSQL](https://www.postgresql.org/)

## Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Terraform](https://www.terraform.io/)

## Set-up

1. Download or pull the repo to your desired location.

2. There are three files for various configuartions that need to be created with various information:-

  i. configuration.conf file inside the dags folder with the following details/stuture:-
    
    [rds_config]
    rdsEndPoint = your_endpoint
    rdsDB = your_RDS_db (Postgres)
    rdsDBDriver = DB_Driver (org.postgresql.Driver)
    rdsDBName = db_name
    rdsTable = table_name
    rdsUser = user
    rdsPass = pass

    [s3_config]
    s3Bucket = unique_s3_bucket

  ii. terraform.tfvars file inside the terraform folder with the following details/stuture:-
    
    rds_user = 'user'
    rds_pass = 'pass'
    db_name = 'db_name'
    s3_bucker_name = 'unique_s3_bucket'

  iii. .env file under the same directory as docker-compose file with the following details/stuture:-
    
    AWS_CREDS_PATH= 'aws_creds_location'

  There's multiple ways of getting creds some more safer, the AWS documentation lists quite a few of them.

3. Go to the terraform folder and use terraform plan to look at the deployment plan and then use terraform apply to deploy the AWS resources. Terraform needs to be downloaded and setup in path for this to work.

4. Depending on how you setup the AWS RDS, the AWS RDS will need to have the 5432 port open and should be accepting connections from your IP address. If you are new to AWS and depending on where you are deploying the docker services, this can range from very complicated to very easy. In the end, the goal is to have the AWS credentials available to the machine that is hosting the scripts and the machine having a way to connect to S3 and RDS.

## Installation

Start the installation with:

    docker build -t airflow-spark-custom .
    docker-compose up -d

This command will pull and create Docker images and containers for Airflow as well as another PostgreSQL container to store poverty data.
This is done according to the instructions in the [docker-compose.yaml](https://github.com/DEMaestro1/aws-hybrid-spark-flow/blob/main/docker-compose.yaml) file:

After everything has been installed, you can check the status of your containers (if they are healthy) with:

    docker ps

**Note**: it might take up to 30 seconds for the containers to have the **healthy** flag after starting, sometimes it takes extra time for the Airflow web interface to be available.

## Airflow Interface

You can now access the Airflow web interface by going to http://localhost:8080/. If you have not changed them in the docker-compose.yml file, the default user is **airflow** and password is **airflow**:

The defaults can be changed inside the docker-compose file.

After signing in, the Airflow home page is the DAGs list page. Here you will see all your DAGs and the Airflow example DAGs, sorted alphabetically. 

Any DAG python script saved in the directory [**dags/**](https://github.com/DEMaestro1/aws-hybrid-spark-flow/tree/main/dags), will show up on the DAGs page.

## Spark Interface

You can access the Spark driver by going to http://localhost:8090/. The port can be changed as needed in the docker-compose file.

## Pipeline Task by Task

#### Task `getFile`

The file is downloaded using the Bash Operator which uses the curl command to store the downloaded file as a csv.

#### Task `loadFileToS3`

The file is then loaded into a S3 Bucket as a csv using the Bash Operator.

This can also be done using a Spark Submit Operator, if need be; like it is done in the following task, you simply need to just read the csv using Spark and write it to S3.

#### Task `transformData`

The csv in S3 is then read and transformed using generic spark code and written as a parquet inside the S3 Bucket using a Spark Submit Operator.

#### Task `loadFiletoRDS`

The postgres jar file located under spark/jars is used for this task. The location of the jar is referenced under the SparkSubmitOperator, you can also add a curl command to grab the jar in the DockerFile depending on your preference.

The processed parquet data is then loaded into AWS RDS PostgreSQL. This can also be done in other and much simpler ways that won't require reading and thus downloading the data.

An example of this can be found in the AWS docs:-
https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PostgreSQL.S3Import.html

## Shut Down and Restart Airflow

For any changes made in the configuration files to be applied, you will need to rebuild the Airflow images with the commands:
	
    docker build -t airflow-custom .
    docker-compose build

Recreate all the containers with:

    docker-compose up -d

## License
You can check out the full license [here](https://github.com/DEMaestro1/aws-hybrid-spark-flow/blob/main/LICENSE)

This project is licensed under the terms of the **GNU** license.
