from PySide2 import QtWidgets
from PySide2.QtCore import QObject, Slot, Property, Signal

import threading

from acquisition import Acquisition, AcquisitionState
from capture_device_preview import CaptureDevicePreview
from UIPkg.image_provider import ImageProvider
from CameraPkg.streaming_api import StreamingAPI

import time

class Backend(QObject):
    """Class used to control the backend of the application."""

    def __init__(self, streamingAPI):
        """Backend constructor

        Args:
            streamingAPI (StreamingAPI): Enum used to know the StreamingAPI (USBCam or OpenCV) specified in the terminal
        """
        super().__init__()
        self.streamingAPI = streamingAPI
        self.acquisition = Acquisition(self.streamingAPI)
        self.preview = CaptureDevicePreview(self.acquisition, self.streamingAPI)
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
        """Method used to run the main thread of the application.

        Args:
            stop (lambda): lambda function used with a boolean to stop the thread when it will be necessary.
        """
        while True:
            if stop():
                break

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
        """Getter mainLayout

        Returns:
            bool: If True, the 'Main Layout' of the UI is enabled. If False, it is not.
        """                  
        return self.mainLayout                                              
    
    @Slot(bool)
    def setMainLayout(self, boolean):
        """Setter mainLayout

        Args:
            boolean (bool): If True, enable the 'Main Layout' of the UI. If False, disable it.
        """
        self.mainLayout = boolean
        self.mainLayoutChanged.emit()

    mainLayoutChanged = Signal()
    mainLayoutEnabled = Property(bool, getMainLayout, setMainLayout, notify=mainLayoutChanged)


    @Slot()
    def getAPI(self):
        """Method to return the current Streaming API running by the application.

        Returns:
            str: Name of the Streaming API.
        """
        if self.streamingAPI == StreamingAPI.USBCAM:
            return "usbcam"
        elif self.streamingAPI == StreamingAPI.OPENCV:
            return "opencv"
        else:
            return "no API"                                                                      
    
    streamingAPINameChanged = Signal()
    streamingAPIName = Property(str, getAPI, notify=streamingAPINameChanged)  


    #---------- APPLICATION
    @Slot(result=bool)
    def exitApplication(self):
        """Method called when the application is going to close.

        Returns:
            bool: If True, the application can close. If False, the application cannot.
        """
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
        """Method to create the acquisition thread"""
        self.stopAcquisitionThread = False
        self.acquisitionThread = threading.Thread(target=self.acquisition.start, args=(lambda: self.stopAcquisitionThread,))


    @Slot(result=bool)
    def startAcquisition(self):
        """Method to start the acquisition. Stop the preview and then, start the acquisition thread.

        Returns:
            bool: If True, the acquisition thread is started. If False, it is not.
        """
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
        """Method to stop the acquisition.

        Returns:
            bool: If True, the acquisition thread is stopped. If False, nothing happened.
        """
        if self.acquisition.runningAcquisition == AcquisitionState.ON:
            self.stopAcquisitionThread = True
            return True
        else:
            return False

    #---------- QLM Property
    @Slot(result=bool)
    def getReadyForAcquisition(self):
        """Getter readyForAcquisition

        Returns:
            bool: If True, the application is ready to start the acquisition. If False, it is not.
        """
        return self.readyForAcquisition                                     
    
    @Slot(bool)
    def setReadyForAcquisition(self, boolean):
        """Setter readyForAcquisition

        Args:
            bool: If True, the application is ready to start the acquisition. If False, it is not.
        """
        self.readyForAcquisition = boolean
        self.readyForAcquisitionChanged.emit()

    readyForAcquisitionChanged = Signal()
    readyForAcquisitionProperty = Property(bool, getReadyForAcquisition, setReadyForAcquisition, notify=readyForAcquisitionChanged)