import sys
import os
import functools
import qimage2ndarray
import design  # Это наш конвертированный файл дизайна
import numpy as np
import cv2 as cv

from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets, QtWebChannel
from models.kumar_roy import KumarRoy64_10
from models.cloud_net import CloudNet

# Костыль
from skimage.io import imread


class SatelliteApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    # from earth explorer site https://ers.cr.usgs.gov
    username = None
    password = None
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

        self.preview = QtWidgets.QLabel()
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

    # Map

    @QtCore.pyqtSlot(float, float)
    def onMapMove(self, lat, lng):
        self.label.setText("Lng: {:.5f}, Lat: {:.5f}".format(lng, lat))

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
        # create new form/message_box to choose year, month and day as listbox/input_text/something

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
        # координаты левого верхнего и правого нижнего угла изображения (lat, lng)
        x, y = self.norm_markers(self.markers[0], self.markers[1])
        # найти нужное изображение
        # загрузить на комп
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
        reply = QtWidgets.QMessageBox.question(self, 'Message', 'Are you sure to exit?',
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.close()

    # Results


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = SatelliteApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
