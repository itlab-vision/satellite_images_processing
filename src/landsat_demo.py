import tarfile
import numpy as np
from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer
from matplotlib import pyplot as plt
# Костыль (у меня не работает cv.imread в питоне)
from skimage.io import imread
from skimage.transform import resize

# your username & password from https://ers.cr.usgs.gov
username = ''
password = ''

# Initialize a new API instance and get an access key
api = API(username, password)
ee = EarthExplorer(username, password)

# Search for Landsat TM scenes
scenes = api.search(
    dataset='landsat_8_c1',
    latitude=50.85,  # center
    longitude=50.35,
    bbox=(50.65, 50.15, 51.05, 50.55),  # +- 0.2
    start_date='2021-01-01',
    end_date='2021-03-01',
    max_cloud_cover=10
)

print(f"{len(scenes)} scenes found.")

# Process the result
for scene in scenes:
    print(scene['display_id'])

image_name = scenes[0]['display_id']

ee.download(identifier=image_name, output_dir='./downloaded')
# Костыль
images_path = 'C:\\mygit\\ITLab\\satellite_images_processing\\src\\downloaded\\'
images = []
size = None
tar = tarfile.open(images_path+image_name+'.tar.gz', 'r')

for i in range(10):
    tar.extract(image_name + '_B{}.TIF'.format(i+1), images_path+image_name)
    image = imread(images_path+image_name + '\\' +
                   image_name + '_B{}.TIF'.format(i+1))
    if(i == 0):
        size = image.shape
    # ландсат выдает снимки разного размера
    image = resize(image, size, preserve_range=True, mode='symmetric')
    # предобработать картинки к рабочему формату

    images.append(image)

# result = np.stack((images[0], images[1], images[2], images[3], images[4],
    # images[5], images[6], images[7], images[8], images[9]), axis=-1)

# plt.imshow(np.concatenate(
    # (result[:, :, 3:4], result[:, :, 2:3], result[:, :, 1:2]), axis=2))
# plt.show()

ee.logout()
api.logout()
