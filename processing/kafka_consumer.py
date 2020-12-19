# Start
# /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 /home/hadoop/big-data-medium-analyzer/processing/kafka_consumer.py
# /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 /home/hadoop/tests/kafka_test_consumer.py
# /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 --py-files /home/hadoop/tests/kafka_test_consumer.py,/home/hadoop/tests/pipelines.py
# /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 --py-files /home/hadoop/big-data-medium-analyzer/processing/pipelines.py /home/hadoop/big-data-medium-analyzer/processing/kafka_consumer.py

from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField
from pyspark.sql.types import ArrayType, LongType, DoubleType, IntegerType, StringType, BooleanType, BinaryType, DateType
from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel

import base64
import io
from skimage import io as sio

import pipelines

# Config
bootstrap_servers = "10.123.252.211:9092,10.123.252.212:9092,10.123.252.213:9092"
kafka_topic_name = "test_json"

# Make a Spark Session
# spark = SparkSession \
#     .builder \
#     .appName("Real time Medium analyzer") \
#     .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
#     .config("hive.metastore.uris", "thrift://localhost:9083") \
#     .enableHiveSupport() \
#     .getOrCreate()

spark = SparkSession \
    .builder \
    .appName("Real time Medium analyzer") \
    .getOrCreate()

# Define the Schema
schema = StructType([
    StructField("id", IntegerType()),
    StructField("url", StringType()),
    StructField("title", StringType()),
    StructField("subtitle", StringType()),
    StructField("image", StringType()),
    StructField("claps", IntegerType()),
    StructField("responses", IntegerType()),
    StructField("reading_time", IntegerType()),
    StructField("publication", StringType()),
    StructField("date", StringType())
])

# Subscribe to kafka to get a Spark DataFrame
raw_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", bootstrap_servers) \
    .option("subscribe", kafka_topic_name) \
    .load()

df = raw_df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING) as json") \
    .withColumn("article", from_json(col("json"), schema)) \
    .selectExpr("article.id as id", "article.url as url", "article.title as title", "article.subtitle as subtitle", "article.image as image", "article.claps as claps", "article.responses as responses", "article.reading_time as reading_time",  "article.publication as publication_str", "article.date as date_str")

##
# Preprocess dataframe
##
df_preprocessed = pipelines.preporcess(df)

##
# Predict claps
##
modelPath = "./claps_model"

loadedPipelineModel = PipelineModel.load(modelPath)
test_reloadedModel = loadedPipelineModel.transform(df_preprocessed)
test_reloadedModel.select('claps', 'features',  'rawPrediction', 'prediction', 'probability').show()

###
# Write dataframe to hive
###
# def processRow(d, epochId):
#     d.write.saveAsTable(name='articles', format='hive', mode='append')

# query = df \
#     .writeStream \
#     .foreachBatch(processRow) \
#     .start() \

###
# Write to console 
###
query = df_preprocessed \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()