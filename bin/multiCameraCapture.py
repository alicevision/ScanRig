import numpy as np
import cv2

import os
import argparse
import logging


log_levels = {
    0: logging.CRITICAL,
    1: logging.ERROR,
    2: logging.WARN,
    3: logging.INFO,
    4: logging.DEBUG,
}

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

print("Press 'q' to exit.")

if args.output and not os.path.exists(args.output):
    os.mkdir(args.output)

logging.info("Args: " + str(args))

captureDevices = []

cameraApiID = 0
for cameraIndex in args.cameras:
    cap = cv2.VideoCapture()
    v = cap.open(cameraApiID + cameraIndex)
    if not v:
        logging.warning("Skip invalid stream ID {}".format(cameraIndex))
        cap.release()
        continue

    width = cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4208)
    height = cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 3120)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    uid = cap.get(cv2.CAP_PROP_GUID)
    logging.info('uid={}, width={}, height={}, fps={}, frame count={}'.format(uid, width, height, fps, frameCount))

    captureDevices.append((cameraIndex, cap))

frameNumber = 0

running = True
while(running):
    frames = []
    frameIdx = []
    for idx, cap in captureDevices:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            continue
        frames.append(frame)
        frameIdx.append(idx)
        # height, width = frame.shape[:2]
        # print('width={}, height={}'.format(width, height))
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    if args.display:
        VERTICAL = 0
        HORIZONTAL = 1
        vis = np.concatenate(frames, axis=HORIZONTAL)
        # Display the resulting frame
        cv2.imshow('ScanRig', vis)
        if cv2.waitKey(args.sleep) & 0xFF == ord('q'):
            running = False
            break

    if args.output:
        for idx, img in zip(frameIdx, frames):
            outFilepath = '{outFolder}/cam{camId}_{frame:06d}.{ext}'.format(outFolder=args.output, camId=idx, frame=frameNumber, ext=args.extension)
            logging.info('Writting file={}'.format(outFilepath))
            cv2.imwrite(outFilepath, img)

    frameNumber += 1

# When everything done, release the capture devices
for idx, cap in captureDevices:
    cap.release()

# When everything done, release the window
if args.display:
    cv2.destroyAllWindows()

