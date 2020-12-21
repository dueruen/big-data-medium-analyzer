# import imageio
import base64
import io
import cv2 as cv2
import numpy as np
import skimage
from skimage import io as sio


filename = "1.png"
with open(filename, "rb") as fid:
    data = fid.read()

b64_bytes = base64.b64encode(data)
b64_string = b64_bytes.decode()

# img = imageio.imread(io.BytesIO(base64.b64decode(b64_string)))
img = sio.imread(io.BytesIO(base64.b64decode(b64_string)))

print('Type of the image : ' , type(img)) 
print('Shape of the image : {}'.format(img.shape)) 
print('Image Height {}'.format(img.shape[0])) 
print('Image Width {}'.format(img.shape[1])) 
print('Dimension of Image {}'.format(img.ndim))

print('Image size {}'.format(img.size)) 

r = img.mean(axis=0).mean(axis=0)
print(r)
print(r[0])
h = '#%02x%02x%02x' % (int(r[0]), int(r[1]), int(r[2]))
print(h)
print(img)
print(img.reshape(-1, 3))
pixels = np.float32(img.reshape(-1, 3))
print(pixels)

n_colors = 5
criteria = (cv2.TermCriteria_EPS + cv2.TermCriteria_MAX_ITER, 200, .1)
flags = cv2.KMEANS_RANDOM_CENTERS

_, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
_, counts = np.unique(labels, return_counts=True)

dominant = palette[np.argmax(counts)]
print(dominant)