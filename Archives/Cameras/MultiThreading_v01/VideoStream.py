import cv2, logging, threading, time

import config
import cameraSettings

class VideoStream(threading.Thread):
    def __init__(self, indexCam):
        threading.Thread.__init__(self)

        self.indexCam = indexCam
        self.running = True
        self.nbSavedFrame = 0
        self.toSave = False
        (self.status, self.frame) = (None, None)

        # Initialize camera
        self.capture = cv2.VideoCapture()

        v = self.capture.open(self.indexCam, apiPreference=cv2.CAP_V4L2)
        if v:
            cameraSettings.setAttributes(self.capture)
            cameraSettings.getAttributes(self.capture)
        else:
            logging.warning("Skip invalid stream ID {}".format(self.indexCam))
            self.stop()

    def run(self):       
        while(self.running):
            (self.status, self.frame) = self.capture.read()

            if self.toSave and self.status:
                config.framesToSave.append((self.indexCam, self.nbSavedFrame, self.frame))
                self.nbSavedFrame += 1
                self.toSave = False

            if not config.GLOBAL_RUNNING:
                self.stop()


    def stop(self):
        self.running = False
        self.capture.release()