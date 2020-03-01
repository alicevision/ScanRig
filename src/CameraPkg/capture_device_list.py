import cv2, logging
import queue, os

from .uvc_camera import UvcCamera
from .dslr_camera import DslrCamera

class CaptureDeviceList(object):
    def __init__(self):
        self.devices = []
        self.savingFrames = queue.Queue()

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
            if isinstance(device, UvcCamera):
                name = "UVC : " + str(device.indexCam)
                names.append(name)
        return names


    def availableUvcCameras(self):
        ids = []
        for id in range(20):
            if os.path.exists('/dev/video' + str(id)):
                ids.append(id)

        return ids

    def addUvcCamera(self, indexDevice):
        device = UvcCamera(indexDevice, self.savingFrames)
        if device.capture.isOpened():
            self.devices.append(device)
        return

    def getDevice(self, indexDevice):
        return self.devices[indexDevice]

    def getDeviceByCamId(self, camId):
        for device in self.devices:
            if camId == device.indexCam:
                return device
        return None

    def grabFrames(self):
        for device in self.devices:
            if isinstance(device, UvcCamera):
                device.grabFrame()

    def retrieveFrames(self):
        for device in self.devices:
            if isinstance(device, UvcCamera):
                device.retrieveFrame()

    def saveFrames(self):
        for device in self.devices:
            if isinstance(device, UvcCamera):
                device.saveFrame()

    def stopDevices(self):
        for device in self.devices:
            if isinstance(device, UvcCamera):
                device.stop()

    def emptyDevices(self):
        for device in self.devices:
            self.devices.remove(device)
