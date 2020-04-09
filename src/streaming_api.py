import argparse
from enum import Enum, auto

class StreamingAPI(Enum):
    USBCAM = auto()
    OPENCV = auto()

#------------------------- CONFIG FUNCTION
def getStreamingAPI():
    parser = argparse.ArgumentParser(description='ScanRig App')
    parser.add_argument('-a', '--api', metavar='Backend API used for streaming', type=str,
                        default='usbcam', choices=['usbcam', 'opencv'],
                        help='Name of the Backend API used for streaming. Default: "usbcam". Can be "usbcam" or "opencv".')

    args = parser.parse_args()

    if args.api == 'usbcam':
        return StreamingAPI.USBCAM
    elif args.api == 'opencv':
        return StreamingAPI.OPENCV