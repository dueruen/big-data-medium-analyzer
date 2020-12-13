# Start
# /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 /home/hadoop/big-data-medium-analyzer/processing/kafka_consumer.py
# /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 /home/hadoop/tests/kafka_test_consumer.py
# /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 --py-files /home/hadoop/tests/kafka_test_consumer.py,/home/hadoop/tests/pipelines.py
# /home/hadoop/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.6 --py-files /home/hadoop/big-data-medium-analyzer/processing/pipelines.py /home/hadoop/big-data-medium-analyzer/processing/kafka_consumer.py

from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField
from pyspark.sql.types import ArrayType, LongType, DoubleType, IntegerType, StringType, BooleanType, BinaryType, DateType
from pyspark.sql import SparkSession

import base64
import io
from skimage import io as sio
# import pipelines

# Config
bootstrap_servers = "10.123.252.211:9092,10.123.252.212:9092,10.123.252.213:9092"
kafka_topic_name = "test_json"

# Make a Spark Session
spark = SparkSession \
    .builder \
    .appName("Real time Medium analyzer") \
    .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
    .config("hive.metastore.uris", "thrift://localhost:9083") \
    .enableHiveSupport() \
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
    .selectExpr("article.id as id", "article.url as url", "article.title as title", "article.subtitle as subtitle", "article.image as image", "article.claps as claps", "article.responses as responses", "article.reading_time as reading_time",  "article.publication as publication", "article.date as date_str")

##
# Preprocess image
##
def preprocess_image(base64_image):
    image = sio.imread(io.BytesIO(base64.b64decode(base64_image)))

    image_pixel_height = image.shape[0]
    image_pixel_width = image.shape[1]
    image_size = image.size
    image_average_pixel_color = image.mean(axis=0).mean(axis=0)
    return (image_pixel_height, image_pixel_width, image_size, int(image_average_pixel_color[0]), int(image_average_pixel_color[1]), int(image_average_pixel_color[2]))

image_udf = udf(lambda base64_image: preprocess_image(base64_image), ArrayType(IntegerType()))

df = df.withColumn("res", image_udf(col("image"))) \
    .withColumn("image_pixel_height", col("res").getItem(0)) \
    .withColumn("image_pixel_width", col("res").getItem(1)) \
    .withColumn("image_size", col("res").getItem(2)) \
    .withColumn("image_average_pixel_color_r", col("res").getItem(3)) \
    .withColumn("image_average_pixel_color_g", col("res").getItem(4)) \
    .withColumn("image_average_pixel_color_b", col("res").getItem(5)) \
    .drop("res")

##
# Preporcess title and subtitle
##
keywords = ["net neutrality", "big data", "data mining", "actionable analytics", "ai", "artificial intelligence", "ml", "machine learning", "neural network", "nl", "information retrieval", "personalization", "startup", "automate", "serverless", "voice recognition", "chatbots", "augmented reality", "ar", "virtual reality", "vr", "robot", "industry 4.0", "internet of things", "iot", "quantum", "blockchain", "ecosystem", "smart", "legacy", "crypto", "futureware", "disruption", "disrupt", "agile", "unicorn", "algorithm", "backdoor", "bug", "cybersecurity", "data lake", "deepfake", "deep learning", "dl", "encryption", "saas", "paas", "iaas", "cloud", "next gen", "hack"]

typewords = ["hands on", "hands-on" "how to", "deep dive", "easy", "hard", "guide", "advanced", "101", "beginner", "intermediate", "expert", "method", "strategi", "introduction"]

def preprocess_title(title):
    title = title.lower()
    keyword_count = 0
    for keyword in keywords:
        keyword_count += title.count(keyword)

    typeword_count = 0
    for typeword in typewords:
        typeword_count += title.count(typeword)

    title_words = len(title.split())
    title_len = len(title)
    return (title_len, title_words, typeword_count, keyword_count)

title_udf = udf(lambda title: preprocess_title(title), ArrayType(IntegerType()))

df = df.withColumn("res", title_udf(col("title"))) \
    .withColumn("title_len", col("res").getItem(0)) \
    .withColumn("title_words", col("res").getItem(1)) \
    .withColumn("title_type_words", col("res").getItem(2)) \
    .withColumn("title_key_words", col("res").getItem(3)) \
    .drop("res")

df = df.withColumn("res", title_udf(col("subtitle"))) \
    .withColumn("subtitle_len", col("res").getItem(0)) \
    .withColumn("subtitle_words", col("res").getItem(1)) \
    .withColumn("subtitle_type_words", col("res").getItem(2)) \
    .withColumn("subtitle_key_words", col("res").getItem(3)) \
    .drop("res")

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