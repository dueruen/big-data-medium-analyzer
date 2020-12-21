from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField
from pyspark.sql.types import ArrayType, LongType, DoubleType, IntegerType, StringType, BooleanType, BinaryType, DateType
from pyspark.sql import SparkSession

import numpy as np
import json
import datetime
import base64
import csv

import pipelines

spark = SparkSession \
  .builder \
  .appName("Hive adder") \
  .getOrCreate()

    #     .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
    # .config("hive.metastore.uris", "thrift://node-master:9083,thrift://node1:9083,thrift://node2:9083") \
    # .enableHiveSupport() \

schema = StructType([
  StructField("id", IntegerType()),
  StructField("url", StringType()),
  StructField("title", StringType()),
  StructField("subtitle", StringType()),
  StructField("image", StringType()),
  StructField("claps", IntegerType()),
  StructField("responses", IntegerType()),
  StructField("reading_time", IntegerType()),
  StructField("publication_str", StringType()),
  StructField("date_str", StringType()),
  StructField("image_pixel_height", IntegerType()),
  StructField("image_pixel_width", IntegerType()),
  StructField("image_size", IntegerType()),
  StructField("image_average_pixel_color_r", IntegerType()),
  StructField("image_average_pixel_color_g", IntegerType()),
  StructField("image_average_pixel_color_b", IntegerType())
])

def readFile(filePath):
  with open(filePath, "rb") as fid:
    data = fid.read()
    b64_bytes = base64.b64encode(data)
    return b64_bytes.decode()

count = 0
data = []
with open('./populate/data/working_medium_data.csv') as csvfile:
  spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
  for row in spamreader:
    if count == 0:
      count += 1
      continue

    # Wrong row length
    if len(row) != 10:
      continue

    # Not image name
    if not row[4]:
      continue

    b64_string = readFile('./populate/data/images/' + row[4])
    image_data = pipelines.preprocess_image(b64_string)

    # Image data not process correctly
    if isinstance(image_data, bool):
      print("image_Data false ")
      print(row)
      continue

    # Wrong image data length
    if len(image_data) != 6:
      print("image_Data not 6 ")
      print(row)
      continue

    data.append((int(float(row[0])), row[1], row[2], row[3], row[4], int(float(row[5])), int(float(row[6])), int(float(row[7])), row[8], row[9], image_data[0], image_data[1], image_data[2], image_data[3], image_data[4], image_data[5]))

    count+= 1
    # Control data amount
    # if count == 9:
    #   break

df = spark.createDataFrame(data,schema)
df.show()

print(df.count())

df = df.dropDuplicates()

print(df.count())
# df.show()

## PREPROCESS
df = pipelines.preprocess_title_subtitle_pipeline(df)

df.printSchema()
p_df = df.toPandas()
p_df.set_index('id', inplace=True)

p_df.to_csv('pre_data.csv')

# df.write.saveAsTable(name='articles', format='hive', mode='append')