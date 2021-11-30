import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
import design  # Это наш конвертированный файл дизайна
from design import QtGui

# Костыль
from models.kumar_roy import KumarRoy64_10
from models.cloud_net import CloudNet
from skimage.io import imread
from skimage.transform import resize
import qimage2ndarray
import numpy as np
import cv2 as cv


class SatelliteApp(QtWidgets.QMainWindow, design.Ui_MainWindow):

    models = []
    labels = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py

        # Models initialize
        # Костыль
        self.fire = KumarRoy64_10('C://Users//Никита//Desktop//fire//model.h5')
        self.cloud = CloudNet('C://Users//Никита//Desktop//cloud//model.h5')
        self.models.append(self.fire)
        self.models.append(self.cloud)

        # Map

        # Map Properties

        # Buttons

        self.button_analyze.clicked.connect(self.analyze)
        self.button_save.clicked.connect(self.save)
        self.button_exit.clicked.connect(self.exit)

        # Results
        # Костыль
        self.labels.append(self.label_fire)
        self.labels.append(self.label_cloud)

    # Map

    # Map Properties

    # Buttons

    def analyze(self):
        # запускаем модели и заполняем pixmap
        # соответствующих label
        # Костыль
        images = []
        # это разные image!
        image = imread('C://Users//Никита//Desktop//fire//image.tif')
        print(image.shape)
        images.append(image)
        image = imread('C://Users//Никита//Desktop//cloud//image.tif')
        images.append(image)

        i = 0
        for model in self.models:
            res = model.process(images[i])
            res = qimage2ndarray.array2qimage(res)
            self.labels[i].setPixmap(QtGui.QPixmap.fromImage(res))
            i += 1

        return

    def save(self):
        # берем из каждой label в results of models pixmap
        # конвертим в np.ndarray и сохраняем
        # Костыль
        i = 0
        for label in self.labels:
            image = qimage2ndarray.rgb_view(label.pixmap().toImage())
            cv.imwrite('res_model_{}.png'.format(i), cv.cvtColor(image, cv.COLOR_RGB2BGR))
            i += 1

        return

    def exit(self):
        reply = QtWidgets.QMessageBox.question(self, 'Message', 'Are you sure to exit?',
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.close()
        return

    # Results


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = SatelliteApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
