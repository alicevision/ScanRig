import threading
import cv2, time

import cameraSettings
import VideoStream
import SaveWatcher
import config


if __name__ == '__main__':
    cameraThreads = []
    counter = 0

    config.config() # Deal with arguments and logging

    #--------------------------------------- Creating threads
    for cameraIndex in config.args.cameras:
        cameraSettings.initCamSettings(cameraIndex)
        camThread = VideoStream.VideoStream(cameraIndex)
        cameraThreads.append(camThread)

    savingThread = SaveWatcher.SaveWatcher()

    #--------------------------------------- Starting threads
    for cam in cameraThreads:
        cam.start()

    savingThread.start()

    #--------------------------------------- Main loop
    camerasRunning = True
    for cam in cameraThreads:
        camerasRunning = camerasRunning and cam.running # If there's no camera, change to False

    if not camerasRunning:
        config.GLOBAL_RUNNING = False # If there's no camera, the GLOBAL_RUNNING boolean change to False

    while camerasRunning:
        #---------------- JUST A TEST !!!
        if counter % 20 == 0:
            for cam in cameraThreads:
                cam.toSave = True
        if counter >= 250:
            config.GLOBAL_RUNNING = False # Permits to stop all the threads (because they are based on this global var)

        counter+= 1

        # Recheck each time if cameras are all running
        for cam in cameraThreads:
            camerasRunning = camerasRunning and cam.running

        time.sleep(0.04)

    #--------------------------------------- Join threads
    for cam in cameraThreads:
        cam.join()
    
    savingThread.join()

    #--------------------------------------- Exit program
    cv2.destroyAllWindows()
    print('Destroyed everything')