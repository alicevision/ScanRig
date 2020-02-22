from PySide2 import QtWidgets
from PySide2.QtCore import QObject, Slot, Property, Signal

from CameraPkg.capture_device_list import CaptureDeviceList
from UIPkg.image_provider import ImageProvider

import time

class CaptureDevicePreview(QObject):
    def __init__(self):
        super().__init__()
        self.captureDevices = CaptureDeviceList() # Empty list for now which accepts only one camera at a time (we use a list because of the common settings)
        self.imageProvider = ImageProvider(self.captureDevices)
        self.runningPreview = False
        self.currentId = -1


    @Slot(str)
    def changePreview(self, camId):
        camId = int(camId)
        self.currentId = camId

        if camId == -1 :
            self.runningPreview = False
            time.sleep(0.04)
            self.captureDevices.stopDevices()
            return

        if self.captureDevices.isEmpty() :
            self.captureDevices.addDevice(camId)
            self.captureDevices.setAllAttributesToDevices()
            self.runningPreview = True
        else:
            self.captureDevices.stopDevices()
            self.captureDevices.addDevice(camId)
            self.captureDevices.setAllAttributesToDevices()


    def getCamExposure(self):                             
        return self.captureDevices.settings["exposure"]                                                  
    
    @Slot(int)
    def setCamExposure(self, val):
        self.captureDevices.setExposure(val)

    @Signal
    def camExposureChanged(self):
        pass

    def getCamList(self):
        return self.captureDevices.listAvailableDevices()


    # PROPERTIES
    camExposure = Property(int, getCamExposure, setCamExposure, notify=camExposureChanged)