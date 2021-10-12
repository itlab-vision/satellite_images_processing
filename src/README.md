# Data processing pipelines

## Piplines


[fire_detection_pipeline.py](fire_detection_pipeline.py)

This script reads a folder with satellite images from .tiff files, performs segmentation using the fire detection Kumar-Roy model, and saves all segmentation results to binary Numpy files for further analysing.


## Datasets

Directory [datasets](datasets) contains implementations for data readers.

Each dataset class should implement an iterator inside itself to return a named turple with an input data tensor and a string containing some relative path (input image path for example). 

```python
from collections import namedtuple
DatasetBlob = namedtuple('DatasetBlob', 'data path')
blob = DatasetBlob(tensor, 'dataset/images/LC08_L1GT_117063_20200825_20200825_01_RT_p00847.tif')
data = blob.data
path = blob.path
```

More information about iteratiors and generators: https://webdevblog.ru/kak-sozdat-svoj-iterator-v-python/

## Models

Directory [models](models) contains implementations for DL models

Each DL model class should have a function "process", which gets satellite images as Numpy tensors, and return processing results as Numpy tensors.


## Savers 

Directory [storers](storers) contains implementations for data storers, which save processing results.

Each storer class should have function "store" which gets output tensor and path as parameters. 


## Data Visualizers

Directory [visualizers](visualizers) contains implementations for data visualizers, which can show processing results.


## High-level data analysers

In future

