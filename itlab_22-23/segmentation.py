import utils.show
from utils.process import get_mask, get_image
import matplotlib.pyplot as plt
import numpy as np


def main():
    # coordinates in EPSG:4326
    bbox = [
      45.41748,
      56.194481,
      46.07666,
      56.544344
      ]
      # image will be picked in time interval
    time_interval = ("2022-08-22T00:00:00Z", "2022-08-23T00:00:00Z")

    x = get_image(bbox, time_interval)  # 5-channels image
    x = utils.show.rgb_410(x)  # RGB image
    model = "model-resnet34-adam-0008.h5"  # choose model from /models
    y = get_mask(bbox, time_interval, model)  # 1-channel mask, where pixels are in range [0, 1]

    # print images
    fig = plt.figure()
    plt.axis('off')
    plt.title("fire segmentation sample")
    a = fig.add_subplot(1, 2, 1)
    plt.imshow(x, interpolation='lanczos')
    a.set_title('image')
    a = fig.add_subplot(1, 2, 2)
    plt.imshow(y, interpolation='lanczos')
    a.set_title('mask')
    plt.show()


if __name__ == '__main__':
    main()
