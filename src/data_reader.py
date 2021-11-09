import zipfile
import os
import cv2
from sklearn.model_selection import train_test_split
import glob
import csv
import numpy as np
import pandas as pd
import shutil
import subprocess
from keras.callbacks import ModelCheckpoint, EarlyStopping
import keras
import rasterio

'''class TrainDataRepresentation:
    def __init__(self, train_generator, steps_per_epoch, validation_data, validation_steps, callbacks, output):
        self.train_generator = train_generator
        self.steps_per_epoch = steps_per_epoch
        self.validation_data = validation_data
        self.validation_steps = validation_steps
        self.callbacks = callbacks
        self.output = output'''

class DataRepresentaion:
    def __init__(self, data, meta, model_path, weight_path ma_exist = False, ma_data = None):
        self.data = data
        self.meta = meta
        if ma_exist:
            self.ma_data = ma_data
        self.model_path = model_path
        self.weight_path = weight_path

class DataReader:
    def __init__(self, data_sourse, output, model_path, weight_path, ma_exist = False):
        self.data = data_sourse
        self.output = output
        self.model_path = model_path
        self.weight_path = weight_path
        self.ma_exist = ma_exist

    def unzip(self):
        output = os.path.join(self.data, 'decompressed')
        os.makedirs(output, exist_ok = True)
        with zipfile.ZipFile(os.path.join(self.data, 'patches', 'landsat_patches.zip')) as zip:
            zip.extract(os.path.join('patches', ''), output)
            zip.extract(os.path.join('mask', ''), output)
            zip.extract(os.path.join('metadata', ''), output)
            if (self.ma_exist):
                zip.extract(os.path.join('manually_annotated', ''), output)
        self.data = output
     
    def create_library(self):
        self.library = []
        for i in os.walk(os.path.join(self.data, 'patches')):
            self.library.append(i)
        self.library = self.library[0][2]
        
    def get_data(self, index):
        ln = len(self.library)
        if index >= ln:
            raise RuntimeError("Запрос несуществующего файла")
        file = os.path.splitext(self.library[index])
        if file[1] != '.tif':
            raise ValueError("Неподходящий тип файла")
        image = rasterio.open(os.path.join(self.data, 'patches', self.library[index])).read().transpose((1, 2, 0))
        meta = open(os.path.join(self.data, 'metadata', file[0] + '.txt'))
        if self.ma_exist:
            ma_data = rasterio.open(os.path.join(self.data, 'manually_annotated', self.library[index])).read().transpose((1, 2, 0))
            return DataRepresentaion(image, meta, self.model_path, self.weight_path, True, ma_data)
        return DataRepresentaion(image, meta, self.model_path, self.weight_path)