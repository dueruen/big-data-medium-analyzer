###
# Problems with dependencies and when logic is in another file
###

# # import imageio
# import base64
# import io
# import cv2
# import numpy as np
# # import skimage
# from skimage import io as sio
# from pyspark.sql.functions import *
# from pyspark.sql.types import *

# p_schema = StructType([
#   StructField("i1", IntegerType()),
#   StructField("i2", IntegerType()),
#   StructField("i3", IntegerType()),
#   StructField("i4", ArrayType(DoubleType())),
#   StructField("i5", ArrayType(DoubleType()))
# ])
# preprocess_image_udf = udf(lambda base64_image: preprocess_image_pipeline(base64_image), preprocess_image_udf_schema)
# #preprocess_image_udf = udf(lambda base64_image: preprocess_image_pipeline(base64_image), IntegerType())

# def preprocess_image_pipeline(base64_image):
#   image = sio.imread(io.BytesIO(base64.b64decode(base64_image)))

#   image_pixel_height = image.shape[0]
#   image_pixel_width = image.shape[1]
#   image_size = image.size
#   image_average_pixel_color = image.mean(axis=0).mean(axis=0)
#   image_dominant_pixel_color = cal_dominant_color(image)

#   # article_df.withColumn("image_pixel_height", image_pixel_height) \
#   #   .withColumn("image_pixel_width", image_pixel_width) \
#   #   .withColumn("image_size", image_size) \
#   #   .withColumn("image_average_pixel_color", image_average_pixel_color) \
#   #   .withColumn("image_dominant_pixel_color", image_dominant_pixel_color)
#   #return image_pixel_height, image_pixel_width, image_size, image_average_pixel_color, image_dominant_pixel_color
#   return 42

# def cal_dominant_color(img):
#   # Calculate the dominant pixel color using k-means clustering
#   pixels = np.float32(img.reshape(-1, 3))
#   n_colors = 5
#   criteria = (cv2.TermCriteria_EPS + cv2.TermCriteria_MAX_ITER, 200, .1)
#   flags = cv2.KMEANS_RANDOM_CENTERS

#   _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
#   _, counts = np.unique(labels, return_counts=True)

#   return palette[np.argmax(counts)]