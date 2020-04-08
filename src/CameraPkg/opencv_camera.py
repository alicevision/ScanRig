import numpy as np
import os
import threading, logging, cv2
from .i_uvc_camera import CameraSetting, IUvcCamera

'''
class OpencvCamera(object):
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

        return

    #----------------------------------------- CAMERA FUNCTIONS
    def start(self):
        if not self.capture.isOpened():
            v = self.capture.open(self.indexCam, apiPreference=cv2.CAP_V4L2)
            if v:
                self.fillBuffer()
                self.setAllSettings()

            else:
                logging.warning("Skip invalid stream ID {}".format(self.indexCam))
                self.stop()


    def fillBuffer(self):
        for i in range(int(self.capture.get(cv2.CAP_PROP_BUFFERSIZE)) + 1):
            self.readFrame()

    def readFrame(self):
        self.status, self.frame = self.capture.read()
        if not self.status:
            logging.warning("Image cannot be read")

    def setSavingFrames(self, savingFrames):
        self.framesToSave = savingFrames

    def saveFrame(self):
        if self.framesToSave:
            self.framesToSave.put((self.indexCam, self.nbSavedFrame, self.frame))
            self.nbSavedFrame += 1

    def stop(self):
        self.capture.release()
        if not self.capture.isOpened():
            print(f"Device n°{self.indexCam} closed")

'''


class OpencvCamera(IUvcCamera):
    def __init__(self, id, settings=None, saveDirectory=None):
        self.id = id
        (self.status, self.frame) = (None, None)
        self.frameCount = 0

        # Initialize settings for the camera
        if settings:
            self.settings = settings
        else:
            self.settings = self.__initSettings()

        self.capture = cv2.VideoCapture()
        self.__start()
        self.formats = self.getSupportedFormats()
        print(self.formats)
        self.setFormat(self.formats[0])
        self.acquisitionFormat = self.formats[0]

        self.saveDirectory = saveDirectory

    
    def __del__(self):
        self.__stop()
        print(f"Camera {self.id} is self-desctructed")



    def getCameraId(self):
        """Returns the camera ID"""
        return self.id

    def getSupportedFormats(self):
        """Returns the available formats for this device"""
        formats = []
        toTest = [(4208, 3120), (4096, 2160), (3840, 2160), (2880, 2160), (1920, 1440), (1920, 1080), (1280, 960), (1280, 720), (640,480)]

        for (w,h) in toTest:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

            actualWidth = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            actualHeight = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

            if actualWidth == w and actualHeight == h:
                formats.append({"width": w, "height": h})

        return formats

    def setFormat(self, format):
        """Set current width & height"""
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, format.get("width"))
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, format.get("height"))
        
        self.__fillBuffer()

    def getFormat(self):
        """Returns the current capability used"""
        w = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

        return {"width": int(w), "height": int(h)}

    def setAcquisitionFormat(self, format):
        """Set the Acquisition width & height"""
        self.acquisitionFormat = format

    def getAcquisitionFormat(self):
        """Returns the Acquisition format"""
        return self.acquisitionFormat

    def getSupportedSettings(self):
        """Does nothing"""
        pass

    def setSetting(self, setting, value):
        """Set a specific setting"""
        if setting == CameraSetting.BRIGHTNESS:
            self.capture.set(cv2.CAP_PROP_BRIGHTNESS, value)
        elif setting == CameraSetting.CONTRAST:
            self.capture.set(cv2.CAP_PROP_CONTRAST, value)
        elif setting == CameraSetting.SATURATION:
            self.capture.set(cv2.CAP_PROP_SATURATION, value)
        elif setting == CameraSetting.WHITE_BALANCE:
            self.capture.set(cv2.CAP_PROP_WB_TEMPERATURE, value)
        elif setting == CameraSetting.AUTO_WHITE_BALANCE:
            self.capture.set(cv2.CAP_PROP_AUTO_WB, value)
        elif setting == CameraSetting.GAMMA:
            self.capture.set(cv2.CAP_PROP_GAMMA, value)
        elif setting == CameraSetting.ISO:
            self.capture.set(cv2.CAP_PROP_GAIN, value)
        elif setting == CameraSetting.SHARPNESS:
            self.capture.set(cv2.CAP_PROP_SHARPNESS, value)
        elif setting == CameraSetting.EXPOSURE:
            self.capture.set(cv2.CAP_PROP_EXPOSURE, value)
        elif setting == CameraSetting.AUTO_EXPOSURE:
            self.capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, value)

    def getSetting(self, setting):
        """Returns the value of a specific setting"""
        if setting == CameraSetting.BRIGHTNESS:
            return self.capture.get(cv2.CAP_PROP_BRIGHTNESS)
        elif setting == CameraSetting.CONTRAST:
            return self.capture.get(cv2.CAP_PROP_CONTRAST)
        elif setting == CameraSetting.SATURATION:
            return self.capture.get(cv2.CAP_PROP_SATURATION)
        elif setting == CameraSetting.WHITE_BALANCE:
            return self.capture.get(cv2.CAP_PROP_WB_TEMPERATURE)
        elif setting == CameraSetting.AUTO_WHITE_BALANCE:
            return self.capture.get(cv2.CAP_PROP_AUTO_WB)
        elif setting == CameraSetting.GAMMA:
            return self.capture.get(cv2.CAP_PROP_GAMMA)
        elif setting == CameraSetting.ISO:
            return self.capture.get(cv2.CAP_PROP_GAIN)
        elif setting == CameraSetting.SHARPNESS:
            return self.capture.get(cv2.CAP_PROP_SHARPNESS)
        elif setting == CameraSetting.EXPOSURE:
            return self.capture.get(cv2.CAP_PROP_EXPOSURE)
        elif setting == CameraSetting.AUTO_EXPOSURE:
            return self.capture.get(cv2.CAP_PROP_AUTO_EXPOSURE)

    def setSaveDirectory(self, path):
        """Set the saving directory"""
        self.saveDirectory = path

    def saveLastFrame(self):
        """Save the frame into the specified directory"""
        frame = self.frame
        filename = f'cam_{self.id}_{self.frameCount:04d}.jpg'
        outFilepath = os.path.join(self.saveDirectory, filename)
        logging.info(f'Writting file={outFilepath}')
        cv2.imwrite(outFilepath, frame)
        self.frameCount += 1

    def getLastFrame(self):
        """Returns the last frame taken"""
        self.status, self.frame = self.capture.read()
        if not self.status:
            logging.warning("Image cannot be read")
        
        return self.frame

#---------- PRIVATE METHODS

    def __start(self):
        if not self.capture.isOpened():
            v = self.capture.open(self.id, apiPreference=cv2.CAP_V4L2)
            if v:
                self.__fillBuffer()
                self.__setAllSettings()

            else:
                logging.warning(f"Skip invalid stream ID {self.id}")
                self.__stop()

    def __stop(self):
        self.capture.release()
        if not self.capture.isOpened():
            print(f"Device n°{self.id} closed")

    def __fillBuffer(self):
        for i in range(int(self.capture.get(cv2.CAP_PROP_BUFFERSIZE)) + 1):
            self.getLastFrame()

    def __initSettings(self):
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

    def __setAllSettings(self):
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

        self.__fillBuffer()

        return