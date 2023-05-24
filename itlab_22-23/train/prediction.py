# Prediction
import os
from numpy import asarray
import numpy as np
# training models
import tensorflow as tf
import keras
import segmentation_models as sm
from keras.models import load_model
# Segmentation Models: using `keras` framework.
os.environ["SM_FRAMEWORK"] = "tf.keras"
# optimizers
from keras.optimizers import Adam
from tensorflow_addons.optimizers import NovoGrad
# Hide GPU from visible devices
tf.config.set_visible_devices([], 'GPU')
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


def predict(batch, model_name):
    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
    loss = sm.losses.JaccardLoss(class_weights=(10,))
    custom_objects = {"jaccard_loss": loss,
                      "iou_score": sm.metrics.iou_score}

    model_path = os.path.join("models", model_name)
    model = load_model(model_path, custom_objects)

    return model.predict(batch, verbose=1)
