from PySide2 import QtWidgets
from PySide2.QtCore import QObject, Slot, Property, Signal

from CameraPkg.capture_device_list import CaptureDeviceList
from CameraPkg.uvc_camera import UvcCamera
from UIPkg.image_provider import ImageProvider

import time


# ONLY ONE CAMERA IN PREVIEW AT A TIME
class CaptureDevicePreview(QObject):
    def __init__(self, acquisitionDevices):
        super().__init__()
        self.previewDevices = CaptureDeviceList() # We have to use a list for the imageProvider even if we only have one camera
        self.runningPreview = False
        self.currentId = -1
        self.imageProvider = ImageProvider(self.previewDevices)
        self.acquisitionDevices = acquisitionDevices
        self.signals = self.initSignals()


    @Slot(result=bool)
    def getRunningPreview(self):
        return self.runningPreview


    @Slot(str)
    def changePreview(self, camId):
        camId = int(camId)
        self.currentId = camId

        # If "No Selected Device" is chosen
        if self.currentId == -1 :
            self.runningPreview = False
            time.sleep(0.04)
            self.previewDevices.stopDevices()
            self.previewDevices.emptyDevices()

            for sig in self.signals:
                sig.emit()
            return

        # Check if the device is already in the acquisition list
        existingDevice = self.acquisitionDevices.getDeviceByCamId(self.currentId)

        # Stop the preview for a moment
        self.runningPreview = False
        self.previewDevices.stopDevices()

        if self.previewDevices.isEmpty() :
            if existingDevice:
                print("existing device")
                existingDevice.start()
                self.previewDevices.devices.append(existingDevice)
            else:
                self.previewDevices.addUvcCamera(self.currentId)

        for sig in self.signals:
            sig.emit()
        self.runningPreview = True
        

    @Slot(result="QVariantList")
    def getAvailableUvcCameras(self):
        return self.previewDevices.availableUvcCameras()

    @Slot()
    def addRemoveDeviceToAcquisition(self):
        if self.currentId == -1:
            return
            
        device = self.previewDevices.getDevice(0)

        if device in self.acquisitionDevices.devices:
            self.acquisitionDevices.devices.remove(device)
            print("Device removed from the Acquisition Process")
        else:
            self.acquisitionDevices.devices.append(device)
            print("Device added to Acquisition Process")

    @Slot(result=bool)
    def isCurrentDeviceInAcquisition(self):
        if self.currentId == -1:
            return False
        else:
            return self.acquisitionDevices.isDeviceIn(self.currentId)

    @Slot(result="QVariantList")
    def getDevicesInAcquisition(self):
        return self.acquisitionDevices.getDevicesNames()



    #----------- GETTERS & SETTERS FOR UVC CAMERAS SETTINGS
    def initSignals(self):
        signals = []
        signals.append(self.cameraExposureChanged)
        signals.append(self.cameraBrightnessChanged)
        signals.append(self.cameraContrastChanged)
        signals.append(self.cameraSaturationChanged)
        signals.append(self.cameraWhiteBalanceChanged)
        signals.append(self.cameraGammaChanged)
        signals.append(self.cameraGainChanged)
        signals.append(self.cameraSharpnessChanged)
        signals.append(self.cameraDraftResolutionChanged)

        return signals



    @Slot(result=str)
    def getCameraDraftResolution(self):
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera):                 
                return device.getDraftResolution()
            else:
                return ""
        else:
            return ""

    @Slot(str)
    def setCameraDraftResolution(self, string):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera): 
                self.runningPreview = False
                time.sleep(0.1)
                device.setDraftResolution(string)
                self.runningPreview = True
                self.cameraDraftResolutionChanged.emit()

    cameraDraftResolutionChanged = Signal()
    cameraDraftResolution = Property(str, getCameraDraftResolution, setCameraDraftResolution, notify=cameraDraftResolutionChanged)  


    @Slot()
    def getCameraExposure(self):
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera):                     
                return device.settings["exposure"]
            else:
                return 0
        else:
            return 0                                              
    
    @Slot(int)
    def setCameraExposure(self, val):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera): 
                device.setExposure(val)
                self.cameraExposureChanged.emit()

    cameraExposureChanged = Signal()
    cameraExposure = Property(int, getCameraExposure, setCameraExposure, notify=cameraExposureChanged)
    

    @Slot()
    def getCameraBrightness(self):   
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera):                     
                return device.settings["brightness"]
            else:
                return 0
        else:
            return 0                                                
    
    @Slot(int)
    def setCameraBrightness(self, val):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera): 
                device.setBrightness(val)
                self.cameraBrightnessChanged.emit()

    cameraBrightnessChanged = Signal()
    cameraBrightness = Property(int, getCameraBrightness, setCameraBrightness, notify=cameraBrightnessChanged)


    @Slot()
    def getCameraContrast(self):  
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera):                     
                return device.settings["contrast"]
            else:
                return 0
        else:
            return 0                                            
    
    @Slot(int)
    def setCameraContrast(self, val):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera): 
                device.setContrast(val)
                self.cameraContrastChanged.emit()

    cameraContrastChanged = Signal()
    cameraContrast = Property(int, getCameraContrast, setCameraContrast, notify=cameraContrastChanged)


    @Slot()
    def getCameraSaturation(self):   
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera):                     
                return device.settings["saturation"]
            else:
                return 0
        else:
            return 0                                            
    
    @Slot(int)
    def setCameraSaturation(self, val):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera): 
                device.setSaturation(val)
                self.cameraSaturationChanged.emit()

    cameraSaturationChanged = Signal()
    cameraSaturation = Property(int, getCameraSaturation, setCameraSaturation, notify=cameraSaturationChanged)


    @Slot()
    def getCameraWhiteBalance(self):  
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera):                     
                return device.settings["tempWB"]
            else:
                return 0
        else:
            return 0                                           
    
    @Slot(int)
    def setCameraWhiteBalance(self, val):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera): 
                device.setTempWB(val)
                self.cameraWhiteBalanceChanged.emit()

    cameraWhiteBalanceChanged = Signal()
    cameraWhiteBalance = Property(int, getCameraWhiteBalance, setCameraWhiteBalance, notify=cameraWhiteBalanceChanged)


    @Slot()
    def getCameraGamma(self):  
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera):                     
                return device.settings["gamma"]
            else:
                return 0
        else:
            return 0                                              
    
    @Slot(int)
    def setCameraGamma(self, val):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera): 
                device.setGamma(val)
                self.cameraGammaChanged.emit()

    cameraGammaChanged = Signal()
    cameraGamma = Property(int, getCameraGamma, setCameraGamma, notify=cameraGammaChanged)


    @Slot()
    def getCameraGain(self):    
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera):                     
                return device.settings["gain"]
            else:
                return 0
        else:
            return 0                                            
    
    @Slot(int)
    def setCameraGain(self, val):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera): 
                device.setGain(val)
                self.cameraGainChanged.emit()

    cameraGainChanged = Signal()
    cameraGain = Property(int, getCameraGain, setCameraGain, notify=cameraGainChanged)


    @Slot()
    def getCameraSharpness(self):   
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera):                     
                return device.settings["sharpness"]
            else:
                return 0
        else:
            return 0                                                  
    
    @Slot(int)
    def setCameraSharpness(self, val):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera): 
                device.setSharpness(val)
                self.cameraSharpnessChanged.emit()

    cameraSharpnessChanged = Signal()
    cameraSharpness = Property(int, getCameraSharpness, setCameraSharpness, notify=cameraSharpnessChanged)