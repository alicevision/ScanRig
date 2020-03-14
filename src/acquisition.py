from PySide2 import QtWidgets
from PySide2.QtCore import QObject, Slot, Property, Signal

import numpy as np
import cv2, time, logging
import os

from enum import Enum, auto

import args_parser
import CameraPkg
from CameraPkg.capture_device_list import CaptureDeviceList
from CameraPkg.uvc_camera import UvcCamera
from CameraPkg.saving import SaveWatcher
from MoteurPkg.serial_management import availablePorts, serialWrite, SerialReader, selectPort


class AcquisitionState(Enum):
    ON = auto()
    OFF = auto()
    OVER = auto()

class Acquisition(QObject):
    def __init__(self):
        super().__init__()
        self.captureDevices = CaptureDeviceList()
        self.runningAcquisition = AcquisitionState.OFF
        self.savingDirectory = ""
        self.takenImages = 0

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
            "bsgi": False,
            "bsgiAngle": 45
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
    def getEngineBSGI(self):                   
        return self.engineSettings["bsgi"]
                                         
    @Slot(bool)
    def setEngineBSGI(self, val):
        self.engineSettings["bsgi"] = val
        self.engineBSGIChanged.emit()

    engineBSGIChanged = Signal()
    bsgi = Property(bool, getEngineBSGI, setEngineBSGI, notify=engineBSGIChanged)


    @Slot()
    def getEngineBSGIAngle(self):                   
        return self.engineSettings["bsgiAngle"]
                                         
    @Slot(int)
    def setEngineBSGIAngle(self, val):
        self.engineSettings["bsgiAngle"] = val
        self.engineBSGIAngleChanged.emit()

    engineBSGIAngleChanged = Signal()
    bsgiAngle = Property(int, getEngineBSGIAngle, setEngineBSGIAngle, notify=engineBSGIAngleChanged)


    @Slot()
    def startEngine(self):
        print("Starting Engine")


#-------------------------------------------- IMAGES
    @Slot(str)
    def changeSavingDirectory(self, path) :
        directory = path.split("file://")[1]
        print(directory)
        self.savingDirectory = directory

    
    @Slot()
    def getTakenImages(self):                   
        return self.takenImages
                                         
    @Slot()
    def incrementTakenImages(self):
        self.takenImages += 1
        self.takenImagesChanged.emit()

    takenImagesChanged = Signal()
    takenImagesProp = Property(int, getTakenImages, incrementTakenImages, notify=takenImagesChanged)

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
            self.captureDevices.grabFrames()
            self.captureDevices.retrieveFrames()
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
                self.captureDevices.grabFrames()
                self.captureDevices.retrieveFrames()

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
        self.takenImages = 0
        i = 0

        # Start UVC Cameras
        for device in self.captureDevices.devices:
            if isinstance(device, UvcCamera):
                device.start()
        # Set the queue saving frames to every devices
        self.captureDevices.setSavingFramesToDevices()

        # Initialize and start saving thread
        stopSavingThread = [False]
        savingThread = SaveWatcher(stopSavingThread, self.captureDevices.savingFrames, self.savingDirectory)
        savingThread.start()

        while True:
            if stop():
                break

            if i > 50:
                break

            self.captureDevices.grabFrames()
            self.captureDevices.retrieveFrames()

            if i % 10 == 0 :
                self.captureDevices.saveFrames()

            i += 1

        # Wait the end of saving thread
        stopSavingThread[0] = True
        savingThread.join()

        self.captureDevices.stopDevices()
        logging.info("End of Acquisition")
        self.runningAcquisition = AcquisitionState.OVER
