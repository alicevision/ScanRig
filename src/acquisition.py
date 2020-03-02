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

    @Slot()
    def startEngine(self):
        print("Starting Engine")

    def start(self, stop):
        self.runningAcquisition = AcquisitionState.ON
        i = 0

        # Start UVC Cameras
        for device in self.captureDevices.devices:
            if isinstance(device, UvcCamera):
                device.start()

        while True:
            if stop():
                break

            if i > 50:
                break

            self.captureDevices.grabFrames()
            self.captureDevices.retrieveFrames()

            if i % 10 == 0 :
                frame = self.captureDevices.devices[0].frame
                directory = self.savingDirectory
                filename = f'cam_0_{i}.jpg'
                outFilepath = os.path.join(directory, filename)
                logging.info(f'Writting file={outFilepath}')
                cv2.imwrite(outFilepath, frame)

            i += 1

        self.captureDevices.stopDevices()
        print("End of Acquisition")
        self.runningAcquisition = AcquisitionState.OVER


    @Slot(str)
    def changeSavingDirectory(self, path) :
        directory = path.split("file://")[1]
        print(directory)
        self.savingDirectory = directory