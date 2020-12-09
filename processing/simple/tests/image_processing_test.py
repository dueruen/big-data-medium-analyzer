import imageio
import base64
import io
import cv2
import cv2 
import numpy as np

filename = "1.png"
with open(filename, "rb") as fid:
    data = fid.read()

b64_bytes = base64.b64encode(data)
b64_string = b64_bytes.decode()

img = imageio.imread(io.BytesIO(base64.b64decode(b64_string)))

print('Type of the image : ' , type(img)) 
print('Shape of the image : {}'.format(img.shape)) 
print('Image Hight {}'.format(img.shape[0])) 
print('Image Width {}'.format(img.shape[1])) 
print('Dimension of Image {}'.format(img.ndim))

print('Image size {}'.format(img.size)) 

print(img.mean(axis=0).mean(axis=0))

pixels = np.float32(img.reshape(-1, 3))

n_colors = 5
criteria = (cv2.TermCriteria_EPS + cv2.TermCriteria_MAX_ITER, 200, .1)
flags = cv2.KMEANS_RANDOM_CENTERS

_, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
_, counts = np.unique(labels, return_counts=True)

dominant = palette[np.argmax(counts)]
print(dominant)