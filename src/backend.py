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
        self.acquisition = Acquisition()
        self.preview = CaptureDevicePreview(self.acquisition.captureDevices)
        self.mainLayout = True
        self.readyForAcquisition = False

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
                self.preview.previewDevices.readFrames()

            if self.acquisition.runningAcquisition == AcquisitionState.OVER:
                self.acquisition.runningAcquisition = AcquisitionState.OFF # STOP Acquisition
                self.acquisitionThread.join() # Wait the end of the thread

                self.createAcquisitionThread() # Create a new acquisition thread

                self.preview.changePreview(self.preview.currentId) # RELAUNCH Preview with the active camera
                self.setMainLayout(True) # ENABLE back the layout


            time.sleep(0.04)
        
        self.preview.runningPreview = False
        time.sleep(0.1)
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
    @Slot(result=bool)
    def exitApplication(self):
        # Reject exit if the acquisition process is not over
        if self.acquisition.runningAcquisition == AcquisitionState.ON:
            return False

        # Stop the Main Thread
        self.stopMainThread = True
        self.mainThread.join() # Make appear some QML Warnings but it does not really matter (seems like a bug)

        print("EXIT APPLICATION")
        return True


    #---------- ACQUISITION
    def createAcquisitionThread(self):
        self.stopAcquisitionThread = False
        self.acquisitionThread = threading.Thread(target=self.acquisition.start, args=(lambda: self.stopAcquisitionThread,))


    @Slot(result=bool)
    def startAcquisition(self):
        if self.acquisition.captureDevices.isEmpty():
            return False

        # STOP THE PREVIEW AND EMPTY THE PREVIEW LIST
        self.preview.runningPreview = False
        time.sleep(0.04)
        self.preview.previewDevices.emptyDevices()

        # Start acquisition
        self.acquisitionThread.start()
        return True

    @Slot(result=bool)
    def stopAcquisition(self):
        if self.acquisition.runningAcquisition == AcquisitionState.ON:
            self.stopAcquisitionThread = True
            return True
        else:
            return False

    #---------- QLM Property
    @Slot(result=bool)
    def getReadyForAcquisition(self):
        return self.readyForAcquisition                                     
    
    @Slot(bool)
    def setReadyForAcquisition(self, boolean):
        self.readyForAcquisition = boolean
        self.readyForAcquisitionChanged.emit()

    readyForAcquisitionChanged = Signal()
    readyForAcquisitionProperty = Property(bool, getReadyForAcquisition, setReadyForAcquisition, notify=readyForAcquisitionChanged)