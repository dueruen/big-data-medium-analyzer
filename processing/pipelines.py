import imageio
import base64
import io
import cv2
import numpy as np

def preprocessing_pipeline(article_df):
  df = preprocess_image_pipeline(article_df)

  return df

def preprocess_image_pipeline(article_df):
  b64_string = article_df.decode()
  image = imageio.imread(io.BytesIO(base64.b64decode(b64_string)))

  image_pixel_height = image.shape[0]
  image_pixel_width = image.shape[1]
  image_size = image.size
  image_average_pixel_color = image.mean(axis=0).mean(axis=0)
  image_dominant_pixel_color = cal_dominant_color(image)

  article_df.withColumn("image_pixel_height", image_pixel_height) \
    .withColumn("image_pixel_width", image_pixel_width) \
    .withColumn("image_size", image_size) \
    .withColumn("image_average_pixel_color", image_average_pixel_color) \
    .withColumn("image_dominant_pixel_color", image_dominant_pixel_color)
  return article_df

def cal_dominant_color(img):
  # Calculate the dominant pixel color using k-means clustering
  pixels = np.float32(img.reshape(-1, 3))
  n_colors = 5
  criteria = (cv2.TermCriteria_EPS + cv2.TermCriteria_MAX_ITER, 200, .1)
  flags = cv2.KMEANS_RANDOM_CENTERS

  _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
  _, counts = np.unique(labels, return_counts=True)

  return palette[np.argmax(counts)]