from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField
from pyspark.sql.types import ArrayType, LongType, DoubleType, IntegerType, StringType, BooleanType, BinaryType, DateType

import base64
import io
from skimage import io as sio
import numpy as np

def preporcess(df):
  df = preprocess_image_pipeline(df)
  df = preprocess_title_subtitle_pipeline(df)
  # df = preprocess_publication_pipeline(df)
  return df

def preprocess_image(base64_image):
    image = sio.imread(io.BytesIO(base64.b64decode(base64_image)))

    image_pixel_height = image.shape[0]
    image_pixel_width = image.shape[1]
    image_size = image.size
    image_average_pixel_color = image.mean(axis=0).mean(axis=0)

    if not isinstance(image_average_pixel_color, np.ndarray):
        print("HERE")
        print(image_average_pixel_color)
        return False

    return (image_pixel_height, image_pixel_width, image_size, int(image_average_pixel_color[0]), int(image_average_pixel_color[1]), int(image_average_pixel_color[2]))

image_udf = udf(lambda base64_image: preprocess_image(base64_image), ArrayType(IntegerType()))

def preprocess_image_pipeline(df):
  df = df.withColumn("res", image_udf(col("image"))) \
      .withColumn("image_pixel_height", col("res").getItem(0)) \
      .withColumn("image_pixel_width", col("res").getItem(1)) \
      .withColumn("image_size", col("res").getItem(2)) \
      .withColumn("image_average_pixel_color_r", col("res").getItem(3)) \
      .withColumn("image_average_pixel_color_g", col("res").getItem(4)) \
      .withColumn("image_average_pixel_color_b", col("res").getItem(5)) \
      .drop("res")
  return df

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

def preprocess_title_subtitle_pipeline(df):
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
  return df

# publication_options = {
#     "None" : 0,
#     "Towards Data Science" : 1,
#     "UX Collective" : 2,
#     "The Startup" : 3,
#     "The Writing Cooperative" : 4,
#     "Data Driven Investor" : 5,
#     "Better Humans" : 6,
#     "Better Marketing" : 7,
# }

# def map_publication(publication):
#     return publication_options.get(publication, 0)

# publication_options_udf = udf(lambda publication: map_publication(publication), IntegerType())

# def preprocess_publication_pipeline(df):
#   df = df.withColumn("publication", publication_options_udf(df.publication_str)) \
#     .drop("publication_str")
#   return df