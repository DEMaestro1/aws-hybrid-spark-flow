FROM apache/airflow:2.5.2-python3.8
USER root

# Install OpenJDK-11 and providers for Apache Spark

RUN apt update && \
    apt-get install -y openjdk-11-jdk && \
    apt-get install -y ant && \
    apt-get clean && \
    mkdir /usr/local/files && \
    chown 1001 /usr/local/files;

# Set JAVA_HOME
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/
RUN export JAVA_HOME

USER airflow

#COPY ./requirements.txt /
#RUN pip install -r /requirements.txt
RUN pip install pyspark==3.3.2 && \
    pip install apache-airflow-providers-apache-spark==4.0.0 && \
    curl https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.2/hadoop-aws-3.3.2.jar --output /home/airflow/.local/lib/python3.8/site-packages/pyspark/jars/hadoop-aws-3.3.2.jar && \
    curl https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.1026/aws-java-sdk-bundle-1.11.1026.jar --output /home/airflow/.local/lib/python3.8/site-packages/pyspark/jars/aws-java-sdk-bundle-1.11.1026.jar;