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
    frameNumber = 0

    # Get arguments
    args = config.config()

    # Initialize arduino
    arduinoSer = selectPort()
    # Init custom Serial reader to handle readLine correctly
    serialReader = SerialReader(arduinoSer)

    # Setup cameras (a first time is necessary)
    for index in args.cameras:
        CameraPkg.settings.initCamSettings(index) # Initialize camera settings (open/close cameras once seems to be required)

    # Initialize every camera
    for index in args.cameras:
        cam = CameraPkg.device.CaptureDevice(index, savingFrames)
        if cam.capture.isOpened():
            captureDevices.append(cam)

    # Initialize and start saving thread
    savingThread = CameraPkg.saving.SaveWatcher(GLOBAL_RUNNING, savingFrames, args)
    savingThread.start()

    # Check if cameras are running
    if not captureDevices:
        GLOBAL_RUNNING[0] = False

    # Make the motor rotate a first time - direction:angle,time
    serialWrite(arduinoSer, "left:10,60")

    # Main loop
    while(GLOBAL_RUNNING[0]):
        # Read frame
        for cam in captureDevices:
            cam.grabFrame()
        for cam in captureDevices:
            cam.retrieveFrame()


        # While the motor is rotating (before to arrive to a step angle)
        line = serialReader.readline()
        while(line == b''):
            print(line)
            line = serialReader.readline()
            # Read frame
            # print("while")
            for cam in captureDevices:
                cam.grabFrame()
            for cam in captureDevices:
                cam.retrieveFrame()
            # time.sleep(0.02)

        # When the motor reaches the step angle    
        if line == b'Success\r\n' :
            serialWrite(arduinoSer, "left:10,60")

            # Read frame
            for cam in captureDevices:
                cam.grabFrame()
            for cam in captureDevices:
                cam.retrieveFrame()

            # Send frames to the saving buffer
            for cam in captureDevices:
                cam.saveFrame()
            print(frameNumber)

        # If there is an error with the motor, we stop the loop
        elif line != b'':
            print(line)
            GLOBAL_RUNNING[0] = False

        if frameNumber >= 10:
            GLOBAL_RUNNING[0] = False

        frameNumber += 1

    # Wait the end of saving thread
    savingThread.join()

    # When everything done, release the capture devices
    for cam in captureDevices:
        cam.stop()

    # When everything done, release the window
    if args.display:
        cv2.destroyAllWindows()

    logging.info("End of Script")

    return


if __name__ == "__main__":
    main()