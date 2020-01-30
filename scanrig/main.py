#------------------------- IMPORTS
import numpy as np
import cv2, time, logging

import config
import CameraPkg
from MoteurPkg.SerialManagement import availablePorts, serialWrite, SerialReader, selectPort

#------------------------- SCRIPT

def main():
    GLOBAL_RUNNING = [True]

    # Get arguments
    args = config.config()

    # Initialize arduino
    arduinoSer = selectPort(115200)
    # Init custom Serial reader to handle readLine correctly
    serialReader = SerialReader(arduinoSer)

    # Create devices list
    captureDevices = CameraPkg.capture_device_list.CaptureDeviceList()

    # Initialize every camera
    for index in args.cameras:
        captureDevices.addDevice(index)
    captureDevices.setAllAttributesToDevices() # Give to devices the default settings
    captureDevices.getAllAttributes()

    # Initialize and start saving thread
    savingThread = CameraPkg.saving.SaveWatcher(GLOBAL_RUNNING, captureDevices.savingFrames, args)
    savingThread.start()

    # Check if cameras are running
    if not captureDevices.isEmpty():
        # Give the motor instructions - direction,totalAngle,stepAngle,transition,time
        time.sleep(4)
        print("is open ? ", arduinoSer.is_open)
        serialReader.clearBuffer()
        serialWrite(arduinoSer, "captureFull:1,360,15,45,45")
        # Read frame
        captureDevices.grabFrames()
        captureDevices.retrieveFrames()
    else:    
        GLOBAL_RUNNING[0] = False

    # Main loop
    while(GLOBAL_RUNNING[0]):

        line = serialReader.readline()
        # While the motor is rotating (before to arrive to a step angle)
        # while(line == b' '):
        #     print("inside while", line)
        #     line = serialReader.readline()
        #     time.sleep(0.01)

        # When the motor reaches the step angle
        if line[:9] == b'Capture\r':
            # Read frame
            captureDevices.grabFrames()
            captureDevices.retrieveFrames()

            # Send frames to the saving buffer
            captureDevices.saveFrames()

        # When the motor reaches the end    
        elif line[:7] == b'Success' :
            print("When success: ", line)
            GLOBAL_RUNNING[0] = False

        # If there is an error with the motor, we stop the loop
        elif line != b' ':
            print('line : ', line)
            print(line[:3])



    # Wait the end of saving thread
    savingThread.join()

    # When everything done, release the capture devices
    captureDevices.stopDevices()

    # # Stop the engine
    # serialWrite(arduinoSer, "stop:")

    logging.info("End of Script")

    return


if __name__ == "__main__":
    main()