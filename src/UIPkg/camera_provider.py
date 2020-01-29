#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide2 import QtWidgets
from PySide2.QtCore import QSize
from PySide2.QtQuick import QQuickImageProvider
from PySide2.QtGui import QImage, QPixmap, QColor
import cv2
import numpy as np

class CameraProvider(QQuickImageProvider):
    def __init__(self, parent=None):
        super(CameraProvider, self).__init__(QQuickImageProvider.Pixmap)
        self.cap = cv2.VideoCapture(0)

    def requestPixmap(self, id, size, requestedSize):
        ret, frame = self.cap.read()
        qImg = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888).rgbSwapped()
        return QPixmap.fromImage(qImg)

    def closeCamera(self):
        self.cap.release()
