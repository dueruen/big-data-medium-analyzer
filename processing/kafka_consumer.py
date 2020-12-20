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
spark = SparkSession \
    .builder \
    .appName("Real time Medium analyzer") \
    .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
    .config("hive.metastore.uris", "thrift://master-node:9083,thrift://node1:9083,thrift://node2:9083") \
    .enableHiveSupport() \
    .getOrCreate()

# Run without hive
# spark = SparkSession \
#     .builder \
#     .appName("Real time Medium analyzer") \
#     .getOrCreate()

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
df = pipelines.preporcess(df)

query = df \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

##
# Predict claps
##
modelPath = "./claps_model"

loadedPipelineModel = PipelineModel.load(modelPath)
df = loadedPipelineModel.transform(df)
df.select('claps', 'features',  'rawPrediction', 'prediction', 'probability').show()

###
# Write dataframe to hive
###
def processRow(d, epochId):
    d.write.saveAsTable(name='articles', format='hive', mode='append')

query = df \
    .writeStream \
    .foreachBatch(processRow) \
    .start() \

###
# Write to console 
###
query = df \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()