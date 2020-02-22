from PySide2 import QtWidgets
from PySide2.QtCore import QObject, Slot, Property, Signal

from acquisition import Acquisition
from capture_device_preview import CaptureDevicePreview
from UIPkg.image_provider import ImageProvider

import time

class Backend(QObject):
    def __init__(self):
        super().__init__()
        self.preview = CaptureDevicePreview()
        self.acquisition = Acquisition(self.preview.captureDevices.settings)


    @Slot()
    def startAcquisition(self):
        # JUST USED TO STOP ALL THE DEVICES AND THE OTHER THREAD
        self.preview.runningPreview = False
        time.sleep(0.04)
        self.preview.captureDevices.stopDevices()

        # Start acquisition
        self.acquisition.start()

        # Relaunch preview
        self.preview.changePreview(self.preview.currentId)