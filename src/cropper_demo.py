import os
import tifffile as tiff
import numpy as np
import cv2 as cv
import math


image = 'LC08_L1TP_023027_20200923_20201006_01_T1'
path = os.path.abspath('')+'\\landsat_downloaded\\'+image+'\\'

with open(path+image+'_MTL.txt', 'r') as f:
    data = f.read().split('PRODUCT_METADATA')[1].split('\n')[14:22]
meta = {}
for info in data:
    meta[info.split('=')[0][4:-1]] = float(info.split('=')[1][1:])

# lattitude = y, longitude = x on image
ul = (meta['CORNER_UL_LON_PRODUCT'], meta['CORNER_UL_LAT_PRODUCT'])  # (x, y)
ur = (meta['CORNER_UR_LON_PRODUCT'], meta['CORNER_UR_LAT_PRODUCT'])
ll = (meta['CORNER_LL_LON_PRODUCT'], meta['CORNER_LL_LAT_PRODUCT'])
lr = (meta['CORNER_LR_LON_PRODUCT'], meta['CORNER_LR_LAT_PRODUCT'])
x1_l, y1_l = ll[0], ul[1]
x2_l, y2_l = ur[0], lr[1]

channels = []
# (lat_1, lon_1, lat_2, lon_2)
bbox = (47.834892, -86.006028, 47.633081, -85.546815)
for i in range(10):
    img = tiff.imread(path+image+'_B{}.TIF'.format(i+1))
    # print(img.shape)  # (height, width)
    x_scale = abs(x2_l-x1_l)/img.shape[1]  # degrees in 1 pixel
    y_scale = abs(y2_l-y1_l)/img.shape[0]
    x1_b = abs(bbox[1]-x1_l)/x_scale
    x2_b = abs(bbox[3]-x1_l)/x_scale
    y1_b = abs(bbox[0]-y1_l)/y_scale
    y2_b = abs(bbox[2]-y1_l)/y_scale
    x1_b, x2_b = math.floor(min(x1_b, x2_b)), math.ceil(max(x1_b, x2_b))
    y1_b, y2_b = math.floor(min(y1_b, y2_b)), math.ceil(max(y1_b, y2_b))
    if i == 0:
        size = (x2_b-x1_b, y2_b-y1_b)
        # print(size)
    channels.append(cv.resize(
        img[y1_b:y2_b+1, x1_b:x2_b+1], size, interpolation=cv.INTER_AREA))

result_image = np.stack((channels[0], channels[1], channels[2], channels[3], channels[4],
                        channels[5], channels[6], channels[7], channels[8], channels[9]), axis=-1)
cv.imshow('cropped image', np.concatenate(
    (result_image[:, :, 7:8], result_image[:, :, 6:7], result_image[:, :, 2:3]), axis=2))
cv.waitKey(0)
