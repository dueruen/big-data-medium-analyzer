# Start 
# /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 /home/hadoop/big-data-medium-analyzer/processing/kafka_consumer.py
# /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 /home/hadoop/tests/kafka_test_consumer.py
# /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 --py-files /home/hadoop/tests/kafka_test_consumer.py,/home/hadoop/tests/pipelines.py

# /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 --py-files /home/hadoop/big-data-medium-analyzer/processing/pipelines.py /home/hadoop/big-data-medium-analyzer/processing/kafka_consumer.py

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

df = raw_df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING) as json") \
    .withColumn("article", from_json(col("json"), schema)) \
    .selectExpr("article.id as id", "article.url as url", "article.title as title", "article.subtitle as subtitle", "article.image as image", "article.claps as claps", "article.responses as responses", "article.reading_time as reading_time",  "article.publication as publication", "article.date as date")

# query = article_df \
#     .writeStream \
#     .outputMode("append") \
#     .format("console") \
#     .start()

# preprocessed_df = pipelines.preprocessing_pipeline(article_df)
df = df.withColumn("res", pipelines.preprocess_image_udf(col("image"))) \
    .withColumn("image_pixel_height", col("res").getItem(0)) \
    .withColumn("image_pixel_width", col("res").getItem(1)) \
    .withColumn("image_size", col("res").getItem(2)) \
    .withColumn("image_average_pixel_color", col("res").getItem(3)) \
    .withColumn("image_dominant_pixel_color", col("res").getItem(4)) \
    .drop("res")

query = df \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()