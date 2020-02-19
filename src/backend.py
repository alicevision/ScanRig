from PySide2 import QtWidgets
from PySide2.QtCore import QObject, Slot, Property, Signal

from acquisition import Acquisition
from capture_device_preview import CaptureDevicePreview
from UIPkg.image_provider import ImageProvider

class Backend(QObject):
    def __init__(self):
        super().__init__()
        self.preview = CaptureDevicePreview()
        self.acquisition = Acquisition(self.preview.captureDevices.settings)


    @Slot()
    def startAcquisition(self):
        self.acquisition.start()
