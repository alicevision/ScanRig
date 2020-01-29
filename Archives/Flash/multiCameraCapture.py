#------------------------- IMPORTS
import numpy as np
import cv2

import os
import argparse
import logging

#------------------------- LOGGING
log_levels = {
    0: logging.CRITICAL,
    1: logging.ERROR,
    2: logging.WARN,
    3: logging.INFO,
    4: logging.DEBUG,
}


#------------------------- ARGUMENTS PARSING
parser = argparse.ArgumentParser(description='Display video stream')
parser.add_argument('-o', '--output', metavar='Output folder', type=str,
                    default='',
                    help='')
parser.add_argument('-e', '--extension', metavar='Output file format/extention', type=str,
                    default='png',
                    help='')
parser.add_argument('-c', '--cameras', metavar='Cameras Indexes', type=int, nargs='+',
                    default=[0],
                    help='')
parser.add_argument('-d', '--display', metavar='Display window', type=bool,
                    default=True,
                    help='')
parser.add_argument('-s', '--sleep', metavar='Display sleep time (ms)', type=int,
                    default=1,
                    help='')
parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=3,
                    help="Verbosity (between 1-4 occurrences with more leading to more "
                         "verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, "
                         "DEBUG=4")

args = parser.parse_args()
logging.basicConfig(level=log_levels[args.verbosity])

if args.output and not os.path.exists(args.output):
    os.mkdir(args.output)

logging.info("Args: " + str(args))
logging.info("Press 'esc' to exit.")


#------------------------- SETTINGS FUNCTIONS
def setAttributes(cap):
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4208)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 3120)
    cap.set(cv2.CAP_PROP_BRIGHTNESS, 0)
    cap.set(cv2.CAP_PROP_CONTRAST, 0)
    cap.set(cv2.CAP_PROP_SATURATION, 32)
    cap.set(cv2.CAP_PROP_WB_TEMPERATURE, 4500) # From 0 to 10 000
    cap.set(cv2.CAP_PROP_AUTO_WB, 0) # Disable auto-white balance
    cap.set(cv2.CAP_PROP_GAMMA, 220)
    cap.set(cv2.CAP_PROP_GAIN, 0) # From 0 to 100
    cap.set(cv2.CAP_PROP_SHARPNESS, 0)
    cap.set(cv2.CAP_PROP_EXPOSURE, 103) # From 0 to 10 000
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1) # Disable auto-exposure

    return

def getAttributes(cap):
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
    gain = cap.get(cv2.CAP_PROP_GAIN)
    gamma = cap.get(cv2.CAP_PROP_GAMMA)
    brightness = cap.get(cv2.CAP_PROP_BRIGHTNESS)
    contrast = cap.get(cv2.CAP_PROP_CONTRAST)
    saturation = cap.get(cv2.CAP_PROP_SATURATION)
    sharpness = cap.get(cv2.CAP_PROP_SHARPNESS)
    fps = cap.get(cv2.CAP_PROP_FPS)
    wb = cap.get(cv2.CAP_PROP_WB_TEMPERATURE)
    logging.info(f'width={width}, height={height}, fps={fps}, exposure={exposure}, gain={gain}, wb={wb}, bright{brightness}, contrast{contrast}, sat{saturation}, sharp{sharpness}')
    logging.info(f'Backend = {cap.get(cv2.CAP_PROP_BACKEND)}')

    return


def initCamSettings():
    cameraApiID = 0
    for cameraIndex in args.cameras:
        cap = cv2.VideoCapture()
        v = cap.open(cameraApiID + cameraIndex, apiPreference=cv2.CAP_V4L2)
        if not v:
            logging.warning("Skip invalid stream ID {}".format(cameraIndex))
            cap.release()
            continue

        setAttributes(cap)

        ret, frame = cap.read() # Read a frame seems to be required to make it work
        cap.release()

    return



#------------------------- SCRIPT

captureDevices = []
cameraApiID = 0

frameNumber = 0
capFrame = 0

initCamSettings() # Initialize camera settings (open/close cameras once seems to be required)

# Initialize every camera
for cameraIndex in args.cameras:
    cap = cv2.VideoCapture()

    v = cap.open(cameraApiID + cameraIndex, apiPreference=cv2.CAP_V4L2)
    if not v:
        logging.warning("Skip invalid stream ID {}".format(cameraIndex))
        cap.release()
        continue

    setAttributes(cap)
    getAttributes(cap)

    captureDevices.append((cameraIndex, cap))

# Main loop
running = True
while(running):
    frames = []
    frameIdx = []
    k = cv2.waitKey(1)
    for idx, cap in captureDevices:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            continue
        frames.append(frame)
        frameIdx.append(idx)
    
    if args.display:
        VERTICAL = 0
        HORIZONTAL = 1
        vis = np.concatenate(frames, axis=VERTICAL)
        vis = cv2.resize(vis, None, fx=0.1, fy=0.1, interpolation=cv2.INTER_AREA)
        cv2.imshow('ScanRig', vis)
        
    if k == 27: #ECHAP
        running = False
        break

    if k == 32: #ESPACE
        for idx, img in zip(frameIdx, frames):
            outFilepath = f'cam{idx}_{capFrame:06d}.{args.extension}'
            logging.info(f'Writting file={outFilepath}')
            cv2.imwrite(outFilepath, img)
        capFrame += 1

    if args.output:
        for idx, img in zip(frameIdx, frames):
            outFilepath = f'{args.output}/cam{idx}_{capFrame:06d}.{args.extension}'
            logging.info(f'Writting file={outFilepath}')
            cv2.imwrite(outFilepath, img)
        capFrame += 1
    else:
        logging.info(f"frame {frameNumber}")

    frameNumber += 1

# When everything done, release the capture devices
for idx, cap in captureDevices:
    cap.release()


# When everything done, release the window
if args.display:
    cv2.destroyAllWindows()