import cv2, logging
import queue, os

from .streaming_api import CHOSEN_STREAMING_API, StreamingAPI

if CHOSEN_STREAMING_API == StreamingAPI.OPENCV:
    from CameraPkg.opencv_camera import OpencvCamera
    from CameraPkg.i_uvc_camera import CameraSetting as CameraSetting
elif CHOSEN_STREAMING_API == StreamingAPI.USBCAM:
    import usbcam
    from usbcam import CameraSetting as CameraSetting

class CaptureDeviceList(object):
    def __init__(self):
        self.devices = []
        self.defaultSettings =  None

        if CHOSEN_STREAMING_API == StreamingAPI.OPENCV:
            self.savingQueue = queue.Queue()

    #----------------------------------------- DEVICES
    def isEmpty(self):
        if self.devices:
            return False
        else:
            return True

    def isDeviceIn(self, camId):
        if self.getDeviceByCamId(camId):
            return True
        else:
            return False

    def getDevicesNames(self):
        names = []
        for device in self.devices:
            name = device.GetCameraName()

            if CHOSEN_STREAMING_API == StreamingAPI.USBCAM:
                name += " | UVC: " + str(device.GetCameraId())

            names.append(name)
        return names


    def availableCameras(self):
        cameras = []
        if CHOSEN_STREAMING_API == StreamingAPI.OPENCV:
            for id in range(20):
                if os.path.exists('/dev/video' + str(id)):
                    cameras.append({ "name": "UVC: " + str(id), "id": id })
        
        elif CHOSEN_STREAMING_API == StreamingAPI.USBCAM:
            devicesList = usbcam.GetDevicesList()
            for device in devicesList:
                cameras.append({ "name": device.name + " | UVC: " + str(device.number), "id": device.number })
        
        return cameras

    def addCamera(self, idDevice, path=""):
        if not path:
            projectDir = os.path.dirname(os.path.dirname(__file__))
            path = os.path.join(projectDir, "capture")
            os.makedirs(path, exist_ok=True)

        if CHOSEN_STREAMING_API == StreamingAPI.OPENCV:
            device = OpencvCamera(idDevice, path)
            if device.capture.isOpened():
                self.devices.append(device)
        
        elif CHOSEN_STREAMING_API == StreamingAPI.USBCAM:
            device = usbcam.CreateCamera(idDevice, path)

            device.SetAcquisitionFormat(device.GetFormat()) 
            self.devices.append(device)
        
        if self.defaultSettings:
            self.applySettingsToOneDevice(self.devices[-1], self.defaultSettings) # Apply default settings to the camera recently created

        return

    def getDevice(self, index):
        return self.devices[index]

    def getDeviceByCamId(self, id):
        for device in self.devices:
            if id == device.GetCameraId():
                return device
        return None

    def readFrames(self):
        for device in self.devices:
            frame = device.GetLastFrame()

    def saveFrames(self):
        for device in self.devices:
            device.SaveLastFrame()

    def setSavingToCameras(self, rootDirectory):
        for device in self.devices:
            if CHOSEN_STREAMING_API == StreamingAPI.OPENCV and isinstance(device, OpencvCamera):
                device.SetSavingQueue(self.savingQueue)
            device.SetSaveDirectory(rootDirectory)

    def emptyDevices(self):
        for device in self.devices:
            self.devices.remove(device)

    def applySettingsToAll(self, settings):
        for device in self.devices:
            self.applySettingsToOneDevice(device, settings)

    def applyAsDefaultSettings(self, settings):
        self.defaultSettings = settings

    def applySettingsToOneDevice(self, device, settings):
        device.SetSetting(CameraSetting.Brightness, settings.get("brightness"))
        device.SetSetting(CameraSetting.Contrast, settings.get("contrast"))
        device.SetSetting(CameraSetting.Saturation, settings.get("saturation"))
        device.SetSetting(CameraSetting.White_Balance, settings.get("tempWB"))
        device.SetSetting(CameraSetting.Gamma, settings.get("gamma"))
        device.SetSetting(CameraSetting.Iso, settings.get("gain"))
        device.SetSetting(CameraSetting.Sharpness, settings.get("sharpness"))
        device.SetSetting(CameraSetting.Exposure, settings.get("exposure"))
        device.SetFormat(settings.get("format"))
        device.SetAcquisitionFormat(settings.get("format"))