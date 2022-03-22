import sys
import os
import functools
import qimage2ndarray
import design
import math
import tarfile
import tifffile as tiff
import numpy as np
import cv2 as cv

from PyQt5 import QtCore, QtGui, QtWebEngineWidgets, QtWebChannel
from PyQt5.QtWidgets import QDialog, QLineEdit, QDialogButtonBox, QLabel, QFormLayout, QMainWindow, QMessageBox, QApplication
from landsatxplore.api import API
from landsatxplore.errors import EarthExplorerError
from landsatxplore.earthexplorer import EarthExplorer
from models.kumar_roy import KumarRoy64_10
from models.cloud_net import CloudNet


class SignIn(QDialog):
    def __init__(self):
        super(SignIn, self).__init__()

        self.login = QLineEdit(self)
        self.password = QLineEdit(self)
        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        label = QLabel(self)
        label.setText(
            "To use this application in on-line mode please enter yours login and password from earth explorer https://ers.cr.usgs.gov")

        layout = QFormLayout(self)
        layout.addWidget(label)
        layout.addRow("Login", self.login)
        layout.addRow("Password", self.password)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getLP(self):
        return self.login.text(), self.password.text()

# TODO finish choosing date
class Date(QDialog):
    def __init__(self, start, end):
        super(SignIn, self).__init__()

        # does it need to store?
        self.start = ''
        self.end = ''
        if start:
            self.start = start
        if end:
            self.end = end

        # listbox???
        self.start_date = None
        self.end_date = None

        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        label = QLabel(self)
        label.setText("Choose start and end date")

        layout = QFormLayout(self)
        layout.addWidget(label)
        # add dates
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getDate(self):
        # return properly
        return None, None


class SatelliteApp(QMainWindow, design.Ui_MainWindow):
    api = None
    ee = None
    # from earth explorer site https://ers.cr.usgs.gov
    username = ''
    password = ''
    start_date = None
    end_date = None
    image = None
    models = []
    labels = []
    runs = 0
    online = True

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Models initialize
        # Костыль
        self.fire = KumarRoy64_10('C://Users//Никита//Desktop//fire//model.h5')
        self.cloud = CloudNet('C://Users//Никита//Desktop//cloud//model.h5')

        # TODO relocate short names "fire" & "cloud" to a model classes as methods like CloudNet.get_type()
        # and with that, fix self.save() method
        self.models.append((self.fire, 'fire'))
        self.models.append((self.cloud, 'cloud'))

        # Map

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.channel = QtWebChannel.QWebChannel()
        self.channel.registerObject("SatelliteApp", self)
        self.view.page().setWebChannel(self.channel)

        file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets/map.html",
        )
        self.view.setUrl(QtCore.QUrl.fromLocalFile(file))
        self.gridLayout_2.addWidget(self.view)
        self.num_markers = 0
        self.markers = [(), ()]

        # Map Properties

        self.preview = QLabel(self)
        self.ispreview = False
        self.button_preview.clicked.connect(self.preview_mode)
        self.button_mode.clicked.connect(self.mode)
        self.button_clear.clicked.connect(self.clear_marker)

        # Buttons

        self.button_analyze.clicked.connect(self.analyze)
        self.button_save.clicked.connect(self.save)
        self.button_exit.clicked.connect(self.exit)

        # Results

        self.labels.append(self.label_fire)
        self.labels.append(self.label_cloud)

        # Sign in

        self.sign_in = SignIn()

    # Map

    @QtCore.pyqtSlot(float, float, result=int)
    def addMarker(self, lat, lng):
        if self.num_markers == 2:
            return 0
        self.num_markers += 1
        self.markers[self.num_markers-1] = (lat, lng)
        return self.num_markers

    def norm_markers(self, x, y):
        ul = (min(x[0], y[0]), min(x[1], y[1]))
        lr = (max(x[0], y[0]), max(x[1], y[1]))
        return ul, lr

    # Map Properties
    # TODO finish preview_mode
    def preview_mode(self):
        if self.image is None:
            return
        if self.ispreview:
            self.button_preview.setText('Preview mode')
            # remove web channel from self.view.page() ?
            # не работает так как надо, хмм...
            self.gridLayout_2.removeWidget(self.view)
            # работает только на тестовом изображении для fire detection!!!!!
            convert = np.concatenate(
                (self.image[:, :, 7:8], self.image[:, :, 6:7], self.image[:, :, 2:3]), axis=2)
            convert = qimage2ndarray.array2qimage(convert)
            self.preview.setPixmap(QtGui.QPixmap.fromImage(convert))
            self.gridLayout_2.addWidget(self.preview)
            self.ispreview = False
        else:
            self.button_preview.setText('Map mode')
            self.gridLayout_2.removeWidget(self.preview)
            # set web channel to self.view.page() ?

            self.gridLayout_2.addWidget(self.view)
            self.ispreview = True

    def mode(self):
        if self.online == True:
            self.online = False
            self.button_mode.setText("Online mode")
            # TODO implement ofline mode
        else:
            self.online = True
            self.button_mode.setText("Offline mode")

    def clear_marker(self):
        if self.num_markers == 2:
            self.markers[1] = (None, None)
            self.num_markers = 1
            self.view.page().runJavaScript("map.removeLayer(marker_2);")
        elif self.num_markers == 1:
            self.markers[0] = (None, None)
            self.num_markers = 0
            self.view.page().runJavaScript("map.removeLayer(marker_1);")

    # Buttons

    def analyze(self):
        if self.online == True:
            if self.num_markers != 2:
                self.view.page().runJavaScript("alert_markers();")
                return
            result = self.authorize()
            if result == False:
                return
            self.date = Date(self.start_date, self.end_date)
            self.date.exec_()
            self.start_date, self.end_date = self.date.getDate()

            # from landsat_downloader
            ul, lr = self.norm_markers(self.markers[0], self.markers[1])
            bbox = (ul[0], ul[1], lr[0], lr[1])
            scenes = self.api.search(
                dataset='landsat_8_c1',
                bbox=bbox,
                start_date=self.start_date,
                end_date=self.end_date,
                max_cloud_cover=10,
                max_results=1
            )
            image = scenes[0]['display_id']
            zip_path = os.path.abspath("")+'\\landsat_downloaded\\zips\\'
            images_path = zip_path[:-5]
            try:
                self.ee.download(identifier=image,
                                 output_dir=zip_path, dataset='landsat_8_c1')
                tar = tarfile.open(zip_path+image+'.tar.gz', 'r')
                tar.extractall(path=images_path+image)
            except EarthExplorerError as e:
                print(e, end='')
                print(' for ' + image + ' from dataset landsat_8_c1')

            # from cropper_demo
            with open(images_path+image+'_MTL.txt', 'r') as f:
                data = f.read().split('PRODUCT_METADATA')[1].split('\n')[14:22]
            meta = {}
            for info in data:
                meta[info.split('=')[0][4:-1]] = float(info.split('=')[1][1:])

            # lattitude = y, longitude = x on image
            ul = (meta['CORNER_UL_LON_PRODUCT'], meta['CORNER_UL_LAT_PRODUCT'])
            ur = (meta['CORNER_UR_LON_PRODUCT'], meta['CORNER_UR_LAT_PRODUCT'])
            ll = (meta['CORNER_LL_LON_PRODUCT'], meta['CORNER_LL_LAT_PRODUCT'])
            lr = (meta['CORNER_LR_LON_PRODUCT'], meta['CORNER_LR_LAT_PRODUCT'])
            x1_l, y1_l = ll[0], ul[1]
            x2_l, y2_l = ur[0], lr[1]

            channels = []
            for i in range(10):
                img = tiff.imread(images_path+image+'_B{}.TIF'.format(i+1))
                x_scale = abs(x2_l-x1_l)/img.shape[1]
                y_scale = abs(y2_l-y1_l)/img.shape[0]
                x1_b = abs(bbox[1]-x1_l)/x_scale
                x2_b = abs(bbox[3]-x1_l)/x_scale
                y1_b = abs(bbox[0]-y1_l)/y_scale
                y2_b = abs(bbox[2]-y1_l)/y_scale
                x1_b, x2_b = math.floor(
                    min(x1_b, x2_b)), math.ceil(max(x1_b, x2_b))
                y1_b, y2_b = math.floor(
                    min(y1_b, y2_b)), math.ceil(max(y1_b, y2_b))
                if i == 0:
                    size = (x2_b-x1_b, y2_b-y1_b)
                channels.append(cv.resize(
                    img[y1_b:y2_b+1, x1_b:x2_b+1], size, interpolation=cv.INTER_AREA))

            self.image = np.stack((channels[0], channels[1], channels[2], channels[3], channels[4],
                                   channels[5], channels[6], channels[7], channels[8], channels[9]), axis=-1)
        else:
            # Костыль
            self.image = tiff.imread(
                'C://Users//Никита//Desktop//fire//image.tif')

        i = 0
        for model in self.models:
            res = model[0].process(self.image)
            res = qimage2ndarray.array2qimage(res)
            self.labels[i].setPixmap(QtGui.QPixmap.fromImage(res))
            i += 1

    def save(self):
        i = 0
        for label in self.labels:
            img = qimage2ndarray.rgb_view(label.pixmap().toImage())
            cv.imwrite('res_{}_model_{}.png'.format(self.models[i][1], self.runs),
                       cv.cvtColor(img, cv.COLOR_RGB2BGR))
            i += 1
        self.runs += 1

    def exit(self):
        reply = QMessageBox.question(self, 'Message', 'Are you sure to exit?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.ee:
                self.ee.logout()
                self.api.logout()
            self.close()

    # Sign in

    def authorize(self):
        if self.username == '' or self.password == '':
            self.sign_in.exec_()
            self.username, self.password = self.sign_in.getLP()
            if self.username == '' or self.password == '':
                return False
            try:
                self.api = API(self.username, self.password)
                self.ee = EarthExplorer(self.username, self.password)
            except Exception as e:
                print(e)
        return True


def main():
    app = QApplication(sys.argv)
    window = SatelliteApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
