import cv2, logging
import queue, os

from .streaming_api import CHOSEN_STREAMING_API, StreamingAPI

if CHOSEN_STREAMING_API == StreamingAPI.OPENCV:
    from .opencv_camera import OpencvCamera
elif CHOSEN_STREAMING_API == StreamingAPI.USBCAM:
    import usbcam

class CaptureDeviceList(object):
    def __init__(self):
        self.devices = []

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
            device = OpencvCamera(idDevice, path, settings=None)
            if device.capture.isOpened():
                self.devices.append(device)
        
        elif CHOSEN_STREAMING_API == StreamingAPI.USBCAM:
            device = usbcam.CreateCamera(idDevice, path)

            device.SetAcquisitionFormat(device.GetFormat()) 
            self.devices.append(device)
        
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
