#------------------------- IMPORTS
import numpy as np
import cv2, time, logging
import queue

import config
from Camera import CaptureDevice, GetFrameThread
from Saving import SaveWatcher
import cameraSettings


#------------------------- SCRIPT

def main():
    captureDevices = []
    GLOBAL_RUNNING = [True]
    savingFrames = queue.Queue()

    frameNumber = 0

    # Get arguments
    config.ARGS = config.config()

    # Setup cameras (a first time is necessary)
    # for index in config.ARGS.cameras:
    #     # cameraSettings.initCamSettings(index) # Initialize camera settings (open/close cameras once seems to be required)
    #     pass

    # Initialize every camera
    for index in config.ARGS.cameras:
        cam = CaptureDevice(index, savingFrames)
        if cam.capture.isOpened():
            captureDevices.append(cam)

    # Initialize and start saving thread
    savingThread = SaveWatcher(GLOBAL_RUNNING, savingFrames)
    savingThread.start()

    # Check if cameras are running
    if not captureDevices:
        GLOBAL_RUNNING[0] = False

    # Main loop
    while(GLOBAL_RUNNING[0]):
        if frameNumber >= 30:
            GLOBAL_RUNNING[0] = False

        # for cam in captureDevices:
        #     cam.grabFrame()

        for cam in captureDevices:
            cam.retrieveFrame()

        print("Motor ACTION")

        # THIS IS A TEST
        if frameNumber % 5 == 0:
            for cam in captureDevices:
                cam.saveFrame()

        # if frameNumber == 50:
        #     cameraSettings.changeAttributes(2000, 8000)
        #     for cam in captureDevices:
        #         for i in range(int(cam.settings["bufferSize"]) + 1):
        #             cam.grabFrame()
        #         cameraSettings.setAttributes(cam.capture)

        # time.sleep(0.001)

        frameNumber += 1
        print(frameNumber)
        # time.sleep(0.05)

    # Wait the end of saving thread
    savingThread.join()

    # When everything done, release the capture devices
    for camera in captureDevices:
        camera.stop()

    # When everything done, release the window
    if config.ARGS.display:
        cv2.destroyAllWindows()

    logging.info("End of Script")

    return


if __name__ == "__main__":
    main()