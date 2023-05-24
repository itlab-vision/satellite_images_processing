import os
import tensorflow as tf
import keras
import segmentation_models as sm
from keras.utils import load_img
import numpy as np
import imageio
from glob import glob
import math
from random import randint
from skimage.transform import rotate, rescale, resize

from tensorflow import keras
from keras.optimizers import Adam
from tensorflow.keras.optimizers.experimental import AdamW
from tensorflow_addons.optimizers import NovoGrad

import keras_tuner

# available GPUs

print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

# In[ ]:


# paths


# your project directory
project_dir = 'fire/'
'''
project_dir
 |
 | -- fire.py
 |
 | -- dataset
 |     | -- patches
 |          | -- folder1 
 |          | -- ...
 |     | -- masks
 |          | -- folder1 
 |          | -- ...
 |
 | -- predictions
 |     | -- hh-mm-ss
 |          | -- image.png
 |          | -- mask.png
 |          | -- predict.png      
 |     | -- ...


'''

# project paths
save_path = os.path.join(project_dir, 'model.h5')  # path for saving model
search_path = os.path.join(project_dir, 'hp_search-25-04-2023-2.h5')  # best during hp search
saved_images = os.path.join(project_dir, 'predictions')  # save all images here
dataset_dir = project_dir  # !!!!!!!!!!!!!!!
patches_dir = os.path.join(dataset_dir, 'patches')
masks_dir = os.path.join(dataset_dir, 'masks')

# Segmentation Models: using `keras` framework.
os.environ["SM_FRAMEWORK"] = "tf.keras"

# get paths

patches = glob(patches_dir + '/**/*.tif', recursive=True)
masks = glob(masks_dir + '/**/*.tif', recursive=True)

patches.sort()
masks.sort()
print('{0} patches and {1} masks were found'.format(len(patches), len(masks)))

annotated = list()
annotation = list()
for patch in patches:
    name = patch[-10:]
    batch = patch[13:52]
    if batch[1] == "a":
        batch = batch[15:]
    matched = filter(lambda x: batch in x and name in x, masks)
    matched = list(matched)
    try:
        mask = matched[0]
        annotation.append(mask)
        annotated.append(patch)
    except Exception as e:
        print("Exception {0} while searching for matched masks for patch {1}".format(e, patch))

patches = annotated
masks = annotation

# In[ ]:


# open images

max_ds_size = 14000
ds_size = min(max_ds_size, min(len(patches), len(masks)))
print('final dataset length: {0}'.format(ds_size))
print('validation split = 0.2')

channels = 5

# normalization layer
normalization = keras.layers.Normalization(axis=1)
adapt_data = np.empty(shape=(ds_size, 256, 256, channels), dtype=np.float32)
for i in range(ds_size):
    x = imageio.imread(patches[i])
    x = np.asarray(x).astype('float32')
    x = x.transpose((2, 0, 1))
    x = np.array([x[1], x[2], x[3], x[4], x[5]])
    x = x.transpose((1, 2, 0))
    adapt_data[i] = x
normalization.adapt(adapt_data, batch_size=100, steps=ds_size)
adapt_data = 0
# open and normalize
train_x = list()
train_y = list()
val_x = list()
val_y = list()
for i in range(ds_size):
    x = imageio.imread(patches[i])
    x = np.asarray(x).astype('float32')
    x = x.transpose((2, 0, 1))
    x = np.array([x[1], x[2], x[3], x[4], x[5]])
    x = x.transpose((1, 2, 0))
    x = normalization(x).numpy()[0]
    y = imageio.imread(masks[i])
    y = np.asarray(y).astype('float32')
    if (i % 5 == 0):
        val_x.append(x)
        val_y.append(y)
    else:
        train_x.append(x)
        train_y.append(y)

# Here we use ***channel last*** format
# image is a tensor with (H, W, C) shape, where C is a number of channels, H and W are image height and width.
#
# But rasterio opens image in ***channel first*** format, so you need to do `.transpose((1, 2, 0))`

# In[ ]:

# data generation and augmentation

# Here, `x_set` is list of patches
# and `y_set` is the list of masks


MAX_PIXEL_VALUE = 65535  # Max. pixel value, used to normalize the image


def augmentation(image, mask):
    if randint(0, 1) == 1:
        image = np.fliplr(image)
        mask = np.fliplr(mask)
    if randint(0, 1) == 1:
        image = np.flipud(image)
        mask = np.flipud(mask)
    angle = randint(-45, 45)
    image = rotate(image, angle, mode='symmetric')
    mask = rotate(mask, angle, mode='symmetric')
    return image, mask


class DataGenerator(tf.keras.utils.Sequence):

    def __init__(self, x_set, y_set, batch_size, augmentation=False, shuffle=True):
        self.x, self.y = x_set, y_set
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.index = 0
        self.on_epoch_end()

    def on_epoch_end(self):
        '''
        # good shuffle
        self.index = np.arange(len(self.indices))
        if self.shuffle == True:
            np.random.shuffle(self.index)
        '''
        # my shuffle
        index = randint(0, len(self) - 1)

    def __len__(self):
        return math.ceil(len(self.x) / self.batch_size)

    def __getitem__(self, index):
        batch_x = np.array(self.x[index * self.batch_size:(index + 1) *
                                                          self.batch_size])
        batch_y = np.array(self.y[index * self.batch_size:(index + 1) *
                                                          self.batch_size])
        if (augmentation):
            for x, y in zip(batch_x, batch_y):
                x, y = augmentation(x, y)
        return (batch_x, batch_y)

    def __next__(self):
        self.index += 1
        if (self.index >= len(self)):
            self.index = 0
        return self[self.index]


batch_size = 80
val_split = 0.2

train_generator = DataGenerator(train_x, train_y, batch_size, augmentation=True)
val_generator = DataGenerator(val_x, val_y, batch_size, augmentation=False)

# steps in model.fit()
steps = math.ceil(len(train_generator))
val_steps = math.ceil(len(val_generator))

# In[ ]:


# hyperparameter search


def build_model(hp):
    BACKBONE = hp.Choice('backbone', values=['resnet50', 'resnet101', 'efficientnetb4'])

    # модель - Unet
    model = sm.Unet(BACKBONE,
                    classes=1,
                    encoder_weights=None,
                    input_shape=(None, None, 5),
                    activation='sigmoid')

    lr = hp.Float('learning rate', min_value=0.0002, max_value=0.001, step = 0.0004)

    opt_list = [
        Adam(learning_rate=lr),
        NovoGrad(learning_rate=lr),
        AdamW(learning_rate=lr),
    ]
    opt_number = hp.Int('optimizer', min_value=0, max_value=len(opt_list) - 1)

    model.compile(
        opt_list[opt_number],
        loss=sm.losses.JaccardLoss(),
        metrics=[sm.metrics.IOUScore()],
    )
    return model


tuner = keras_tuner.BayesianOptimization(
    build_model,
    objective=keras_tuner.Objective("val_iou_score", direction="max"),
    overwrite=True,
    max_trials=12,
    # max_epochs=50,
)

tuner.search_space_summary()

tuner.search(
    train_generator,
    epochs=15,
    steps_per_epoch=steps,
    validation_data=val_generator,
    validation_steps=val_steps, )

tuner.results_summary(num_trials=12)
