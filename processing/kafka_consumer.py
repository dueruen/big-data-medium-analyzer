# Start 
# /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 /home/hadoop/big-data-medium-analyzer/processing/kafka_consumer.py
# /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 /home/hadoop/tests/kafka_test_consumer.py

from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField
from pyspark.sql.types import LongType, DoubleType, IntegerType, StringType, BooleanType, BinaryType, DateType
from pyspark.sql import SparkSession

import pipelines

# Config
bootstrap_servers = "10.123.252.211:9092,10.123.252.212:9092,10.123.252.213:9092"
kafka_topic_name = "test_json"

# Make a Spark Session
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

#raw_df.printSchema()

article_df = raw_df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING) as json") \
    .withColumn("article", from_json(col("json"), schema)) \
    .selectExpr("article.id as id", "article.url as url", "article.title as title", "article.subtitle as subtitle", "article.image as image", "article.claps as claps", "article.responses as responses", "article.reading_time as reading_time",  "article.publication as publication", "article.date as date")

query = article_df \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

preprocessed_df = pipelines.preprocessing_pipeline(article_df)

query = preprocessed_df \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()    

#df = df.withColumn("article", from_json(col("json"), schema))
#    .selectExpr("article.id as id")

#article_string_df = df.selectExpr("CAST(value AS STRING)")

#dataset = spark.createDataset(df.select("json"))
#df = spark.read.json(dataset)

# query = df \
#     .writeStream \
#     .outputMode("append") \
#     .format("console") \
#     .start()

#article_df = article_string_df.select(from_json(col("value"), schema).alias("data")).select("data.*")
#df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING) as json") \
#    .withColumn("article", from_json(col("json"), schema=schema)) \
#    .selectExpr("article.id as id")

#querys = df \
#    .writeStream \
#    .outputMode("append") \
#    .format("console") \
#    .start()

#article_df = spark.read.json(spark.sparkContext.parallelize([df.select("json")]))

#query = article_df \
#    .writeStream \
#    .outputMode("append") \
#    .format("console") \
#    .start()

# query.awaitTermination()

# from pyspark.sql.functions import *
# from pyspark.sql.types import StructType, StructField
# from pyspark.sql.types import LongType, DoubleType, IntegerType, StringType, BooleanType, BinaryType, DateType
# from pyspark.sql import SparkSession

# # Config
# bootstrap_servers = "10.123.252.211:9092,10.123.252.212:9092,10.123.252.213:9092"
# kafka_topic_name = "test_json"

# # Make a Spark Session
# spark = SparkSession \
#   .builder \
#   .appName("Real time Medium analyzer") \
#   .getOrCreate()


# # Define the Schema
# schema = StructType([
#   StructField("id", LongType()),
#   StructField("url", StringType()),
#   StructField("title", StringType()),
#   StructField("subtitle", StringType()),
#   StructField("image", BinaryType()),
#   StructField("claps", IntegerType()),
#   StructField("responses", IntegerType()),
#   StructField("reading_time", IntegerType()),
#   StructField("publication", StringType()),
#   StructField("date", DateType())
# ])

# # Subscribe to kafka to get a Spark DataFrame
# df = spark \
#   .readStream \
#   .format("kafka") \
#   .option("kafka.bootstrap.servers", bootstrap_servers) \
#   .option("subscribe", kafka_topic_name) \
#   .load()

# df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING) as json")

# df.show()

# query = df \
#     .writeStream \
#     .outputMode("complete") \
#     .format("console") \
#     .start()


# words = df.select(
#    explode(
#        split(df.value, " ")
#    ).alias("word")
# )

# # Generate running word count
# wordCounts = words.groupBy("word").count()
# windowedCounts = words \
#     .withWatermark("timestamp", "10 minutes") \
#     .groupBy(
#         window(words.timestamp, "10 minutes", "5 minutes"),
#         words.word) \
#     .count()

# wordCounts \
#   .writeStream \
#   .format("txt") \
#   .option("path", "hdfs://node-master:9000/user/hadoop") \
#   .start()

# query = wordCounts \
#     .writeStream \
#     .outputMode("complete") \
#     .format("console") \
#     .start()

# # hdfs://node-master:9000


# query.awaitTermination()

# (10) Output the results of the Streaming Transformations and final predicted sentiments to the console sink
# query = predictions_df.writeStream.outputMode("complete").format("console").option("truncate", "false").start() 
# query.awaitTermination()

# from pyspark.sql.functions import *
# from pyspark.sql.types import StructType, StructField
# from pyspark.sql.types import LongType, DoubleType, IntegerType, StringType, BooleanType, BinaryType, DateType
# from pyspark.sql import SparkSession
# import datetime

# # Config
# bootstrap_servers = "10.123.252.213:9092"
# kafka_topic_name = "test"

# # Make a Spark Session
# spark = SparkSession \
#   .builder \
#   .appName("Real time Medium analyzer") \
#   .getOrCreate()

# # Define the Schema
# schema = StructType([
#   StructField("id", LongType()),
#   StructField("url", StringType()),
#   StructField("title", StringType()),
#   StructField("subtitle", StringType()),
#   StructField("image", BinaryType()),
#   StructField("claps", IntegerType()),
#   StructField("responses", IntegerType()),
#   StructField("reading_time", IntegerType()),
#   StructField("publication", StringType()),
#   StructField("date", DateType())
# ])

# # Subscribe to kafka to get a Spark DataFrame
# df = spark \
#   .readStream \
#   .format("kafka") \
#   .option("kafka.bootstrap.servers", bootstrap_servers) \
#   .option("subscribe", kafka_topic_name) \
#   .load()
# df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

# words = df.select(
#    explode(
#        split(df.value, " ")
#    ).alias("word")
# )

# words = words.withColumn("timestamp", datetime.datetimeConnection reset by 10.123.252.213 port 22

# [process exited with code 255]
# #wordCounts = words.groupBy("word").count()
# wordCounts = words \
#     .withWatermark("timestamp", "10 minutes") \
#     .groupBy(
#         window(words.timestamp, "10 minutes", "5 minutes"),
#         words.word) \
#     .count()

# wordCounts \
#     .writeStream \
#     .format("json") \
#     .option("path", "hdfs://node-master:9000/user/hadoop/books") \
#     .option("checkpointLocation", "hdfs://node-master:9000/user/hadoop/checkpoints") \
#     .start()

# query = wordCounts \
#     .writeStream \
#     .outputMode("complete") \
#     .format("console") \
#     .start()

# query.awaitTermination()