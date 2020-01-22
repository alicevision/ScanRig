#------------------------- IMPORTS
import numpy as np
import cv2, time, logging
import queue

import config
import CameraPKG


#------------------------- SCRIPT

def main():
    captureDevices = []
    GLOBAL_RUNNING = [True]
    savingFrames = queue.Queue()

    frameNumber = 0

    # Get arguments
    args = config.config()

    # Setup cameras (a first time is necessary)
    for index in args.cameras:
        CameraPKG.settings.initCamSettings(index) # Initialize camera settings (open/close cameras once seems to be required)

    # Initialize every camera
    for index in args.cameras:
        cam = CameraPKG.device.CaptureDevice(index, savingFrames)
        if cam.capture.isOpened():
            captureDevices.append(cam)

    # Initialize and start saving thread
    savingThread = CameraPKG.saving.SaveWatcher(GLOBAL_RUNNING, savingFrames, args)
    savingThread.start()

    # Check if cameras are running
    if not captureDevices:
        GLOBAL_RUNNING[0] = False

    # Main loop
    while(GLOBAL_RUNNING[0]):
        if frameNumber >= 70:
            GLOBAL_RUNNING[0] = False

        for cam in captureDevices:
            cam.grabFrame()

        for cam in captureDevices:
            cam.retrieveFrame()

        print("Motor ACTION")

        # THIS IS A TEST
        if frameNumber % 15 == 0:
            for cam in captureDevices:
                cam.saveFrame()

        time.sleep(0.04)

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