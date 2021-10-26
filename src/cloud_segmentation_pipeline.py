import os
import numpy as np
import tifffile as tiff
from models.cloud_net import CloudNet


# read and preprocess dataset && download model (костыль)
images_path = os.path.abspath('') + '/image.tif'
model_path = os.path.abspath('') + '/model.h5'
MAX_PIXEL_VALUE = 65535

#read & preprocess image


# init && process
model = CloudNet(model_path)
#result = model.process(image)


# visualise (костыль)
#fig, (a, b) = plt.subplots(1,2, figsize=(12,8))
# get image
#src =
#a.imshow(src)
#b.imshow(result)
#plt.show()

# save (костыль)
#cv.imwrite('res_model.png', cv.cvtColor(result, cv.COLOR_RGB2BGR))
#print('results of model was written to {}'.format(os.path.abspath('')))
