# Start
# /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.2.3,org.apache.spark:spark-sql-kafka-0-10_2.11:2.2.3 kafka_consumer.py

from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField
from pyspark.sql.types import LongType, DoubleType, IntegerType, StringType, BooleanType, BinaryType, DateType
from pyspark.sql import SparkSession

# Config
bootstrap_servers = "10.123.252.213:9092"
kafka_topic_name = "test"

# Make a Spark Session
spark = SparkSession \
  .builder \
  .appName("Real time Medium analyzer") \
  .getOrCreate()

# Define the Schema
schema = StructType([
  StructField("id", LongType()),
  StructField("url", StringType()),
  StructField("title", StringType()),
  StructField("subtitle", StringType()),
  StructField("image", BinaryType()),
  StructField("claps", IntegerType()),
  StructField("responses", IntegerType()),
  StructField("reading_time", IntegerType()),
  StructField("publication", StringType()),
  StructField("date", DateType())
])

# Subscribe to kafka to get a Spark DataFrame
df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", bootstrap_servers) \
  .option("subscribe", kafka_topic_name) \
  .load()
df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

words = df.select(
   explode(
       split(df.value, " ")
   ).alias("word")
)

# Generate running word count
wordCounts = words.groupBy("word").count()

query = wordCounts \
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

query.awaitTermination()

# (10) Output the results of the Streaming Transformations and final predicted sentiments to the console sink
# query = predictions_df.writeStream.outputMode("complete").format("console").option("truncate", "false").start() 
# query.awaitTermination()