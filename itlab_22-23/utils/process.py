from utils.landsat_downloader import download
from train.prediction import predict
import numpy as np
import os
from PIL import Image
import math


DEFAULT_MODEL = "model-resnet34-adam-0008.h5"
MIN_LONGITUDE_DELTA = 0.18
MIN_LATITUDE_DELTA = 0.1


def date_to_interval(date):
    return "{0}T00:00:00Z".format(date), "{0}T23:59:59Z".format(date)


def request_size(bbox):
    size = math.ceil((bbox[2] - bbox[0]) / MIN_LONGITUDE_DELTA)
    size *= 256
    return size


def get_mask(bbox, time_interval, model=DEFAULT_MODEL):
    assert (bbox[2] > bbox[0] and bbox[3] > bbox[1])
    """
    date is a string in format "yyyy-mm-dd"
    where y - year, m - month, d - day
    """
    x = get_image(bbox, time_interval, rescale=True, type=np.float32)
    y = get_valid_area_mask(x, model)
    
    return y


def get_image(bbox, time_interval, rescale=False, type=np.uint8):
    assert (bbox[2] > bbox[0] and bbox[3] > bbox[1])
    """
    date is a string in format "yyyy-mm-dd"
    where y - year, m - month, d - day
    """
    if bbox[2] - bbox[0] > MIN_LONGITUDE_DELTA * 9:
        im1 = get_image(
            [bbox[0],
             bbox[1],
             float((bbox[0] + bbox[2]) / 2),
             bbox[3],
             ],
            time_interval)
        im2 = get_image(
            [float((bbox[0] + bbox[2]) / 2),
             bbox[1],
             bbox[2],
             bbox[3],
             ],
            time_interval)
        return np.concatenate((im1, im2), axis=1)
    elif bbox[3] - bbox[1] > MIN_LATITUDE_DELTA * 9:
        im1 = get_image(
            [bbox[0],
             bbox[1],
             bbox[2],
             float((bbox[3] + bbox[1]) / 2),
             ],
            time_interval)
        im2 = get_image(
            [bbox[0],
             float((bbox[3] + bbox[1]) / 2),
             bbox[2],
             bbox[3],
             ],
            time_interval)
        return np.concatenate((im2, im1), axis=0)
    else:
        size = request_size(bbox)
        x = download(bbox, time_interval, rescale=rescale, width=size, height=size)
        x = x.astype(type)
        return x
        

def split(im, width = 256, heigth = 256):
    M = width
    N = heigth
    tiles = [im[u:u+M,v:v+N] for u in range(0,im.shape[0],M) for v in range(0,im.shape[1],N)]
    return np.asarray(tiles)


def get_valid_area_mask(x, model):
    batch = split(x)
    mask_batch = predict(batch, model)
    mask = np.empty((x.shape[0], x.shape[1], 1))
    N = mask.shape[0] // 256

    for i in range(0, N):
        for j in range(0, N):
            u = i*256
            v = j*256
            mask[u:u+256, v:v+256] = mask_batch[i*N + j]

    return mask
