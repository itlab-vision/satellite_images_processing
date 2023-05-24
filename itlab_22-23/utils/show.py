import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os


def true_rgb(x):
    # return image with 3 channels:
    # visible red, green and blue
    image_rgb = x.transpose(2, 0, 1)
    image_rgb = np.array([image_rgb[2], image_rgb[1], image_rgb[0]])
    image_rgb = image_rgb.transpose((1, 2, 0))
    return image_rgb


def rgb_410(x):
    # return image with 3 channels:
    # shortwave infrared as red, visible green and blue
    image_rgb = x.transpose(2, 0, 1)
    image_rgb = np.array([image_rgb[4], image_rgb[1], image_rgb[0]])
    image_rgb = image_rgb.transpose((1, 2, 0))
    return image_rgb


def show(image, title="image"):
    image *= (255 / np.max(image))
    image = image.astype(np.uint8)
    if image.shape[0] == 1:
        image = image.astype(np.uint8)
        image = image[:, :, 0]

    plt.title(title)
    plt.imshow(image, interpolation='nearest')
    plt.show()


def save_rgb(img, path, name):
    img *= 255
    img = img.astype(np.uint8)
    img = Image.fromarray(img)
    img.save(os.path.join(path, name))


def save_grayscale(img, path, name):
    img *= 255
    img = img.astype(np.uint8)
    img = img[:, :, 0]
    img = Image.fromarray(img, 'L')
    img.save(os.path.join(path, name))
