import time
import logging
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
    """Class used to display the camera preview inside of the UI"""

    def __init__(self, acquisition, streamingAPI):
        """CaptureDevicePreview constructor

        Args:
            acquisition (Acquistion): reference to the Acquisition instance
            streamingAPI (StreamingAPI): Enum used to know the StreamingAPI (USBCam or OpenCV) specified in the terminal
        """
        super().__init__()
        self.streamingAPI = streamingAPI
        self.previewDevices = CaptureDeviceList() # We have to use a list for the imageProvider even if we only have one camera
        self.runningPreview = False
        self.currentId = -1
        self.applyToAllBtn = True
        self.imageProvider = ImageProvider(self.previewDevices)
        self.acquisitionInstance = acquisition # Reference to the Acquisition Object to make interaction
        self.signals = self.initSignals()

    @Slot()
    def getCurrentId(self):
        """Getter currentId: the ID of the camera currently displaying

        Returns:
            int: ID of the camera. If -1, no camera is displayed.
        """
        return self.currentId                                        
    
    @Slot(int)
    def setCurrentId(self, val):
        """Setter currentId: the ID of the camera currently displaying

        Args:
            val (int): ID of the new camera we want to display. If -1, no camera is displayed.
        """
        self.currentId = val
        self.currentIdChanged.emit()

    currentIdChanged = Signal()
    currentIdProperty = Property(int, getCurrentId, setCurrentId, notify=currentIdChanged)


    def changeApplyToAllBtnState(self, boolean):
        """Setter applyToAllBtn: the 'Apply To All' button state

        Args:
            boolean (bool): If True, enable the button. If False, disable it.
        """
        self.applyToAllBtn = boolean
        self.applyToAllBtnChanged.emit()

    @Slot(result=bool)
    def getApplyToAllBtn(self):   
        """Getter applyToAllBtn: the 'Apply To All' button state

        Returns:
            bool: If True, the button is enabled. If False, the button is disabled.
        """
        return self.applyToAllBtn                                        
    
    @Slot()
    def setApplyToAllBtn(self):
        """Apply all the settings' values diplayed on the UI to all the cameras: the already existing cameras inside of the acquisition list and also the future created cameras.
        Change also the state of the 'Apply To All' button to make it disabled.
        """
        settings = {
            "brightness" : self.getCameraSettingGeneric(CameraSetting.Brightness),
            "contrast" : self.getCameraSettingGeneric(CameraSetting.Contrast),
            "saturation" : self.getCameraSettingGeneric(CameraSetting.Saturation),
            "tempWB" : self.getCameraSettingGeneric(CameraSetting.White_Balance),
            "gamma" : self.getCameraSettingGeneric(CameraSetting.Gamma),
            "gain" : self.getCameraSettingGeneric(CameraSetting.Iso),
            "sharpness" : self.getCameraSettingGeneric(CameraSetting.Sharpness),
            "exposure" : self.getCameraSettingGeneric(CameraSetting.Exposure),
            "format" : self.previewDevices.getDevice(0).GetAcquisitionFormat()
        }
        
        self.previewDevices.applyAsDefaultSettings(settings) # Make these settings be default for next created cameras
        self.acquisitionInstance.captureDevices.applySettingsToAll(settings) # Apply these settings to every camera already inside the acquisition list

        self.changeApplyToAllBtnState(False)

    applyToAllBtnChanged = Signal()
    applyToAllBtnProperty = Property(int, getApplyToAllBtn, setApplyToAllBtn, notify=applyToAllBtnChanged)


    @Slot(result=bool)
    def getRunningPreview(self):
        """Getter runningPreview : state of the preview

        Returns:
            bool: If True, the preview is running (images are displayed). If False, the preview is stopped.
        """
        return self.runningPreview


    @Slot(str)
    def changePreview(self, camId):
        """Change the camera displayed on the preview. Also used to 'disable' the preview with the 'No Device Selected' picture.

        Args:
            camId (int): ID of the new camera we want to display. If -1, no camera is displayed.
        """
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
        existingDevice = self.acquisitionInstance.captureDevices.getDeviceByCamId(self.currentId)

        # Stop the preview for a moment
        self.runningPreview = False
        self.previewDevices.emptyDevices()

        if self.previewDevices.isEmpty() :
            if existingDevice:
                print("existing device")
                self.previewDevices.devices.append(existingDevice)
            else:
                self.previewDevices.addCamera(self.currentId, self.acquisitionInstance.savingRootDirectory)

        for sig in self.signals:
            sig.emit()
        self.runningPreview = True
        

    @Slot(result="QStringList")
    def getAvailableCameras(self):
        """Method to return the available UCV Cameras connected to the system.

        Returns:
            QStringList: List with the name/ID of each camera.
        """
        cameras = self.previewDevices.availableCameras()
        names = [cam.get("name") for cam in cameras]
        return names

    @Slot(result="QStringList")
    def getAvailableResolutions(self):
        """Method to find and return the available resolutions/formats of the current camera displayed.

        Returns:
            QStringList: List with the available resolutions/formats.
        """
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
        """Add or Remove the current camera displayed of the acquisition list."""
        if self.currentId == -1:
            return
            
        device = self.previewDevices.getDevice(0)

        if device in self.acquisitionInstance.captureDevices.devices:
            self.acquisitionInstance.captureDevices.devices.remove(device)
            print("Device removed from the Acquisition Process")
        else:
            self.acquisitionInstance.captureDevices.devices.append(device)
            print("Device added to Acquisition Process")

    @Slot(result=bool)
    def isCurrentDeviceInAcquisition(self):
        """Check if the current camera displayed is in the acquisition list or not.

        Returns:
            bool: If True, the camera is inside the acquisition list. If False, the camera is not.
        """
        if self.currentId == -1:
            return False
        else:
            return self.acquisitionInstance.captureDevices.isDeviceIn(self.currentId)

    @Slot(result="QVariantList")
    def getDevicesInAcquisition(self):
        """Method to return the name of all the cameras in the acquisition list.

        Returns:
            QVariantList: List with the name of each camera.
        """
        return self.acquisitionInstance.captureDevices.getDevicesNames()



    #----------- GETTERS & SETTERS FOR UVC CAMERAS SETTINGS
    def initSignals(self):
        """Method used to add some of the signals used by Qt in an list and return this list. Purpose: easier to emit those signals later.

        Returns:
            [Signal]: List of Signal
        """
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
        """Method to return the resolution/format of the current camera (current format displayed on the preview or the format which will be used during the acquisition).

        Args:
            mode (str, optional): The mode can take two different values: 'preview' or 'acquisition'. Default is 'preview'.

        Returns:
            str: Resolution/Format of the current camera corresponding to the mode.
        """
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
        """Method to set the resolution/format of the current camera (current format displayed on the preview or the format which will be used during the acquisition).

        Args:
            string (str): String representing the resolution/format.
            mode (str, optional): The mode can take two different values: 'preview' or 'acquisition'. Default is 'preview'.

        Returns:
            bool: If True, the set is done. If False, the set is not.
        """
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
                        self.changeApplyToAllBtnState(True)
                    break

        # Run again the preview
        self.runningPreview = True

        return True

    def getCameraSettingGeneric(self, setting):
        """Method to return the value of the setting passed in argument.

        Args:
            setting (CameraSetting): Enum representing the camera setting.

        Returns:
            int: Value of the setting.
        """
        if self.previewDevices.isEmpty():
            return 0

        device = self.previewDevices.getDevice(0)

        try:
            val = device.GetSetting(setting)
        except RuntimeError:
            logging.warning(f"The setting {setting} cannot be read. Value is 0, by default.") # TODO: Make this a better way by checking if the setting is usabled or not (and so on, enable/disable it on the UI to avoid issues)
            val = 0

        return val

    def setCameraSettingGeneric(self, setting, val):
        """Method to set the value of the setting passed in argument.

        Args:
            setting (CameraSetting): Enum representing the camera setting.
            val (int): Value to set.

        Returns:
            bool: If True, the set is done. If False, the set is not.
        """
        if self.previewDevices.isEmpty():
            return False

        device = self.previewDevices.getDevice(0)
        device.SetSetting(setting, val)

        self.changeApplyToAllBtnState(True)
        return True


    @Slot(result=str)
    def getCameraFormat(self):
        """Method to return the preview resolution/format of the current camera.

        Returns:
            str: Preview resolution/format of the current camera.
        """
        return self.getCameraFormatGeneric()

    @Slot(str)
    def setCameraFormat(self, string):
        """Method to set the preview resolution/format of the current camera.

        Args:
            string (str): String representing the preview resolution/format.
        """
        if self.setCameraFormatGeneric(string):
            self.cameraFormatChanged.emit()

    cameraFormatChanged = Signal()
    cameraFormat = Property(str, getCameraFormat, setCameraFormat, notify=cameraFormatChanged)


    @Slot(result=str)
    def getCameraAcquisitionFormat(self):
        """Method to return the acquisition resolution/format of the current camera.

        Returns:
            str: Acquisition resolution/format of the current camera.
        """
        return self.getCameraFormatGeneric(mode="acquisition")

    @Slot(str)
    def setCameraAcquisitionFormat(self, string):
        """Method to set the acquisition resolution/format of the current camera.

        Args:
            string (str): String representing the acquisition resolution/format.
        """
        if self.setCameraFormatGeneric(string, mode="acquisition"):
            self.cameraAcquisitionFormatChanged.emit()

    cameraAcquisitionFormatChanged = Signal()
    cameraAcquisitionFormat = Property(str, getCameraAcquisitionFormat, setCameraAcquisitionFormat, notify=cameraAcquisitionFormatChanged)  


    @Slot()
    def getCameraExposure(self):
        """Method to return the value of the Exposure.

        Returns:
            int: Value of the Exposure.
        """
        return self.getCameraSettingGeneric(CameraSetting.Exposure)               
    
    @Slot(int)
    def setCameraExposure(self, val):
        """Method to set the value of the Exposure.

        Args:
            val (int): Value to set.
        """
        if self.setCameraSettingGeneric(CameraSetting.Exposure, val):
            self.cameraExposureChanged.emit()

    cameraExposureChanged = Signal()
    cameraExposure = Property(int, getCameraExposure, setCameraExposure, notify=cameraExposureChanged)
    

    @Slot()
    def getCameraBrightness(self):  
        """Method to return the value of the Brightness.

        Returns:
            int: Value of the Brightness.
        """ 
        return self.getCameraSettingGeneric(CameraSetting.Brightness)                                            
    
    @Slot(int)
    def setCameraBrightness(self, val):
        """Method to set the value of the Brightness.

        Args:
            val (int): Value to set.
        """
        if self.setCameraSettingGeneric(CameraSetting.Brightness, val):
            self.cameraBrightnessChanged.emit()

    cameraBrightnessChanged = Signal()
    cameraBrightness = Property(int, getCameraBrightness, setCameraBrightness, notify=cameraBrightnessChanged)


    @Slot()
    def getCameraContrast(self):  
        """Method to return the value of the Contrast.

        Returns:
            int: Value of the Contrast.
        """ 
        return self.getCameraSettingGeneric(CameraSetting.Contrast)                                            
    
    @Slot(int)
    def setCameraContrast(self, val):
        """Method to set the value of the Contrast.

        Args:
            val (int): Value to set.
        """
        if self.setCameraSettingGeneric(CameraSetting.Contrast, val):
            self.cameraContrastChanged.emit()

    cameraContrastChanged = Signal()
    cameraContrast = Property(int, getCameraContrast, setCameraContrast, notify=cameraContrastChanged)


    @Slot()
    def getCameraSaturation(self): 
        """Method to return the value of the Saturation.

        Returns:
            int: Value of the Saturation.
        """   
        return self.getCameraSettingGeneric(CameraSetting.Saturation)                                           
    
    @Slot(int)
    def setCameraSaturation(self, val):
        """Method to set the value of the Saturation.

        Args:
            val (int): Value to set.
        """
        if self.setCameraSettingGeneric(CameraSetting.Saturation, val):
            self.cameraSaturationChanged.emit()

    cameraSaturationChanged = Signal()
    cameraSaturation = Property(int, getCameraSaturation, setCameraSaturation, notify=cameraSaturationChanged)


    @Slot()
    def getCameraWhiteBalance(self):
        """Method to return the value of the White Balance.

        Returns:
            int: Value of the White Balance.
        """   
        return self.getCameraSettingGeneric(CameraSetting.White_Balance)                                         
    
    @Slot(int)
    def setCameraWhiteBalance(self, val):
        """Method to set the value of the White Balance.

        Args:
            val (int): Value to set.
        """
        if self.setCameraSettingGeneric(CameraSetting.White_Balance, val):
            self.cameraWhiteBalanceChanged.emit()

    cameraWhiteBalanceChanged = Signal()
    cameraWhiteBalance = Property(int, getCameraWhiteBalance, setCameraWhiteBalance, notify=cameraWhiteBalanceChanged)


    @Slot()
    def getCameraGamma(self):  
        """Method to return the value of the Gamma.

        Returns:
            int: Value of the Gamma.
        """ 
        return self.getCameraSettingGeneric(CameraSetting.Gamma)                                            
    
    @Slot(int)
    def setCameraGamma(self, val):
        """Method to set the value of the Gamma.

        Args:
            val (int): Value to set.
        """
        if self.setCameraSettingGeneric(CameraSetting.Gamma, val):
            self.cameraGammaChanged.emit()

    cameraGammaChanged = Signal()
    cameraGamma = Property(int, getCameraGamma, setCameraGamma, notify=cameraGammaChanged)


    @Slot()
    def getCameraGain(self):    
        """Method to return the value of the Gain.

        Returns:
            int: Value of the Gain.
        """ 
        return self.getCameraSettingGeneric(CameraSetting.Iso)                                        
    
    @Slot(int)
    def setCameraGain(self, val):
        """Method to set the value of the Gain.

        Args:
            val (int): Value to set.
        """
        if self.setCameraSettingGeneric(CameraSetting.Iso, val):
            self.cameraGainChanged.emit()

    cameraGainChanged = Signal()
    cameraGain = Property(int, getCameraGain, setCameraGain, notify=cameraGainChanged)


    @Slot()
    def getCameraSharpness(self):  
        """Method to return the value of the Sharpness.

        Returns:
            int: Value of the Sharpness.
        """  
        return self.getCameraSettingGeneric(CameraSetting.Sharpness)                                                
    
    @Slot(int)
    def setCameraSharpness(self, val):
        """Method to set the value of the Sharpness.

        Args:
            val (int): Value to set.
        """
        if self.setCameraSettingGeneric(CameraSetting.Sharpness, val):
            self.cameraSharpnessChanged.emit()

    cameraSharpnessChanged = Signal()
    cameraSharpness = Property(int, getCameraSharpness, setCameraSharpness, notify=cameraSharpnessChanged)