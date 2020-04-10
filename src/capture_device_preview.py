import time
from PySide2 import QtWidgets
from PySide2.QtCore import QObject, Slot, Property, Signal

from UIPkg.image_provider import ImageProvider
from CameraPkg.capture_device_list import CaptureDeviceList
from CameraPkg.streaming_api import StreamingAPI, CHOSEN_STREAMING_API

if CHOSEN_STREAMING_API == StreamingAPI.OPENCV:
    from CameraPkg.opencv_camera import OpencvCamera
    from CameraPkg.i_uvc_camera import CameraSetting as CameraSetting
elif CHOSEN_STREAMING_API == StreamingAPI.USBCAM:
    import usbcam
    from usbcam import CameraSetting as CameraSetting


# ONLY ONE CAMERA IN PREVIEW AT A TIME
class CaptureDevicePreview(QObject):
    def __init__(self, acquisitionDevices, acquisitionSavingRootDirectory, streamingAPI):
        super().__init__()
        self.streamingAPI = streamingAPI
        self.previewDevices = CaptureDeviceList() # We have to use a list for the imageProvider even if we only have one camera
        self.runningPreview = False
        self.currentId = -1
        self.imageProvider = ImageProvider(self.previewDevices)
        self.acquisitionDevices = acquisitionDevices # Reference to the acquisition devices list
        self.acquisitionSavingRootDirectory = acquisitionSavingRootDirectory # Reference to the acquisition saving directory
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
                self.previewDevices.addCamera(self.currentId, self.acquisitionSavingRootDirectory)

        for sig in self.signals:
            sig.emit()
        self.runningPreview = True
        

    @Slot(result="QStringList")
    def getAvailableCameras(self):
        cameras = self.previewDevices.availableCameras()
        names = [cam.get("name") for cam in cameras]
        return names

    @Slot(result="QStringList")
    def getAvailableResolutions(self):
        if not self.previewDevices.isEmpty():   
            device = self.previewDevices.getDevice(0)

            if CHOSEN_STREAMING_API == StreamingAPI.OPENCV:
                printableResolutions = []

                for elt in device.formats:
                    txt = f'{elt["width"]}x{elt["height"]}'
                    printableResolutions.append(txt)

                return printableResolutions

            if CHOSEN_STREAMING_API == StreamingAPI.USBCAM:
                printableResolutions = []
                formats = device.GetSupportedFormats()

                for elt in formats:
                    txt = f'{elt.width}x{elt.height} | {elt.encoding.name}'
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

    def getCameraFormatGeneric(self, mode="preview"):
        if self.previewDevices.isEmpty():
            return ""

        device = self.previewDevices.getDevice(0)

        if mode == "preview":
            res = device.GetFormat()
        elif mode == "acquisition":
            res = device.GetAcquisitionFormat()
        else:
            return ""

        if CHOSEN_STREAMING_API == StreamingAPI.OPENCV:
            return f'{res["width"]}x{res["height"]}'
        elif CHOSEN_STREAMING_API == StreamingAPI.USBCAM:
            return f'{res.width}x{res.height} | {res.encoding.name}'        
        else:
            return ""

    def setCameraFormatGeneric(self, string, mode="preview"):
        if self.previewDevices.isEmpty():
            return False

        device = self.previewDevices.getDevice(0)

        # Stop the preview
        self.runningPreview = False
        time.sleep(0.1)

        if CHOSEN_STREAMING_API == StreamingAPI.OPENCV:
            # Get resolution from string
            res = string.split("x")
            w = int(res[0])
            h = int(res[1])
            # Set resolution
            if mode == "preview":
                device.SetFormat({"width":w, "height":h})
            elif mode == "acquisition":
                device.SetAcquisitionFormat({"width":w, "height":h})

        if CHOSEN_STREAMING_API == StreamingAPI.USBCAM:
            # Get format from string
            txt = string.split(" | ")
            res = txt[0]
            encoding = txt[1]

            splitRes = res.split("x")
            w = int(splitRes[0])
            h = int(splitRes[1])

            # # Set format
            allFormats = device.GetSupportedFormats()
            for f in allFormats:
                if f.width == w and f.height == h and f.encoding.name == encoding:
                    if mode == "preview":   
                        device.SetFormat(f)
                    elif mode == "acquisition":
                        device.SetAcquisitionFormat(f)
                    break

        # Run again the preview
        self.runningPreview = True

        return True

    def getCameraSettingGeneric(self, setting):
        if self.previewDevices.isEmpty():
            return 0

        device = self.previewDevices.getDevice(0)   
        return device.GetSetting(setting)

    def setCameraSettingGeneric(self, setting, val):
        if self.previewDevices.isEmpty():
            return False

        device = self.previewDevices.getDevice(0)
        device.SetSetting(setting, val)
        return True


    @Slot(result=str)
    def getCameraFormat(self):
        return self.getCameraFormatGeneric()

    @Slot(str)
    def setCameraFormat(self, string):
        if self.setCameraFormatGeneric(string):
            self.cameraFormatChanged.emit()

    cameraFormatChanged = Signal()
    cameraFormat = Property(str, getCameraFormat, setCameraFormat, notify=cameraFormatChanged)


    @Slot(result=str)
    def getCameraAcquisitionFormat(self):
        return self.getCameraFormatGeneric(mode="acquisition")

    @Slot(str)
    def setCameraAcquisitionFormat(self, string):
        if self.setCameraFormatGeneric(string, mode="acquisition"):
            self.cameraAcquisitionFormatChanged.emit()

    cameraAcquisitionFormatChanged = Signal()
    cameraAcquisitionFormat = Property(str, getCameraAcquisitionFormat, setCameraAcquisitionFormat, notify=cameraAcquisitionFormatChanged)  


    @Slot()
    def getCameraExposure(self):
        return self.getCameraSettingGeneric(CameraSetting.Exposure)               
    
    @Slot(int)
    def setCameraExposure(self, val):
        if self.setCameraSettingGeneric(CameraSetting.Exposure, val):
            self.cameraExposureChanged.emit()

    cameraExposureChanged = Signal()
    cameraExposure = Property(int, getCameraExposure, setCameraExposure, notify=cameraExposureChanged)
    

    @Slot()
    def getCameraBrightness(self):   
        return self.getCameraSettingGeneric(CameraSetting.Brightness)                                            
    
    @Slot(int)
    def setCameraBrightness(self, val):
        if self.setCameraSettingGeneric(CameraSetting.Brightness, val):
            self.cameraBrightnessChanged.emit()

    cameraBrightnessChanged = Signal()
    cameraBrightness = Property(int, getCameraBrightness, setCameraBrightness, notify=cameraBrightnessChanged)


    @Slot()
    def getCameraContrast(self):  
        return self.getCameraSettingGeneric(CameraSetting.Contrast)                                            
    
    @Slot(int)
    def setCameraContrast(self, val):
        if self.setCameraSettingGeneric(CameraSetting.Contrast, val):
            self.cameraContrastChanged.emit()

    cameraContrastChanged = Signal()
    cameraContrast = Property(int, getCameraContrast, setCameraContrast, notify=cameraContrastChanged)


    @Slot()
    def getCameraSaturation(self):   
        return self.getCameraSettingGeneric(CameraSetting.Saturation)                                           
    
    @Slot(int)
    def setCameraSaturation(self, val):
        if self.setCameraSettingGeneric(CameraSetting.Saturation, val):
            self.cameraSaturationChanged.emit()

    cameraSaturationChanged = Signal()
    cameraSaturation = Property(int, getCameraSaturation, setCameraSaturation, notify=cameraSaturationChanged)


    @Slot()
    def getCameraWhiteBalance(self):  
        return self.getCameraSettingGeneric(CameraSetting.White_Balance)                                         
    
    @Slot(int)
    def setCameraWhiteBalance(self, val):
        if self.setCameraSettingGeneric(CameraSetting.White_Balance, val):
            self.cameraWhiteBalanceChanged.emit()

    cameraWhiteBalanceChanged = Signal()
    cameraWhiteBalance = Property(int, getCameraWhiteBalance, setCameraWhiteBalance, notify=cameraWhiteBalanceChanged)


    @Slot()
    def getCameraGamma(self):  
        return self.getCameraSettingGeneric(CameraSetting.Gamma)                                            
    
    @Slot(int)
    def setCameraGamma(self, val):
        if self.setCameraSettingGeneric(CameraSetting.Gamma, val):
            self.cameraGammaChanged.emit()

    cameraGammaChanged = Signal()
    cameraGamma = Property(int, getCameraGamma, setCameraGamma, notify=cameraGammaChanged)


    @Slot()
    def getCameraGain(self):    
        return self.getCameraSettingGeneric(CameraSetting.Iso)                                        
    
    @Slot(int)
    def setCameraGain(self, val):
        if self.setCameraSettingGeneric(CameraSetting.Iso, val):
            self.cameraGainChanged.emit()

    cameraGainChanged = Signal()
    cameraGain = Property(int, getCameraGain, setCameraGain, notify=cameraGainChanged)


    @Slot()
    def getCameraSharpness(self):   
        return self.getCameraSettingGeneric(CameraSetting.Sharpness)                                                
    
    @Slot(int)
    def setCameraSharpness(self, val):
        if self.setCameraSettingGeneric(CameraSetting.Sharpness, val):
            self.cameraSharpnessChanged.emit()

    cameraSharpnessChanged = Signal()
    cameraSharpness = Property(int, getCameraSharpness, setCameraSharpness, notify=cameraSharpnessChanged)