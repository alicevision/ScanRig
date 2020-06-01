from PySide2 import QtWidgets
from PySide2.QtCore import QObject, Slot, Property, Signal

import numpy as np
import cv2, time, logging
import os

from enum import Enum, auto

import CameraPkg
from CameraPkg.capture_device_list import CaptureDeviceList
from CameraPkg.opencv_camera import OpencvCamera
from CameraPkg.saving import SaveWatcher
from MoteurPkg.serial_management import availablePorts, serialWrite, SerialReader, selectPort
from CameraPkg.streaming_api import StreamingAPI


class AcquisitionState(Enum):
    """Enum for the Acquisiton State."""
    ON = auto()
    OFF = auto()
    OVER = auto()

class Acquisition(QObject):
    """Class used to control the acquistion process."""

    def __init__(self, streamingAPI):
        """Acquisition constructor

        Args:
            streamingAPI (StreamingAPI): Enum used to know the StreamingAPI (USBCam or OpenCV) specified in the terminal
        """
        super().__init__()
        self.streamingAPI = streamingAPI
        self.captureDevices = CaptureDeviceList()
        self.runningAcquisition = AcquisitionState.OFF
        self.savingRootDirectory = os.path.dirname(__file__)
        self.nbTakenImages = 0
        self.nbImagesToTake = 0

        self.engineSettings = self.initEngineSettings()
        self.arduinoSer = None
        self.serialReader = None


#-------------------------------------------- ENGINE SETTINGS
    def initEngineSettings(self):
        """Method to init the engine settings.

        Returns:
            Object: Object containing all the engine settings.
        """
        settings = {
            "totalAngle": 180,
            "stepAngle": 15,
            "direction": 0,
            "acceleration": 45,
            "timeSpeed": 50,
            "photometricStereo": False,
            "photometricStereoAngle": 45
        }
        return settings


    @Slot()
    def getEngineTotalAngle(self):
        """Getter totalAngle: the number of degrees to be covered during acquisition.

        Returns:
            int: Value of totalAngle.
        """
        return self.engineSettings["totalAngle"]
                                         
    @Slot(int)
    def setEngineTotalAngle(self, val):
        """Setter totalAngle: the number of degrees to be covered during acquisition.

        Args:
            val (int): Value to set.
        """
        self.engineSettings["totalAngle"] = val
        self.engineTotalAngleChanged.emit()

    engineTotalAngleChanged = Signal()
    totalAngle = Property(int, getEngineTotalAngle, setEngineTotalAngle, notify=engineTotalAngleChanged)


    @Slot()
    def getEngineStepAngle(self): 
        """Getter stepAngle: the number of degrees which separates two consecutive captures.

        Returns:
            int: Value of stepAngle.
        """                  
        return self.engineSettings["stepAngle"]
                                         
    @Slot(int)
    def setEngineStepAngle(self, val):
        """Setter stepAngle: the number of degrees which separates two consecutive captures.

        Args:
            val (int): Value to set.
        """
        self.engineSettings["stepAngle"] = val
        self.engineStepAngleChanged.emit()

    engineStepAngleChanged = Signal()
    stepAngle = Property(int, getEngineStepAngle, setEngineStepAngle, notify=engineStepAngleChanged)


    @Slot()
    def getEngineDirection(self):
        """Getter direction: clockwise or counterclockwise direction.

        Returns:
            int: O for left, 1 for right.
        """                          
        return self.engineSettings["direction"]
                                         
    @Slot(int)
    def setEngineDirection(self, val):
        """Setter direction: clockwise or counterclockwise direction.

        Args:
            val (int): Value to set. 0 for left, 1 for right.
        """                
        self.engineSettings["direction"] = val
        self.engineDirectionChanged.emit()

    engineDirectionChanged = Signal()
    direction = Property(int, getEngineDirection, setEngineDirection, notify=engineDirectionChanged)


    @Slot()
    def getEngineAcceleration(self): 
        """Getter acceleration: the number of degrees used by the arm to accelerate before starting the acquisition.

        Returns:
            int: Value of acceleration.
        """                        
        return self.engineSettings["acceleration"]
                                         
    @Slot(int)
    def setEngineAcceleration(self, val):
        """Setter acceleration: the number of degrees used by the arm to accelerate before starting the acquisition.

        Args:
            val (int): Value to set.
        """   
        self.engineSettings["acceleration"] = val
        self.engineAccelerationChanged.emit()

    engineAccelerationChanged = Signal()
    acceleration = Property(int, getEngineAcceleration, setEngineAcceleration, notify=engineAccelerationChanged)


    @Slot()
    def getEngineTimeSpeed(self):  
        """Getter timeSpeed: this is actually the speed of the rotation. This value (in seconds) is the required time for a complete revolution.

        Returns:
            int: Value of timeSpeed.
        """                   
        return self.engineSettings["timeSpeed"]
                                         
    @Slot(int)
    def setEngineTimeSpeed(self, val):
        """Setter timeSpeed: this is actually the speed of the rotation. This value (in seconds) is the required time for a complete revolution.

        Args:
            val (int): Value to set.
        """  
        self.engineSettings["timeSpeed"] = val
        self.engineTimeSpeedChanged.emit()

    engineTimeSpeedChanged = Signal()
    timeSpeed = Property(int, getEngineTimeSpeed, setEngineTimeSpeed, notify=engineTimeSpeedChanged)


    @Slot()
    def getEnginePhotometricStereo(self):  
        """Getter photometricStereo

        Returns:
            bool: If True, 'Photometric Stereo' is enabled. If False, it is not.
        """                       
        return self.engineSettings["photometricStereo"]
                                         
    @Slot(bool)
    def setEnginePhotometricStereo(self, val):
        """Setter photometricStereo

        Args:
            val (bool): If True, enable 'Photometric Stereo'. If False, disable it.
        """
        self.engineSettings["photometricStereo"] = val
        self.enginePhotometricStereoChanged.emit()

    enginePhotometricStereoChanged = Signal()
    photometricStereo = Property(bool, getEnginePhotometricStereo, setEnginePhotometricStereo, notify=enginePhotometricStereoChanged)


    @Slot()
    def getEnginePhotometricStereoAngle(self):  
        """Getter photometricStereoAngle: the number of degrees which separates two consecutive Photometric Stereo captures.

        Returns:
            int: Value of photometricStereoAngle.
        """                   
        return self.engineSettings["photometricStereoAngle"]
                                         
    @Slot(int)
    def setEnginePhotometricStereoAngle(self, val):
        """Setter photometricStereoAngle: the number of degrees which separates two consecutive Photometric Stereo captures.

        Args:
            val (int): Value to set.
        """       
        self.engineSettings["photometricStereoAngle"] = val
        self.enginePhotometricStereoAngleChanged.emit()

    enginePhotometricStereoAngleChanged = Signal()
    photometricStereoAngle = Property(int, getEnginePhotometricStereoAngle, setEnginePhotometricStereoAngle, notify=enginePhotometricStereoAngleChanged)


    @Slot()
    def startEngine(self):
        # Useless for now. Can be useful if we want to switch on the engine and control it before launching the acquisition.
        # Do not delete the method as it a slot for QML Button.
        print("Starting Engine")


#-------------------------------------------- IMAGES
    @Slot(str)
    def changeSavingDirectory(self, path) :
        """Method to change the image saving directory path. Used in combination with QML.

        Args:
            path (str): Directory path coming from QML.
        """
        directory = path.split("file://")[1]
        print(directory)
        self.savingRootDirectory = directory

    def createCaptureFolder(self):
        """Method to create a capture folder inside of the saving directory path."""
        root = self.savingRootDirectory
        newFolder = os.path.join(root, "capture")
        os.makedirs(newFolder, exist_ok=True)
        self.savingRootDirectory = newFolder

    
    @Slot()
    def getNbTakenImages(self):
        """Getter nbTakenImages

        Returns:
            int: number of pictures already taken.
        """
        return self.nbTakenImages
                                         
    @Slot(int)
    def setNbTakenImages(self, val):
        """Setter nbTakenImages: not a normal setter.

        Args:
            val (int): 0 will set the attribute to 0. 1 will increment the attribute by 1.
        """
        if val == 0:
            self.nbTakenImages = 0
        if val == 1:
            self.nbTakenImages += 1
        self.nbTakenImagesChanged.emit()

    nbTakenImagesChanged = Signal()
    nbTakenImagesProp = Property(int, getNbTakenImages, setNbTakenImages, notify=nbTakenImagesChanged)


    @Slot()
    def getNbImagesToTake(self):
        """Getter nbImagesToTake

        Returns:
            int: number of pictures each camera has to take.
        """          
        return self.nbImagesToTake
                                         
    @Slot(int)
    def setNbImagesToTake(self, val):
        """Setter nbImagesToTake

        Args:
            val (int): number of pictures each camera has to take.
        """
        self.nbImagesToTake = val
        self.nbImagesToTakeChanged.emit()

    nbImagesToTakeChanged = Signal()
    nbImagesToTakeProp = Property(int, getNbImagesToTake, setNbImagesToTake, notify=nbImagesToTakeChanged)

#-------------------------------------------- ACQUISITION

    def start(self, stop):
        """Method to launch the acquisition process.

        Args:
            stop (lambda): lambda function used with a boolean to stop the thread if it is necessary.
        """
        self.runningAcquisition = AcquisitionState.ON
        self.setNbTakenImages(0)
        self.setNbImagesToTake(11)
        i = 0

        print(self.engineSettings)

        # Set the acquisition format to each camera
        for device in self.captureDevices.devices:
            device.SetFormat(device.GetAcquisitionFormat())

        # Set the saving parameters to cameras (and the saving queue for OPENCV API)
        self.captureDevices.setSavingToCameras(self.savingRootDirectory)

        # Initialize and start saving thread ONLY IF OPENCV CAMERAS
        if self.streamingAPI == StreamingAPI.OPENCV:
            stopSavingThread = [False]
            savingThread = SaveWatcher(stopSavingThread, self.captureDevices.savingQueue)
            savingThread.start()

        while True:
            if stop():
                break

            if i > 100:
                break

            self.captureDevices.readFrames()

            if i % 10 == 0 :
                self.captureDevices.saveFrames()
                self.setNbTakenImages(1)

            i += 1

        # Wait the end of saving thread (ONLY FOR OPENCV API)
        if self.streamingAPI == StreamingAPI.OPENCV:        
            stopSavingThread[0] = True
            savingThread.join()

        logging.info("End of Acquisition")
        self.runningAcquisition = AcquisitionState.OVER



    # Real start method using the engine. Supposed to work. We cannot try for the moment.
    """
    def start(self, stop):
        self.runningAcquisition = AcquisitionState.ON
        self.setNbTakenImages(0) # Set the number of taken images to 0
        self.setNbImagesToTake(self.engineSettings.get('totalAngle') / self.engineSettings.get('stepAngle')) # Set the number of images to take


        # Set the acquisition format to each camera
        for device in self.captureDevices.devices:
            device.SetFormat(device.GetAcquisitionFormat())

        # Set the saving parameters to cameras (and the saving queue for OPENCV API)
        self.captureDevices.setSavingToCameras(self.savingRootDirectory)

        # Initialize and start saving thread ONLY IF OPENCV CAMERAS
        if self.streamingAPI == StreamingAPI.OPENCV:
            stopSavingThread = [False]
            savingThread = SaveWatcher(stopSavingThread, self.captureDevices.savingQueue)
            savingThread.start()


        # Initialize arduino
        arduinoSer = selectPort()
        # Init custom Serial reader to handle readLine correctly
        serialReader = SerialReader(arduinoSer)

        # Get the engine configuration
        totalAngle = self.engineSettings.get('totalAngle')
        stepAngle = self.engineSettings.get('stepAngle')
        direction = 'left' if self.engineSettings.get('direction') == 0 else 'right'
        acceleration = self.engineSettings.get('acceleration')
        timeSpeed = self.engineSettings.get('timeSpeed')
        
        # Give instruction to the engine to launch it
        serialWrite(arduinoSer, f'{direction}CaptureFull:{totalAngle},{stepAngle},{acceleration},{timeSpeed}')


        # Main loop
        while True:
            if stop():
                break

            line = serialReader.readline()
            # While the motor is rotating (before to arrive to a step angle)
            while(line == b''):
                line = serialReader.readline()
                time.sleep(0.01)

            # When the motor reaches the step angle
            if line == b'Capture\r':
                # Read frame
                self.captureDevices.readFrames()

                # Save frame + Increment number
                self.captureDevices.saveFrames()
                self.setNbTakenImages(1)

            # When the motor reaches the end    
            elif line == b'Success\r' :
                print("Success!!!!")
                break

            # If there is an error with the motor, we stop the loop
            elif line != b'':
                print(line)
                break


        # Wait the end of saving thread (ONLY FOR OPENCV API)
        if self.streamingAPI == StreamingAPI.OPENCV:        
            stopSavingThread[0] = True
            savingThread.join()

        logging.info("End of Acquisition")
        self.runningAcquisition = AcquisitionState.OVER
        """