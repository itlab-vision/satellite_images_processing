'''
Data reader code
'''
import zipfile
import os
import rasterio

class DataRepresentaion:
    """
    How the data looks like
    """
    def __init__(self, data, meta, model_path, weight_path, ma_exist = False, ma_data = None):
        """
        Inicialization of the data
        """
        self.data = data
        self.meta = meta
        if ma_exist:
            self.ma_data = ma_data
        self.model_path = model_path
        self.weight_path = weight_path

class DataReader:
    """
    Class with mothods to read the data
    """
    def __init__(self, data_sourse, output, model_path, weight_path, ma_exist = False):
        """
        Inicialization of paths to data
        """
        self.data = data_sourse
        self.output = output
        self.model_path = model_path
        self.weight_path = weight_path
        self.ma_exist = ma_exist
        self.library = []

    def unzip(self):
        """
        Unziper
        """
        output = os.path.join(self.data, 'decompressed')
        os.makedirs(output, exist_ok = True)
        with zipfile.ZipFile(os.path.join(self.data, 'patches', 'landsat_patches.zip')) as zipper:
            zipper.extract(os.path.join('patches', ''), output)
            zipper.extract(os.path.join('mask', ''), output)
            zipper.extract(os.path.join('metadata', ''), output)
            if self.ma_exist:
                zipper.extract(os.path.join('manually_annotated', ''), output)
        self.data = output

    def create_library(self):
        """
        Creates the library from all files in folder
        """
        for i in os.walk(os.path.join(self.data, 'patches')):
            self.library.append(i)
        self.library = self.library[0][2]

    def get_data(self, index):
        """
        Main function
        """
        length = len(self.library)
        if index >= length:
            raise RuntimeError("Запрос несуществующего файла")
        file = os.path.splitext(self.library[index])
        if file[1] != '.tif':
            raise ValueError("Неподходящий тип файла")
        image = rasterio.open(os.path.join(self.data, 'patches',
            self.library[index])).read().transpose((1, 2, 0))
        with open(os.path.join(self.data, 'metadata', file[0] + '.txt'),
            "r", encoding = 'UTF-8') as meta:
            if self.ma_exist:
                ma_data = rasterio.open(os.path.join(self.data, 'manually_annotated',
                    self.library[index])).read().transpose((1, 2, 0))
                return DataRepresentaion(image, meta, self.model_path,
                    self.weight_path, True, ma_data)
            return DataRepresentaion(image, meta, self.model_path, self.weight_path)
