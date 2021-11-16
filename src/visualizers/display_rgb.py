import tifffile
import numpy as np
from matplotlib import pyplot as plt


class DisplayAsRGB():
    def __init__(self):
        pass

    # May be it's better to cut channels according to a model type
    # example: for kumar_roy fire detection to see how good result of model,
    # it's better to use 7 (swir3), 6(swir2), 2(blue) channels instead of 4(red), 3(green), 2(blue) to show,
    # at same time, for cloud_net cloud segmentation we get already prepared image and use first 3 channels
    def prepare(self, images):
        # Input - list if images\paths to images
        results = []
        for image in images:
            if isinstance(image, str):
                image = imread(image)
            elif not isinstance(image, np.ndarray):
                raise ValueError("image must be a numpy array or path to image")
            # --------- костыль
            if image.shape[2] >= 10:
                results.append(np.concatenate(
                    (image[:, :, 3:4], image[:, :, 2:3], image[:, :, 1:2]), axis=2))
            elif 3 < image.shape[2] < 10:
                results.append(image[:, :, 0:3])
            # -----------------
            elif image.shape[2] in (1, 3):
                results.append(image)
            else:
                raise ValueError(
                    "num of image channels must be 1 or 3 or more")
        # Output - list of images channels = 3 (RGB)
        return results

    def show(self, images):
        # Input - list if images\path to images len 2 or 1
        if len(images) > 2:
            raise AttributeError(
                "can visualize at most 2 images at the moment")
        rgb = self.prepare(images)
        fig, (input_image, output_image) = plt.subplots(1, 2, figsize=(12, 8))
        input_image.imshow(rgb[0])
        output_image.imshow(rgb[1])
        plt.show()
