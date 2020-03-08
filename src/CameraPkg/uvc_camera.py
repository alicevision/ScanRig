import numpy as np
import threading, logging, cv2


class UvcCamera(object):
    def __init__(self, indexCam, framesToSave=None, settings=None):
        self.indexCam = indexCam
        (self.status, self.frame) = (None, None)
        self.nbSavedFrame = 0
        self.framesToSave = framesToSave

        # Initialize settings for the camera
        if settings:
            self.settings = settings
        else:
            self.settings = self.initSettings()

        self.capture = cv2.VideoCapture()
        self.start()
        self.resolutions = self.findResolutions()
        print(self.resolutions)
        self.setResolution(self.resolutions[0][0], self.resolutions[0][1])
        self.setDraftResolution(self.resolutions[0][0], self.resolutions[0][1])
        self.changeResolution(draft=True)


    #----------------------------------------- SETTINGS
    def initSettings(self):
        settings = {
            "width" : 1280,
            "height" : 720,
            "draftWidth" : 1280,
            "draftHeight" : 720,
            "brightness" : 0,
            "contrast" : 0,
            "saturation" : 32,
            "tempWB" : 4500, # From 0 to 10 000
            "autoWB" : 0,
            "gamma" : 220,
            "gain" : 0, # From 0 to 100
            "sharpness" : 0,
            "exposure" : 500, # From 0 to 10 000
            "autoExposure" : 1
        }
        return settings

    def findResolutions(self):
        resolutions = []
        toTest = [(4208, 3120), (4096, 2160), (3840, 2160), (2880, 2160), (1920, 1440), (1920, 1080), (1280, 960), (1280, 720), (640,480)]

        for (w,h) in toTest:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

            actualWidth = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            actualHeight = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

            if actualWidth == w and actualHeight == h:
                resolutions.append((w,h))

        return resolutions

    def setResolution(self, w, h):
        self.settings["width"] = w
        self.settings["height"] = h
        return

    def getResolution(self):
        return (self.settings["width"], self.settings["height"])

    def setDraftResolution(self, w, h):
        self.settings["draftWidth"] = w
        self.settings["draftHeight"] = h    
        return

    def getDraftResolution(self):
        return (self.settings["draftWidth"], self.settings["draftHeight"])


    def changeResolution(self, draft=False):
        if draft:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.get("draftWidth"))
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.get("draftHeight"))
        else:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.get("width"))
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.get("height"))
        
        self.fillBuffer()
        self.retrieveFrame()
        return


    def setBrightness(self, value):
        self.settings["brightness"] = value
        self.capture.set(cv2.CAP_PROP_BRIGHTNESS, self.settings.get("brightness"))
        return

    def setContrast(self, value):
        self.settings["contrast"] = value
        self.capture.set(cv2.CAP_PROP_CONTRAST, self.settings.get("contrast"))
        return
    
    def setSaturation(self, value):
        self.settings["saturation"] = value
        self.capture.set(cv2.CAP_PROP_SATURATION, self.settings.get("saturation"))
        return

    def setTempWB(self, value):
        self.settings["tempWB"] = value
        self.capture.set(cv2.CAP_PROP_WB_TEMPERATURE, self.settings.get("tempWB"))
        return

    def setGamma(self, value):
        self.settings["gamma"] = value
        self.capture.set(cv2.CAP_PROP_GAMMA, self.settings.get("gamma"))
        return

    def setGain(self, value):
        self.settings["gain"] = value
        self.capture.set(cv2.CAP_PROP_GAIN, self.settings.get("gain"))
        return

    def setSharpness(self, value):
        self.settings["sharpness"] = value
        self.capture.set(cv2.CAP_PROP_SHARPNESS, self.settings.get("sharpness"))
        return

    def setExposure(self, value):
        self.settings["exposure"] = value
        self.capture.set(cv2.CAP_PROP_EXPOSURE, self.settings.get("exposure"))
        return

    # Set everything but the Draft Resolution (of course)
    def setAllSettings(self):
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.get("width"))
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.get("height"))
        self.capture.set(cv2.CAP_PROP_BRIGHTNESS, self.settings.get("brightness"))
        self.capture.set(cv2.CAP_PROP_CONTRAST, self.settings.get("contrast"))
        self.capture.set(cv2.CAP_PROP_SATURATION, self.settings.get("saturation"))
        self.capture.set(cv2.CAP_PROP_WB_TEMPERATURE, self.settings.get("tempWB")) 
        self.capture.set(cv2.CAP_PROP_AUTO_WB, self.settings.get("autoWB"))
        self.capture.set(cv2.CAP_PROP_GAMMA, self.settings.get("gamma"))
        self.capture.set(cv2.CAP_PROP_GAIN, self.settings.get("gain")) 
        self.capture.set(cv2.CAP_PROP_SHARPNESS, self.settings.get("sharpness"))
        self.capture.set(cv2.CAP_PROP_EXPOSURE, self.settings.get("exposure")) 
        self.capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, self.settings.get("autoExposure"))

        self.fillBuffer()
        self.retrieveFrame()

        return

    #----------------------------------------- CAMERA FUNCTIONS
    def start(self):
        if not self.capture.isOpened():
            v = self.capture.open(self.indexCam, apiPreference=cv2.CAP_V4L2)
            if v:
                self.fillBuffer()
                self.retrieveFrame()
                self.setAllSettings()

            else:
                logging.warning("Skip invalid stream ID {}".format(self.indexCam))
                self.stop()


    def fillBuffer(self):
        for i in range(int(self.capture.get(cv2.CAP_PROP_BUFFERSIZE)) + 1):
            self.grabFrame()

    def grabFrame(self):
        # print("image grabbed")
        ret = self.capture.grab()
        if not ret:
            logging.warning("Image cannot be grabbed")

    def retrieveFrame(self):
        self.status, self.frame = self.capture.retrieve()
        if not self.status:
            logging.warning("Image cannot be retrieved")

    def saveFrame(self):
        if self.framesToSave:
            self.framesToSave.put((self.indexCam, self.nbSavedFrame, self.frame))
            self.nbSavedFrame += 1

    def stop(self):
        self.capture.release()
        if not self.capture.isOpened():
            print(f"Device n°{self.indexCam} closed")