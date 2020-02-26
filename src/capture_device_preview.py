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


    @Slot(result=bool)
    def getRunningPreview(self):
        return self.runningPreview


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
            self.runningPreview = False
            self.captureDevices.stopDevices()
            self.captureDevices.addDevice(camId)
            self.captureDevices.setAllAttributesToDevices()
            self.runningPreview = True

    @Slot()
    def getCamList(self):
        return self.captureDevices.listAvailableDevices()


    #----------- GETTERS & SETTERS FOR SETTINGS
    @Slot()
    def getCamExposure(self):                            
        return self.captureDevices.settings["exposure"]                                                  
    
    @Slot(int)
    def setCamExposure(self, val):
        self.captureDevices.setExposure(val)
        self.camExposureChanged.emit()

    camExposureChanged = Signal()
    camExposure = Property(int, getCamExposure, setCamExposure, notify=camExposureChanged)


    @Slot()
    def getCamBrightness(self):                             
        return self.captureDevices.settings["brightness"]                                                  
    
    @Slot(int)
    def setCamBrightness(self, val):
        self.captureDevices.setBrightness(val)
        self.camBrightnessChanged.emit()

    camBrightnessChanged = Signal()
    camBrightness = Property(int, getCamBrightness, setCamBrightness, notify=camBrightnessChanged)


    @Slot()
    def getCamContrast(self):                             
        return self.captureDevices.settings["contrast"]                                                  
    
    @Slot(int)
    def setCamContrast(self, val):
        self.captureDevices.setContrast(val)
        self.camContrastChanged.emit()

    camContrastChanged = Signal()
    camContrast = Property(int, getCamContrast, setCamContrast, notify=camContrastChanged)


    @Slot()
    def getCamSaturation(self):                             
        return self.captureDevices.settings["saturation"]                                                  
    
    @Slot(int)
    def setCamSaturation(self, val):
        self.captureDevices.setSaturation(val)
        self.camSaturationChanged.emit()

    camSaturationChanged = Signal()
    camSaturation = Property(int, getCamSaturation, setCamSaturation, notify=camSaturationChanged)


    @Slot()
    def getCamWhiteBalance(self):                             
        return self.captureDevices.settings["tempWB"]                                                  
    
    @Slot(int)
    def setCamWhiteBalance(self, val):
        self.captureDevices.setTempWB(val)
        self.camWhiteBalanceChanged.emit()

    camWhiteBalanceChanged = Signal()
    camWhiteBalance = Property(int, getCamWhiteBalance, setCamWhiteBalance, notify=camWhiteBalanceChanged)


    @Slot()
    def getCamGamma(self):                             
        return self.captureDevices.settings["gamma"]                                                  
    
    @Slot(int)
    def setCamGamma(self, val):
        self.captureDevices.setGamma(val)
        self.camGammaChanged.emit()

    camGammaChanged = Signal()
    camGamma = Property(int, getCamGamma, setCamGamma, notify=camGammaChanged)


    @Slot()
    def getCamGain(self):                             
        return self.captureDevices.settings["gain"]                                                  
    
    @Slot(int)
    def setCamGain(self, val):
        self.captureDevices.setGain(val)
        self.camGainChanged.emit()

    camGainChanged = Signal()
    camGain = Property(int, getCamGain, setCamGain, notify=camGainChanged)


    @Slot()
    def getCamSharpness(self):                             
        return self.captureDevices.settings["sharpness"]                                                  
    
    @Slot(int)
    def setCamSharpness(self, val):
        self.captureDevices.setSharpness(val)
        self.camSharpnessChanged.emit()

    camSharpnessChanged = Signal()
    camSharpness = Property(int, getCamSharpness, setCamSharpness, notify=camSharpnessChanged)