import numpy as np
import cv2

from PySide2 import QtWidgets
from PySide2.QtCore import QSize, QObject, Slot, Property
from PySide2.QtQuick import QQuickImageProvider
from PySide2.QtGui import QImage, QPixmap

class ImageProvider(QQuickImageProvider):
    """Class used to give the preview frame to QML"""
    def __init__(self, devices):
        """ImageProvider constructor.

        Args:
            devices ([UvcCamera]): List of UvcCamera. Designed to contain only one device. (not optimal)
        """
        super(ImageProvider, self).__init__(QQuickImageProvider.Pixmap)
        self.previewDevices = devices

    def requestPixmap(self, id, size, requestedSize):
        """Method to send the frame to QML."""
        camId = int(id.split("/")[0])
        if camId == -1: 
            return
        if self.previewDevices.isEmpty():
            return

        device = self.previewDevices.getDevice(0)

        frame = device.GetLastFrame() # Because we only have one device

        try: # OPENCV API
            qImg = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888).rgbSwapped()
        except AttributeError: # Happened with USBCAM API (we should make an if statement instead but we have a package issue)
            buffer = np.array(frame, copy=False)
            buffer = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
            qImg = QImage(buffer, buffer.shape[1], buffer.shape[0], QImage.Format_RGB888).rgbSwapped()

        return QPixmap.fromImage(qImg)