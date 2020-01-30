from PySide2 import QtWidgets
from PySide2.QtCore import QObject, Slot, Property, Signal

class Backend(QObject):
    def __init__(self, acquisition):
        super(Backend, self).__init__()
        self.acquisition = acquisition

    @Slot()
    def startAcquisition(self):
        self.acquisition.start()

    def getCamExposure(self):                             
        return self.acquisition.captureDevices.settings["exposure"]                                                  
    
    @Slot(int)
    def setCamExposure(self, val):
        self.acquisition.captureDevices.setExposure(val)

    @Signal
    def camExposureChanged(self):
        pass

    def getCamList(self):
        return self.acquisition.captureDevices.listAvailableDevices()
                                                                                                    
    camExposure = Property(int, getCamExposure, setCamExposure, notify=camExposureChanged)
