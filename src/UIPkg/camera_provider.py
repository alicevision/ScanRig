import numpy as np
import cv2

from PySide2 import QtWidgets
from PySide2.QtCore import QSize
from PySide2.QtQuick import QQuickImageProvider
from PySide2.QtGui import QImage, QPixmap

class CameraProvider(QQuickImageProvider):
    def __init__(self, acquisition):
        super(CameraProvider, self).__init__(QQuickImageProvider.Pixmap)
        self.acquisition = acquisition

    def requestPixmap(self, id, size, requestedSize):
        frame = self.acquisition.captureDevices.getDevice(0).frame
        qImg = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888).rgbSwapped()
        return QPixmap.fromImage(qImg)

    def startAcquisition(self):
        self.acquisition.start()
