from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField
from pyspark.sql.types import ArrayType, LongType, DoubleType, IntegerType, StringType, BooleanType, BinaryType, DateType
from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel

import base64
import io
from skimage import io as sio
import uuid

import pipelines

# Config
bootstrap_servers = "node-master:9092,node1:9092,node2:9092"
kafka_topic_name = "test_json"

# Make a Spark Session
spark = SparkSession \
    .builder \
    .appName("Medium clap predictor") \
    .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
    .config("hive.metastore.uris", "thrift://node-master:9083,thrift://node1:9083,thrift://node2:9083") \
    .enableHiveSupport() \
    .getOrCreate()

# Define the Schema
schema = StructType([
    StructField("title", StringType()),
    StructField("subtitle", StringType()),
    StructField("image", StringType()),
    StructField("reading_time", IntegerType()),
    StructField("publication", StringType())
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
    .selectExpr("article.title as title", "article.subtitle as subtitle", "article.image as image", "article.reading_time as reading_time",  "article.publication as publication_str")

##
# Preprocess dataframe
##
df = pipelines.preporcess(df)

##
# Predict claps
##
# Add label
df = df.withColumn("claps", lit(1))
modelPath = "./claps_model"

loadedPipelineModel = PipelineModel.load(modelPath)
prediction_df = loadedPipelineModel.transform(df)
#df.select('claps', 'features',  'rawPrediction', 'prediction', 'probability').show()

query = prediction_df \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

###
# Write dataframe to hive
###
df = df.drop("claps") \
    .withColumn("id", str(uuid.uuid4())) \
    .withColumn("prediction", prediction_df.prediction) \

def processRow(d, epochId):
    d.write.saveAsTable(name='predictions', format='hive', mode='append')

query = df \
    .writeStream \
    .foreachBatch(processRow) \
    .start() \

###
# Write to kafka
###
df = df.select("id", "prediction")
query = df \
  .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
  .writeStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "node-master:9092,node1:9092,node2:9092") \
  .option("topic", "claps_predicted") \
  .start()

query.awaitTermination()