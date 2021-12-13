import numpy as np
import cv2 as cv

from keras.models import *
from keras.layers import *


class KumarRoy64_10():

    def __init__(self, path, th_fire=0.25):
        self.model = self.get_model(
            input_height=256, input_width=256, n_filters=64, n_channels=10)
        self.model.load_weights(path)
        self.th_fire = th_fire

    def preprocess(self, image):
        if image.shape[2] < 10:
            raise ValueError("num of image channels must be more than 9")
        img = cv.resize(image, (256, 256), interpolation=cv.INTER_AREA)
        img = img[:, :, 0:10]
        return img

    def process(self, image):
        # Input: numpy array (image) of shape (256, 256, 10) width x height x channels
        if isinstance(image, list):
            res = []
            for img in image:
                t = self.preprocess(img)
                t = self.model.predict(np.array([t]), batch_size=None)
                t = t[0, :, :, 0] > self.th_fire
                t = np.array(t * 255, dtype=np.uint8)
                res.append(t)
        elif isinstance(image, np.ndarray):
            res = self.preprocess(image)
            res = self.model.predict(np.array([res]), batch_size=None)
            res = res[0, :, :, 0] > self.th_fire
            res = np.array(res * 255, dtype=np.uint8)
        else:
            raise ValueError(
                "image must be a numpy array or list of numpy arrays")
        # Output: numpy array (mask) of shape (256, 256) width x height
        return res

    def conv2d_block(self, input_tensor, n_filters, kernel_size=3, batchnorm=True):
        # first layer
        x = Conv2D(filters=n_filters, kernel_size=(kernel_size, kernel_size), kernel_initializer="he_normal",
                   padding="same")(input_tensor)
        if batchnorm:
            x = BatchNormalization()(x)
        x = Activation("relu")(x)

        # second layer
        x = Conv2D(filters=n_filters, kernel_size=(kernel_size, kernel_size), kernel_initializer="he_normal",
                   padding="same")(x)
        if batchnorm:
            x = BatchNormalization()(x)
        x = Activation("relu")(x)
        return x

    def get_unet(self, nClasses, input_height=256, input_width=256, n_filters=16, dropout=0.1, batchnorm=True, n_channels=10):
        input_img = Input(shape=(input_height, input_width, n_channels))

        # contracting path
        c1 = self.conv2d_block(input_img, n_filters=n_filters*1,
                               kernel_size=3, batchnorm=batchnorm)
        p1 = MaxPooling2D((2, 2))(c1)
        p1 = Dropout(dropout)(p1)

        c2 = self.conv2d_block(p1, n_filters=n_filters*2,
                               kernel_size=3, batchnorm=batchnorm)
        p2 = MaxPooling2D((2, 2))(c2)
        p2 = Dropout(dropout)(p2)

        c3 = self.conv2d_block(p2, n_filters=n_filters*4,
                               kernel_size=3, batchnorm=batchnorm)
        p3 = MaxPooling2D((2, 2))(c3)
        p3 = Dropout(dropout)(p3)

        c4 = self.conv2d_block(p3, n_filters=n_filters*8,
                               kernel_size=3, batchnorm=batchnorm)
        p4 = MaxPooling2D(pool_size=(2, 2))(c4)
        p4 = Dropout(dropout)(p4)

        c5 = self.conv2d_block(p4, n_filters=n_filters*16,
                               kernel_size=3, batchnorm=batchnorm)

        # expansive path
        u6 = Conv2DTranspose(n_filters*8, (3, 3),
                             strides=(2, 2), padding='same')(c5)
        u6 = concatenate([u6, c4])
        u6 = Dropout(dropout)(u6)
        c6 = self.conv2d_block(u6, n_filters=n_filters*8,
                               kernel_size=3, batchnorm=batchnorm)

        u7 = Conv2DTranspose(n_filters*4, (3, 3),
                             strides=(2, 2), padding='same')(c6)
        u7 = concatenate([u7, c3])
        u7 = Dropout(dropout)(u7)
        c7 = self.conv2d_block(u7, n_filters=n_filters*4,
                               kernel_size=3, batchnorm=batchnorm)

        u8 = Conv2DTranspose(n_filters*2, (3, 3),
                             strides=(2, 2), padding='same')(c7)
        u8 = concatenate([u8, c2])
        u8 = Dropout(dropout)(u8)
        c8 = self.conv2d_block(u8, n_filters=n_filters*2,
                               kernel_size=3, batchnorm=batchnorm)

        u9 = Conv2DTranspose(n_filters*1, (3, 3),
                             strides=(2, 2), padding='same')(c8)
        u9 = concatenate([u9, c1], axis=3)
        u9 = Dropout(dropout)(u9)
        c9 = self.conv2d_block(u9, n_filters=n_filters*1,
                               kernel_size=3, batchnorm=batchnorm)

        outputs = Conv2D(1, (1, 1), activation='sigmoid')(c9)
        model = Model(inputs=[input_img], outputs=[outputs])
        return model

    def get_model(self, nClasses=1, input_height=128, input_width=128, n_filters=16, dropout=0.1, batchnorm=True, n_channels=10):
        model = self.get_unet

        return model(
            nClasses=nClasses,
            input_height=input_height,
            input_width=input_width,
            n_filters=n_filters,
            dropout=dropout,
            batchnorm=batchnorm,
            n_channels=n_channels
        )
