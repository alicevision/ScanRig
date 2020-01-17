import numpy as np
import threading, logging, cv2

import config, cameraSettings

class GetFrameThread(threading.Thread):
    def __init__(self, capDevice):
        threading.Thread.__init__(self)
        self.capDevice = capDevice

    def run(self):
        (self.capDevice.status, self.capDevice.frame) = self.capDevice.capture.read()
        print(f"Reading frame from cam {self.capDevice.indexCam}")


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
            cameraSettings.setAttributes(self.capture)
            cameraSettings.getAttributes(self.capture)
        else:
            logging.warning("Skip invalid stream ID {}".format(self.indexCam))
            self.stop()

    def saveFrame(self):
        self.framesToSave.append((self.indexCam, self.nbSavedFrame, self.frame))
        self.nbSavedFrame += 1

    def stop(self):
        self.capture.release()