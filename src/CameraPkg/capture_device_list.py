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
    """Class used to store and control several cameras."""
    def __init__(self):
        """CaptureDeviceList constructor"""
        self.devices = []
        self.defaultSettings =  None

        if CHOSEN_STREAMING_API == StreamingAPI.OPENCV:
            self.savingQueue = queue.Queue()

    #----------------------------------------- DEVICES
    def isEmpty(self):
        """Method to check if the list is empty or not.

        Returns:
            bool: If True, the list is empty. If False, the list is not empty.
        """
        if self.devices:
            return False
        else:
            return True

    def isDeviceIn(self, camId):
        """Method to check if the reference of a camera is stored in the list or not.

        Args:
            camId (int): ID of the camera.

        Returns:
            bool: If True, the list contains the camera. If False, the list does not.
        """
        if self.getDeviceByCamId(camId):
            return True
        else:
            return False

    def getDevicesNames(self):
        """Method to return a list of the storred camera names.

        Returns:
            [str]: List with all the storred camera names.
        """
        names = []
        for device in self.devices:
            name = device.GetCameraName()

            if CHOSEN_STREAMING_API == StreamingAPI.USBCAM:
                name += " | UVC: " + str(device.GetCameraId())

            names.append(name)
        return names


    def availableCameras(self):
        """Method to return a list of the available cameras connected to the system.

        Returns:
            [str]: List with all the available cameras on the system.
        """
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
        """Method to add a new camera inside of the list.

        Args:
            idDevice (int): ID of the camera.
            path (str, optional): Path used to store the images taken by this camera. Default is "".
        """
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
        """Method to return the reference of a camera storred in the list using a list index (and not the Camera ID).

        Args:
            index (int): Index used to return the camera.

        Returns:
            UvcCamera: Camera reference corresponding to the index list.
        """
        return self.devices[index]

    def getDeviceByCamId(self, id):
        """Method to return the reference of a camera storred in the list using its camera ID.

        Args:
            id (int): ID of the camera.

        Returns:
            UvcCamera: Reference to the UvcCamera. If not found, returns None.
        """
        for device in self.devices:
            if id == device.GetCameraId():
                return device
        return None

    def readFrames(self):
        """Method to make all the cameras read a frame."""
        for device in self.devices:
            frame = device.GetLastFrame()

    def saveFrames(self):
        """Method to make all the cameras save a frame."""
        for device in self.devices:
            device.SaveLastFrame()

    def setSavingToCameras(self, rootDirectory):
        """Method to tell each camera a new saving directory path.

        Args:
            rootDirectory (str): Path to the root directory where we want to save pictures.
        """
        for device in self.devices:
            if CHOSEN_STREAMING_API == StreamingAPI.OPENCV and isinstance(device, OpencvCamera):
                device.SetSavingQueue(self.savingQueue)
            device.SetSaveDirectory(rootDirectory)

    def emptyDevices(self):
        """Method to remove all the cameras of the list."""
        for device in self.devices:
            self.devices.remove(device)

    def applySettingsToAll(self, settings):
        """Method to make all the cameras adopt the settings.

        Args:
            settings (Object): Object describing all the settings.
        """
        for device in self.devices:
            self.applySettingsToOneDevice(device, settings)

    def applyAsDefaultSettings(self, settings):
        """Method to make the settings Object passed in argument as the default settings Object of the instance.

        Args:
            settings (Object): Object describing all the settings.
        """
        self.defaultSettings = settings

    def applySettingsToOneDevice(self, device, settings):
        """Method to make one particular device adopt the settings.

        Args:
            device (UvcCamera): Reference to a camera.
            settings (Object): Object describing all the settings.
        """
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