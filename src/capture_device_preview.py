from PySide2 import QtWidgets
from PySide2.QtCore import QObject, Slot, Property, Signal

from CameraPkg.capture_device_list import CaptureDeviceList
from CameraPkg.opencv_camera import OpencvCamera
from CameraPkg.i_uvc_camera import CameraSetting
from UIPkg.image_provider import ImageProvider
from streaming_api import StreamingAPI

import time


# ONLY ONE CAMERA IN PREVIEW AT A TIME
class CaptureDevicePreview(QObject):
    def __init__(self, acquisitionDevices, streamingAPI):
        super().__init__()
        self.streamingAPI = streamingAPI
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
            self.previewDevices.emptyDevices()

            for sig in self.signals:
                sig.emit()
            return

        # Check if the device is already in the acquisition list
        existingDevice = self.acquisitionDevices.getDeviceByCamId(self.currentId)

        # Stop the preview for a moment
        self.runningPreview = False

        if self.previewDevices.isEmpty() :
            if existingDevice:
                print("existing device")
                self.previewDevices.devices.append(existingDevice)
            else:
                self.previewDevices.addOpencvCamera(self.currentId)

        for sig in self.signals:
            sig.emit()
        self.runningPreview = True
        

    @Slot(result="QVariantList")
    def getAvailableOpencvCameras(self):
        return self.previewDevices.availableOpencvCameras()

    @Slot(result="QStringList")
    def getAvailableUvcResolutions(self):
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera):
                printableResolutions = []

                for elt in device.formats:
                    txt = f'{elt["width"]}x{elt["height"]}'
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
        signals.append(self.cameraFormatChanged)
        signals.append(self.cameraAcquisitionFormatChanged)

        return signals



    @Slot(result=str)
    def getCameraFormat(self):
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera):
                res = device.GetFormat()
                return f'{res["width"]}x{res["height"]}'           
            else:
                return ""
        else:
            return ""

    @Slot(str)
    def setCameraFormat(self, string):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera):
                # Stop the preview
                self.runningPreview = False
                time.sleep(0.1)

                # Get resolution from string
                res = string.split("x")
                w = int(res[0])
                h = int(res[1])
                # Set resolution
                device.SetFormat({"width":w, "height":h})

                # Run again the preview
                self.runningPreview = True
                self.cameraFormatChanged.emit()

    cameraFormatChanged = Signal()
    cameraFormat = Property(str, getCameraFormat, setCameraFormat, notify=cameraFormatChanged)


    @Slot(result=str)
    def getCameraAcquisitionFormat(self):
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera):             
                res = device.GetAcquisitionFormat()
                return f'{res["width"]}x{res["height"]}' 
            else:
                return ""
        else:
            return ""

    @Slot(str)
    def setCameraAcquisitionFormat(self, string):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera):
                # Get resolution from string
                res = string.split("x")
                w = int(res[0])
                h = int(res[1])
                # Set acquisition format in the attribute only (the preview is not affected)
                device.SetAcquisitionFormat({"width":w, "height":h})
                self.cameraAcquisitionFormatChanged.emit()

    cameraAcquisitionFormatChanged = Signal()
    cameraAcquisitionFormat = Property(str, getCameraAcquisitionFormat, setCameraAcquisitionFormat, notify=cameraAcquisitionFormatChanged)  


    @Slot()
    def getCameraExposure(self):
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera):                  
                return device.GetSetting(CameraSetting.EXPOSURE)
            else:
                return 0
        else:
            return 0                                              
    
    @Slot(int)
    def setCameraExposure(self, val):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera): 
                device.SetSetting(CameraSetting.EXPOSURE, val)
                self.cameraExposureChanged.emit()

    cameraExposureChanged = Signal()
    cameraExposure = Property(int, getCameraExposure, setCameraExposure, notify=cameraExposureChanged)
    

    @Slot()
    def getCameraBrightness(self):   
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera):                     
                return device.GetSetting(CameraSetting.BRIGHTNESS)
            else:
                return 0
        else:
            return 0                                                
    
    @Slot(int)
    def setCameraBrightness(self, val):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera): 
                device.SetSetting(CameraSetting.BRIGHTNESS, val)
                self.cameraBrightnessChanged.emit()

    cameraBrightnessChanged = Signal()
    cameraBrightness = Property(int, getCameraBrightness, setCameraBrightness, notify=cameraBrightnessChanged)


    @Slot()
    def getCameraContrast(self):  
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera):                     
                return device.GetSetting(CameraSetting.CONTRAST)
            else:
                return 0
        else:
            return 0                                            
    
    @Slot(int)
    def setCameraContrast(self, val):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera): 
                device.SetSetting(CameraSetting.CONTRAST, val)
                self.cameraContrastChanged.emit()

    cameraContrastChanged = Signal()
    cameraContrast = Property(int, getCameraContrast, setCameraContrast, notify=cameraContrastChanged)


    @Slot()
    def getCameraSaturation(self):   
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera):                     
                return device.GetSetting(CameraSetting.SATURATION)
            else:
                return 0
        else:
            return 0                                            
    
    @Slot(int)
    def setCameraSaturation(self, val):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera): 
                device.SetSetting(CameraSetting.SATURATION, val)
                self.cameraSaturationChanged.emit()

    cameraSaturationChanged = Signal()
    cameraSaturation = Property(int, getCameraSaturation, setCameraSaturation, notify=cameraSaturationChanged)


    @Slot()
    def getCameraWhiteBalance(self):  
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera):                     
                return device.GetSetting(CameraSetting.WHITE_BALANCE)
            else:
                return 0
        else:
            return 0                                           
    
    @Slot(int)
    def setCameraWhiteBalance(self, val):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera): 
                device.SetSetting(CameraSetting.WHITE_BALANCE, val)
                self.cameraWhiteBalanceChanged.emit()

    cameraWhiteBalanceChanged = Signal()
    cameraWhiteBalance = Property(int, getCameraWhiteBalance, setCameraWhiteBalance, notify=cameraWhiteBalanceChanged)


    @Slot()
    def getCameraGamma(self):  
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera):                     
                return device.GetSetting(CameraSetting.GAMMA)
            else:
                return 0
        else:
            return 0                                              
    
    @Slot(int)
    def setCameraGamma(self, val):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera): 
                device.SetSetting(CameraSetting.GAMMA, val)
                self.cameraGammaChanged.emit()

    cameraGammaChanged = Signal()
    cameraGamma = Property(int, getCameraGamma, setCameraGamma, notify=cameraGammaChanged)


    @Slot()
    def getCameraGain(self):    
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera):                     
                return device.GetSetting(CameraSetting.ISO)
            else:
                return 0
        else:
            return 0                                            
    
    @Slot(int)
    def setCameraGain(self, val):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera): 
                device.SetSetting(CameraSetting.ISO, val)
                self.cameraGainChanged.emit()

    cameraGainChanged = Signal()
    cameraGain = Property(int, getCameraGain, setCameraGain, notify=cameraGainChanged)


    @Slot()
    def getCameraSharpness(self):   
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera):                     
                return device.GetSetting(CameraSetting.SHARPNESS)
            else:
                return 0
        else:
            return 0                                                  
    
    @Slot(int)
    def setCameraSharpness(self, val):
        if not self.previewDevices.isEmpty(): 
            device = self.previewDevices.getDevice(0)
            if isinstance(device, OpencvCamera): 
                device.SetSetting(CameraSetting.SHARPNESS, val)
                self.cameraSharpnessChanged.emit()

    cameraSharpnessChanged = Signal()
    cameraSharpness = Property(int, getCameraSharpness, setCameraSharpness, notify=cameraSharpnessChanged)