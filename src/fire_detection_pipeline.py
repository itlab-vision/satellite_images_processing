import os
import rasterio
import numpy as np
import cv2 as cv

from models.kumar_roy import KumarRoy64_10
from matplotlib import pyplot as plt

# read and preprocess dataset && download model (костыль)
images_path = os.path.abspath('') + '/image.tif'

image = rasterio.open(images_path).read().transpose((1, 2, 0))
MAX_PIXEL_VALUE = 65535
image = np.float32(image)/MAX_PIXEL_VALUE

model_path = os.path.abspath('') + '/model.h5'

# init && process
model = KumarRoy64_10(model_path)
result = model.process(image)

# visualise (костыль)
fig, (a, b) = plt.subplots(1,2, figsize=(12,8))
src = np.concatenate((image[:,:,7:8],image[:,:,6:7],image[:,:,2:3]), axis = 2)
a.imshow(src)
b.imshow(result)
plt.show()

# save (костыль)
cv.imwrite('res_model.png', cv.cvtColor(result, cv.COLOR_RGB2BGR))
print('results of model was written to {}'.format(os.path.abspath('')))
