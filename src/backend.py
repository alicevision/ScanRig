from PySide2 import QtWidgets
from PySide2.QtCore import QObject, Slot, Property, Signal

import threading

from acquisition import Acquisition, AcquisitionState
from capture_device_preview import CaptureDevicePreview
from UIPkg.image_provider import ImageProvider

import time

class Backend(QObject):
    def __init__(self):
        super().__init__()
        self.preview = CaptureDevicePreview()
        self.acquisition = Acquisition(self.preview.captureDevices.settings)
        self.mainLayout = True

        # THREAD: Main Thread which works continuously
        self.stopMainThread = False
        self.mainThread = threading.Thread(target=self.runMainThread, args=(lambda: self.stopMainThread,))
        self.mainThread.start()

        # THREAD: Acquisition
        self.createAcquisitionThread()


    #---------- MAIN THREAD
    def runMainThread(self, stop):
        while True:
            if stop():
                break

            if self.preview.runningPreview:
                self.preview.captureDevices.grabFrames()
                self.preview.captureDevices.retrieveFrames()

            if self.acquisition.runningAcquisition == AcquisitionState.OVER:
                self.acquisition.runningAcquisition = AcquisitionState.OFF # STOP Acquisition
                self.acquisitionThread.join() # Wait the end of the thread

                self.createAcquisitionThread() # Create a new acquisition thread

                self.preview.changePreview(self.preview.currentId) # RELAUNCH Preview with the active camera
                self.setMainLayout(True) # ENABLE back the layout


            time.sleep(0.04)
        print("End of Main Thread")


    #---------- LAYOUT
    @Slot()
    def getMainLayout(self):                         
        return self.mainLayout                                              
    
    @Slot(bool)
    def setMainLayout(self, boolean):
        self.mainLayout = boolean
        self.mainLayoutChanged.emit()

    mainLayoutChanged = Signal()
    mainLayoutEnabled = Property(bool, getMainLayout, setMainLayout, notify=mainLayoutChanged)


    #---------- APPLICATION
    @Slot()
    def exitApplication(self):
        # Stop the Main Thread
        self.stopMainThread = True
        self.mainThread.join() # Make appear some QML Warnings but it does not really matter (seems like a bug)
        self.preview.captureDevices.stopDevices()

        print("EXIT APPLICATION")


    #---------- ACQUISITION
    def createAcquisitionThread(self):
        self.stopAcquisitionThread = False
        self.acquisitionThread = threading.Thread(target=self.acquisition.start, args=(lambda: self.stopAcquisitionThread,))


    @Slot()
    def startAcquisition(self):
        # STOP THE PREVIEW AND ALL THE DEVICES
        self.preview.runningPreview = False
        time.sleep(0.04)
        self.preview.captureDevices.stopDevices()

        # Start acquisition
        self.acquisitionThread.start()

    @Slot()
    def stopAcquisition(self):
        self.stopAcquisitionThread = True