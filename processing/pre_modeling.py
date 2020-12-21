from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField
from pyspark.sql.types import ArrayType, LongType, DoubleType, IntegerType, StringType, BooleanType, BinaryType, DateType
from pyspark.sql import SparkSession

import pyspark.mllib.linalg as ln
import pyspark.mllib.stat as st
import numpy as np
import json
import datetime
import base64
import csv

import pipelines

spark = SparkSession \
    .builder \
    .appName("Pre modeling") \
    .getOrCreate()

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
with open('./populate/data/working_medium_data.csv', newline='') as csvfile:
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

    b64_string = readFile(f'./populate/data/images/{row[4]}')
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

    data.append((int(float(row[0])), row[1], row[2], row[3], "b64_string", int(float(row[5])), int(float(row[6])), int(float(row[7])), row[8], row[9], image_data[0], image_data[1], image_data[2], image_data[3], image_data[4], image_data[5]))
    
    count+= 1
    # Control data amount 
    if count == 9:
      break

df = spark.createDataFrame(data,schema)
df.show()

print(df.count())

df = df.dropDuplicates()

print(df.count())
# df.show()

## PREPROCESS
df = df.drop(df.url)
df = df.drop(df.date_str)

df = df.drop(df.image)

df = pipelines.preprocess_title_subtitle_pipeline(df)
df = df.drop(df.title)
df = df.drop(df.subtitle)

df.printSchema()

## calculates the descriptive statistics of the numeric features
numeric_cols = ['claps','responses','reading_time',
                'image_pixel_height','image_pixel_width','image_size','image_average_pixel_color_r','image_average_pixel_color_g','image_average_pixel_color_b',
                'title_len','title_words','title_type_words','title_key_words',
                'subtitle_len','subtitle_words','subtitle_type_words','subtitle_key_words'
               ]

numeric_rdd = df\
  .select(numeric_cols)\
  .rdd \
  .map(lambda row: [e for e in row])
mllib_stats = st.Statistics.colStats(numeric_rdd)

for col, m, v in zip(numeric_cols, mllib_stats.mean(), mllib_stats.variance()):
  print('{0:<30}: \t{1:<10.2f} \t {2:.2f}'.format(col, m, np.sqrt(v)))

######### Load and use saved model
# from pyspark.ml import PipelineModel
# modelPath = "./claps_model"

# loadedPipelineModel = PipelineModel.load(modelPath)
# test_reloadedModel = loadedPipelineModel.transform(df)
# test_reloadedModel.select('claps', 'features',  'rawPrediction', 'prediction', 'probability').show()
#########

from pyspark.ml.classification import LogisticRegression
from pyspark.ml.linalg import Vectors
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.feature import OneHotEncoderEstimator, StringIndexer, VectorAssembler,StandardScaler
from pyspark.ml.linalg import DenseVector
from pyspark.ml import Pipeline

# Define pipeline steps
categoricalColumns = ['publication_str']
stages = []
for categoricalCol in categoricalColumns:
    stringIndexer = StringIndexer(inputCol = categoricalCol, outputCol = categoricalCol + 'Index')
    encoder = OneHotEncoderEstimator(inputCols=[stringIndexer.getOutputCol()], outputCols=[categoricalCol + "classVec"])
    stages += [stringIndexer, encoder]


numericCols = ['reading_time',
                'image_pixel_height','image_pixel_width','image_size','image_average_pixel_color_r','image_average_pixel_color_g','image_average_pixel_color_b',
                'title_len','title_words','title_type_words','title_key_words',
                'subtitle_len','subtitle_words','subtitle_type_words','subtitle_key_words'
               ]
assemblerInputs = [c + "classVec" for c in categoricalColumns] + numericCols
assembler = VectorAssembler(inputCols=assemblerInputs, outputCol="vectorized_features")
stages += [assembler]

scaler = StandardScaler(inputCol="vectorized_features", outputCol="features")
stages += [scaler]

lr = LogisticRegression(labelCol = 'claps', maxIter=10)
stages += [lr]

# Train the model
train, test = df.randomSplit([0.8, 0.2], seed = 2018)
print("Training Dataset Count: " + str(train.count()))
print("Test Dataset Count: " + str(test.count()))

cols = df.columns
pipeline = Pipeline(stages = stages)
pipelineModel = pipeline.fit(train)
predictions = pipelineModel.transform(test)
predictions.select('claps', 'features',  'rawPrediction', 'prediction', 'probability').show()

predictions.groupby("prediction").count().show()

# Evaluat model
import pyspark.ml.evaluation as ev
evaluator = ev.BinaryClassificationEvaluator(
    rawPredictionCol='probability', 
    labelCol='claps')

print(evaluator.evaluate(predictions, 
    {evaluator.metricName: 'areaUnderROC'}))
print(evaluator.evaluate(predictions, 
   {evaluator.metricName: 'areaUnderPR'}))

# Save model
# modelPath = "./claps_model"
# pipelineModel.write().overwrite().save(modelPath)