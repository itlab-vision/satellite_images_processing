import sys
import os
import functools
import qimage2ndarray
import design  # Это наш конвертированный файл дизайна
import numpy as np
import cv2 as cv

from PyQt5 import QtCore, QtGui, QtWebEngineWidgets, QtWebChannel
from PyQt5.QtWidgets import QDialog, QLineEdit, QDialogButtonBox, QLabel, QFormLayout, QMainWindow, QMessageBox, QApplication
from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer
from models.kumar_roy import KumarRoy64_10
from models.cloud_net import CloudNet

# Костыль
from skimage.io import imread


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


class SatelliteApp(QMainWindow, design.Ui_MainWindow):
    api = None
    ee = None
    # from earth explorer site https://ers.cr.usgs.gov
    username = ''
    password = ''
    # date - string
    year = None
    month = None
    day = None
    # loaded/choosen tiff image
    image = None
    models = []
    labels = []
    runs = 0

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Models initialize
        # Костыль
        self.fire = KumarRoy64_10('C://Users//Никита//Desktop//fire//model.h5')
        self.cloud = CloudNet('C://Users//Никита//Desktop//cloud//model.h5')

        self.models.append(self.fire)
        self.models.append(self.cloud)

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
        self.button_date.clicked.connect(self.choose_date)
        self.button_clear.clicked.connect(self.clear_markers)

        # Buttons

        self.button_analyze.clicked.connect(self.analyze)
        self.button_save.clicked.connect(self.save)
        self.button_exit.clicked.connect(self.exit)

        # Results

        self.labels.append(self.label_fire)
        self.labels.append(self.label_cloud)

        # Sign In

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
        left_up = (min(x[0], y[0]), min(x[1], y[1]))
        right_down = (max(x[0], y[0]), max(x[1], y[1]))
        return left_up, right_down

    # Map Properties

    def preview_mode(self):
        # debug
        return
        if self.image == None:
            return
        if self.ispreview:
            self.button_preview.setText('Preview mode')
            # remove web channel from self.view.page() ?

            self.gridLayout_2.removeWidget(self.view)
            # convert self.image/loaded tif to self.preview pixmap

            self.gridLayout_2.addWidget(self.preview)
            self.ispreview = False
        else:
            self.button_preview.setText('Map mode')
            self.gridLayout_2.removeWidget(self.preview)
            # set web channel to self.view.page() ?

            self.gridLayout_2.addWidget(self.view)
            self.ispreview = True

    def choose_date(self):
        # debug
        return
        # create new form/dialog to choose year, month and day as listbox/input_text/something

    def clear_markers(self):
        self.num_markers = 0
        self.markers[0] = (None, None)
        self.markers[1] = (None, None)
        self.view.page().runJavaScript("map.removeLayer(marker_1);")
        self.view.page().runJavaScript("map.removeLayer(marker_2);")

    # Buttons

    def analyze(self):
        if self.num_markers != 2:
            self.view.page().runJavaScript("alert_markers();")
            return
        if not self.authorize():
            return
        # координаты левого верхнего и правого нижнего угла изображения (lat, lng)
        x, y = self.norm_markers(self.markers[0], self.markers[1])
        # найти нужное изображение
        scenes = self.api.search(
            dataset='landsat_8_c1',
            latitude=(y[0]+x[0])/2,
            longitude=(y[1]+x[1])/2,
            bbox=(x[0], x[1], y[0], y[1]),
            start_date='2021-01-01',
            end_date='2021-03-01',
            max_cloud_cover=10  # hz how much is needed
        )
        # загрузить на комп
        #self.ee.download(
            #identifier=scenes[0]['display_id'], output_dir='./downloaded')
        # прочитать с компа в self.image
        # Костыль
        self.image = imread('C://Users//Никита//Desktop//fire//image.tif')

        i = 0
        for model in self.models:
            res = model.process(self.image)
            res = qimage2ndarray.array2qimage(res)
            self.labels[i].setPixmap(QtGui.QPixmap.fromImage(res))
            i += 1

    def save(self):
        i = 0
        for label in self.labels:
            img = qimage2ndarray.rgb_view(label.pixmap().toImage())
            cv.imwrite('res_model_{}_{}.png'.format(i, self.runs),
                       cv.cvtColor(img, cv.COLOR_RGB2BGR))
            i += 1
        self.runs += 1

    def exit(self):
        reply = QMessageBox.question(self, 'Message', 'Are you sure to exit?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.ee.logout()
            self.api.logout()
            self.close()

    # Results

    # Sign In

    def authorize(self):
        self.sign_in.exec_()
        self.username, self.password = self.sign_in.getLP()
        if self.username == '' or self.password == '':
            return False
        # добавить try catch блок
        self.api = API(self.username, self.password)
        self.ee = EarthExplorer(self.username, self.password)
        return True


def main():
    app = QApplication(sys.argv)
    window = SatelliteApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
