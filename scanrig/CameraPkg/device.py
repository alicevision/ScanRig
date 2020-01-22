import numpy as np
import threading, logging, cv2

from CameraPKG import settings

class CaptureDevice(object):
    def __init__(self, indexCam, framesToSave):
        self.indexCam = indexCam
        (self.status, self.frame) = (None, None)
        self.nbSavedFrame = 0
        self.framesToSave = framesToSave

        # Initialize camera
        self.capture = cv2.VideoCapture()

        v = self.capture.open(self.indexCam, apiPreference=cv2.CAP_V4L2)
        if v:
            settings.setAttributes(self.capture)
            settings.getAttributes(self.capture)
        else:
            logging.warning("Skip invalid stream ID {}".format(self.indexCam))
            self.stop()

    def grabFrame(self):
        if not self.capture.grab():
            logging.warning("Image cannot be grabbed")

    def retrieveFrame(self):
        self.status, self.frame = self.capture.retrieve()
        # self.frame = cv2.cvtColor(self.frame, cv2.COLOR_YUV2BGR_UYVY) # To use only with the FSCAM_CU135
        if not self.status:
            logging.warning("Image cannot be retrieved")

    def saveFrame(self):
        self.framesToSave.put((self.indexCam, self.nbSavedFrame, self.frame))
        self.nbSavedFrame += 1

    def stop(self):
        self.capture.release()