import numpy as np
import cv2, time, logging

import args_parser
import CameraPkg
from MoteurPkg.serial_management import availablePorts, serialWrite, SerialReader, selectPort

class Acquisition():
    def __init__(self):
        self.captureDevices = CameraPkg.capture_device_list.CaptureDeviceList()
        for id in self.captureDevices.listAvailableDevices():
            self.captureDevices.addDevice(id)

        self.captureDevices.setAllAttributesToDevices() # Give to devices the default settings

    def start(self):
        GLOBAL_RUNNING = [True]

        # Get arguments
        args = args_parser.parse()

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

