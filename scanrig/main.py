#------------------------- IMPORTS
import numpy as np
import cv2, time, logging
import queue

import config
import CameraPkg
from MoteurPkg.SerialManagement import availablePorts, serialWrite, SerialReader, selectPort


#------------------------- SCRIPT

def main():
    captureDevices = []
    GLOBAL_RUNNING = [True]
    savingFrames = queue.Queue()

    # Get arguments
    args = config.config()

    # Initialize arduino
    arduinoSer = selectPort()
    # Init custom Serial reader to handle readLine correctly
    serialReader = SerialReader(arduinoSer)

    # Initialize every camera
    for index in args.cameras:
        cam = CameraPkg.device.CaptureDevice(index, savingFrames)
        if cam.capture.isOpened():
            captureDevices.append(cam)

    # Initialize and start saving thread
    savingThread = CameraPkg.saving.SaveWatcher(GLOBAL_RUNNING, savingFrames, args)
    savingThread.start()

    # Check if cameras are running
    if captureDevices:
        # Give the motor instructions - direction:totalAngle,stepAngle,transition,time
        serialReader.clearBuffer()
        time.sleep(4)
        serialWrite(arduinoSer, "leftCaptureFull:360,15,45,45")
        # serialWrite(arduinoSer, "leftCaptureFull:10,5,30,60")
        # Read frame
        for cam in captureDevices:
            cam.grabFrame()
        for cam in captureDevices:
            cam.retrieveFrame()
    else:    
        GLOBAL_RUNNING[0] = False

    # Main loop
    while(GLOBAL_RUNNING[0]):
        # Read frame
        # for cam in captureDevices:
        #     cam.grabFrame()
        # for cam in captureDevices:
        #     cam.retrieveFrame()

        line = serialReader.readline()
        # While the motor is rotating (before to arrive to a step angle)
        while(line == b''):
            line = serialReader.readline()
            time.sleep(0.01)

        # When the motor reaches the step angle
        if line == b'Capture\r':
            # Read frame
            for cam in captureDevices:
                cam.grabFrame()
            for cam in captureDevices:
                cam.retrieveFrame()

            # Send frames to the saving buffer
            for cam in captureDevices:
                cam.saveFrame()

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
    for cam in captureDevices:
        cam.stop()

    logging.info("End of Script")

    return


if __name__ == "__main__":
    main()