import cv2, logging
import queue, os

from . import capture_device

class CaptureDeviceList(object):
    def __init__(self, settings=None):
        self.devices = []
        self.savingFrames = queue.Queue()

        if settings:
            self.settings = settings
        else:
            self.settings = self.initSettings()

    #----------------------------------------- GLOBAL SETTINGS
    def initSettings(self):
        settings = {
            "width" : 1280,
            "height" : 720,
            "brightness" : 0,
            "contrast" : 0,
            "saturation" : 32,
            "tempWB" : 4500, # From 0 to 10 000
            "autoWB" : 0,
            "gamma" : 220,
            "gain" : 0, # From 0 to 100
            "sharpness" : 0,
            "exposure" : 2000, # From 0 to 10 000
            "autoExposure" : 1,
            "bufferSize" : 1
        }
        return settings

    def setResolution(self, w, h):
        self.settings["width"] = w
        self.settings["height"] = h
        for device in self.devices:
            device.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.get("width"))
            device.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.get("height"))
        return

    def setBrightness(self, value):
        self.settings["brightness"] = value
        for device in self.devices:
            device.capture.set(cv2.CAP_PROP_BRIGHTNESS, self.settings.get("brightness"))
        return

    def setContrast(self, value):
        self.settings["contrast"] = value
        for device in self.devices:
            device.capture.set(cv2.CAP_PROP_CONTRAST, self.settings.get("contrast"))
        return
    
    def setSaturation(self, value):
        self.settings["saturation"] = value
        for device in self.devices:
            device.capture.set(cv2.CAP_PROP_SATURATION, self.settings.get("saturation"))
        return

    def setTempWB(self, value):
        self.settings["tempWB"] = value
        for device in self.devices:
            device.capture.set(cv2.CAP_PROP_WB_TEMPERATURE, self.settings.get("tempWB"))
        return

    def setGamma(self, value):
        self.settings["gamma"] = value
        for device in self.devices:
            device.capture.set(cv2.CAP_PROP_GAMMA, self.settings.get("gamma"))
        return

    def setGain(self, value):
        self.settings["gain"] = value
        for device in self.devices:
            device.capture.set(cv2.CAP_PROP_GAIN, self.settings.get("gain"))
        return

    def setSharpness(self, value):
        self.settings["sharpness"] = value
        for device in self.devices:
            device.capture.set(cv2.CAP_PROP_SHARPNESS, self.settings.get("sharpness"))
        return

    def setExposure(self, value):
        self.settings["exposure"] = value
        for device in self.devices:
            device.capture.set(cv2.CAP_PROP_EXPOSURE, self.settings.get("exposure"))
        return

    def setAllAttributesToDevices(self):
        for device in self.devices:
            # device.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('U','Y','V','Y')) # To use only with the FSCAM_CU135
            # device.capture.set(cv2.CAP_PROP_CONVERT_RGB, False) # To use only with the FSCAM_CU135
            # device.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            device.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.get("width"))
            device.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.get("height"))
            device.capture.set(cv2.CAP_PROP_BRIGHTNESS, self.settings.get("brightness"))
            device.capture.set(cv2.CAP_PROP_CONTRAST, self.settings.get("contrast"))
            device.capture.set(cv2.CAP_PROP_SATURATION, self.settings.get("saturation"))
            device.capture.set(cv2.CAP_PROP_WB_TEMPERATURE, self.settings.get("tempWB")) 
            device.capture.set(cv2.CAP_PROP_AUTO_WB, self.settings.get("autoWB"))
            device.capture.set(cv2.CAP_PROP_GAMMA, self.settings.get("gamma"))
            device.capture.set(cv2.CAP_PROP_GAIN, self.settings.get("gain")) 
            device.capture.set(cv2.CAP_PROP_SHARPNESS, self.settings.get("sharpness"))
            device.capture.set(cv2.CAP_PROP_EXPOSURE, self.settings.get("exposure")) 
            device.capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, self.settings.get("autoExposure"))
        return

    #----------------------------------------- DEVICES
    def isEmpty(self):
        if self.devices:
            return False
        else:
            return True

    def addDevice(self, indexDevice):
        device = capture_device.CaptureDevice(indexDevice, self.savingFrames)
        if device.capture.isOpened():
            self.devices.append(device)
        return

    def getDevice(self, indexDevice):
        return self.devices[indexDevice]

    def listAvailableDevices(self):
        ids = []
        ids.append("No device selected")
        for id in range(20):
            if os.path.exists('/dev/video' + str(id)):
                ids.append(id)

        return ids

    def grabFrames(self):
        for device in self.devices:
            device.grabFrame()

    def retrieveFrames(self):
        for device in self.devices:
            device.retrieveFrame()

    def saveFrames(self):
        for device in self.devices:
            device.saveFrame()

    def stopDevices(self):
        for device in self.devices:
            device.stop()
            self.devices.remove(device)
