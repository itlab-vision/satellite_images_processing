import os
import numpy as np
import cv2 as cv
from models.cloud_net import CloudNet
from visualizers.display_rgb import DisplayAsRGB
from skimage.io import imread
from skimage.transform import resize
from matplotlib import pyplot as plt

# read and preprocess dataset && download model (костыль)
model_path = os.path.abspath('') + '/model.h5'
MAX_PIXEL_VALUE = 65535  # maximum gray level in landsat 8 images

# готовое 4 - канальное изображение
images_path = os.path.abspath('') + '/image.tif'
image = imread(images_path)
image = resize(image, (384, 384), preserve_range=True, mode='symmetric') # нужно только в общем случае


# не готовое изображение
#images_path = os.path.abspath('') + '/38-Cloud_test'
#image_ends = 'patch_26_2_by_6_LC08_L1TP_032035_20160420_20170223_01_T1.TIF'

#image_red = imread(images_path + '/test_red/'+ 'red_'+image_ends)
#image_green = imread(images_path + '/test_green/'+ 'green_'+image_ends)
#image_blue = imread(images_path + '/test_blue/'+ 'blue_'+image_ends)
#image_nir = imread(images_path + '/test_nir/'+ 'nir_'+image_ends)

#image = np.stack((image_red, image_green, image_blue, image_nir), axis=-1)
#image = resize(image, (384, 384), preserve_range=True, mode='symmetric') # нужно только в общем случае
#image /= MAX_PIXEL_VALUE

#import tifffile as tiff
#tiff.imsave(os.path.abspath('')+'/test_image_0.tif', image)


# init && process
model = CloudNet(model_path)
result = model.process(image)

# visualise
displayer = DisplayAsRGB()
displayer.show([image, np.expand_dims(result, 2)])

# save (костыль)
cv.imwrite('res_model.png', cv.cvtColor(result, cv.COLOR_RGB2BGR))
print('results of model was written to {}'.format(os.path.abspath('')))
