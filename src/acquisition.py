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
    ON = auto()
    OFF = auto()
    OVER = auto()

class Acquisition(QObject):
    def __init__(self, streamingAPI):
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
        return self.engineSettings["totalAngle"]
                                         
    @Slot(int)
    def setEngineTotalAngle(self, val):
        self.engineSettings["totalAngle"] = val
        self.engineTotalAngleChanged.emit()

    engineTotalAngleChanged = Signal()
    totalAngle = Property(int, getEngineTotalAngle, setEngineTotalAngle, notify=engineTotalAngleChanged)


    @Slot()
    def getEngineStepAngle(self):                   
        return self.engineSettings["stepAngle"]
                                         
    @Slot(int)
    def setEngineStepAngle(self, val):
        self.engineSettings["stepAngle"] = val
        self.engineStepAngleChanged.emit()

    engineStepAngleChanged = Signal()
    stepAngle = Property(int, getEngineStepAngle, setEngineStepAngle, notify=engineStepAngleChanged)


    @Slot()
    def getEngineDirection(self):                   
        return self.engineSettings["direction"]
                                         
    @Slot(int)
    def setEngineDirection(self, val):
        self.engineSettings["direction"] = val
        self.engineDirectionChanged.emit()

    engineDirectionChanged = Signal()
    direction = Property(int, getEngineDirection, setEngineDirection, notify=engineDirectionChanged)


    @Slot()
    def getEngineAcceleration(self):                   
        return self.engineSettings["acceleration"]
                                         
    @Slot(int)
    def setEngineAcceleration(self, val):
        self.engineSettings["acceleration"] = val
        self.engineAccelerationChanged.emit()

    engineAccelerationChanged = Signal()
    acceleration = Property(int, getEngineAcceleration, setEngineAcceleration, notify=engineAccelerationChanged)


    @Slot()
    def getEngineTimeSpeed(self):                   
        return self.engineSettings["timeSpeed"]
                                         
    @Slot(int)
    def setEngineTimeSpeed(self, val):
        self.engineSettings["timeSpeed"] = val
        self.engineTimeSpeedChanged.emit()

    engineTimeSpeedChanged = Signal()
    timeSpeed = Property(int, getEngineTimeSpeed, setEngineTimeSpeed, notify=engineTimeSpeedChanged)


    @Slot()
    def getEnginePhotometricStereo(self):                   
        return self.engineSettings["photometricStereo"]
                                         
    @Slot(bool)
    def setEnginePhotometricStereo(self, val):
        self.engineSettings["photometricStereo"] = val
        self.enginePhotometricStereoChanged.emit()

    enginePhotometricStereoChanged = Signal()
    photometricStereo = Property(bool, getEnginePhotometricStereo, setEnginePhotometricStereo, notify=enginePhotometricStereoChanged)


    @Slot()
    def getEnginePhotometricStereoAngle(self):                   
        return self.engineSettings["photometricStereoAngle"]
                                         
    @Slot(int)
    def setEnginePhotometricStereoAngle(self, val):
        self.engineSettings["photometricStereoAngle"] = val
        self.enginePhotometricStereoAngleChanged.emit()

    enginePhotometricStereoAngleChanged = Signal()
    photometricStereoAngle = Property(int, getEnginePhotometricStereoAngle, setEnginePhotometricStereoAngle, notify=enginePhotometricStereoAngleChanged)


    @Slot()
    def startEngine(self):
        print("Starting Engine")


#-------------------------------------------- IMAGES
    @Slot(str)
    def changeSavingDirectory(self, path) :
        directory = path.split("file://")[1]
        print(directory)
        self.savingRootDirectory = directory

    def createCaptureFolder(self):
        root = self.savingRootDirectory
        newFolder = os.path.join(root, "capture")
        os.makedirs(newFolder, exist_ok=True)
        self.savingRootDirectory = newFolder

    
    @Slot()
    def getNbTakenImages(self):                   
        return self.nbTakenImages
                                         
    @Slot(int)
    def setNbTakenImages(self, val):
        if val == 0:
            self.nbTakenImages = 0
        if val == 1:
            self.nbTakenImages += 1
        self.nbTakenImagesChanged.emit()

    nbTakenImagesChanged = Signal()
    nbTakenImagesProp = Property(int, getNbTakenImages, setNbTakenImages, notify=nbTakenImagesChanged)


    @Slot()
    def getNbImagesToTake(self):                   
        return self.nbImagesToTake
                                         
    @Slot(int)
    def setNbImagesToTake(self, val):
        self.nbImagesToTake = val
        self.nbImagesToTakeChanged.emit()

    nbImagesToTakeChanged = Signal()
    nbImagesToTakeProp = Property(int, getNbImagesToTake, setNbImagesToTake, notify=nbImagesToTakeChanged)

#-------------------------------------------- ACQUISITION

    '''
    def start(self):
        GLOBAL_RUNNING = [True]

        # Get arguments
        args = args_parser.parse()CheckBox
        # Initialize arduino
        arduinoSer = selectPort()
        # Init custom Serial reader to handle readLine correctly
        serialReader = SerialReader(arduinoSer)

        # Initialize and start saving thread
        savingThread = CameraPkg.saving.SaveWatcher(GLOBAL_RUNNING, self.captureDevices.savingFrames, args)
        savingThread.start()

        # Check if cameras are running
        if not self.captureDevices.isEmpty():
            # Give the motor instructions - direction:totalAngle,stepAngle,transition,time
            time.sleep(2)
            serialWrite(arduinoSer, "leftCaptureFull:60,15,45,45")
            # Read frame
            self.captureDevices.readFrames()
        else:    
            GLOBAL_RUNNING[0] = False

        # Main loop
        while(GLOBAL_RUNNING[0]):

            line = serialReader.readline()
            # While the motor is rotating (before to arrive to a step angle)
            while(line == b''):
                line = serialReader.readline()
                time.sleep(0.01)

            # When the motor reaches the step angle
            if line == b'Capture\r':
                # Read frame
                self.captureDevices.readFrames()

                # Send frames to the saving buffer
                self.captureDevices.saveFrames()

            # When the motor reaches the end    
            elif line == b'Success\r' :
                print("Success!!!!")
                GLOBAL_RUNNING[0] = False

            # If there is an error with the motor, we stop the loop
            elif line != b'':
                print(line)
                GLOBAL_RUNNING[0] = False


        # Wait the end of saving thread
        savingThread.join()

        # When everything done, release the capture devices
        self.captureDevices.stopDevices()

        logging.info("End of Capture")

        return
        '''


    def start(self, stop):
        self.runningAcquisition = AcquisitionState.ON
        self.setNbTakenImages(0)
        self.setNbImagesToTake(11)
        i = 0

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
