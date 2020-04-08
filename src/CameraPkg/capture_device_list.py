import cv2, logging
import queue, os

from .opencv_camera import OpencvCamera
from .dslr_camera import DslrCamera

class CaptureDeviceList(object):
    def __init__(self):
        self.devices = []
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
            if isinstance(device, OpencvCamera):
                name = "UVC : " + str(device.id)
                names.append(name)
        return names


    def availableOpencvCameras(self):
        ids = []
        for id in range(20):
            if os.path.exists('/dev/video' + str(id)):
                ids.append(id)

        return ids

    def addOpencvCamera(self, idDevice):
        device = OpencvCamera(idDevice, settings=None)
        if device.capture.isOpened():
            self.devices.append(device)
        return

    def getDevice(self, index):
        return self.devices[index]

    def getDeviceByCamId(self, id):
        for device in self.devices:
            if id == device.id:
                return device
        return None

    def readFrames(self):
        for device in self.devices:
            if isinstance(device, OpencvCamera):
                frame = device.getLastFrame()

    def saveFrames(self):
        for device in self.devices:
            if isinstance(device, OpencvCamera):
                device.saveLastFrame()

    # ONLY FOR OPENCV API
    def setSavingToOpencvCameras(self, rootDirectory):
        for device in self.devices:
            if isinstance(device, OpencvCamera):
                device.setSavingQueue(self.savingQueue)
                device.setSaveDirectory(rootDirectory)

    def emptyDevices(self):
        for device in self.devices:
            self.devices.remove(device)
