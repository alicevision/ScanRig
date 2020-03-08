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

    @Slot()
    def getCurrentId(self):   
        return self.currentId                                        
    
    @Slot(int)
    def setCurrentId(self, val):
        self.currentId = val
        self.currentIdChanged.emit()

    currentIdChanged = Signal()
    currentIdProperty = Property(int, getCurrentId, setCurrentId, notify=currentIdChanged)


    @Slot(result=bool)
    def getRunningPreview(self):
        return self.runningPreview


    @Slot(str)
    def changePreview(self, camId):
        camId = int(camId)
        self.setCurrentId(camId)

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
                existingDevice.changeResolution(draft=True)
                self.previewDevices.devices.append(existingDevice)
            else:
                self.previewDevices.addUvcCamera(self.currentId)

        for sig in self.signals:
            sig.emit()
        self.runningPreview = True
        

    @Slot(result="QVariantList")
    def getAvailableUvcCameras(self):
        return self.previewDevices.availableUvcCameras()

    @Slot(result="QStringList")
    def getAvailableUvcResolutions(self):
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera):
                printableResolutions = []

                for elt in device.resolutions:
                    txt = f'{elt[0]}x{elt[1]}'
                    printableResolutions.append(txt)

                return printableResolutions
            else:
                return ""

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
        signals.append(self.cameraResolutionChanged)

        return signals



    @Slot(result=str)
    def getCameraDraftResolution(self):
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera):
                res = device.getDraftResolution()
                return f'{res[0]}x{res[1]}'           
            else:
                return ""
        else:
            return ""

    @Slot(str)
    def setCameraDraftResolution(self, string):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera):
                # Stop the preview
                self.runningPreview = False
                time.sleep(0.1)

                # Get resolution from string
                res = string.split("x")
                w = int(res[0])
                h = int(res[1])
                # Set resolution
                device.setDraftResolution(w, h)
                device.changeResolution(draft=True)

                # Run again the preview
                self.runningPreview = True
                self.cameraDraftResolutionChanged.emit()

    cameraDraftResolutionChanged = Signal()
    cameraDraftResolution = Property(str, getCameraDraftResolution, setCameraDraftResolution, notify=cameraDraftResolutionChanged)


    @Slot(result=str)
    def getCameraResolution(self):
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera):             
                res = device.getResolution()
                return f'{res[0]}x{res[1]}'
            else:
                return ""
        else:
            return ""

    @Slot(str)
    def setCameraResolution(self, string):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, UvcCamera):
                # Get resolution from string
                res = string.split("x")
                w = int(res[0])
                h = int(res[1])
                # Set resolution in the dictionnary only (the preview is not affected)
                device.setResolution(w, h)
                self.cameraResolutionChanged.emit()

    cameraResolutionChanged = Signal()
    cameraResolution = Property(str, getCameraResolution, setCameraResolution, notify=cameraResolutionChanged)  


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