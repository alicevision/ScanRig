import cv2, logging

cameraSettingsList = {
    "width" : 4208,
    "height" : 3120,
    "brightness" : 0,
    "contrast" : 0,
    "saturation" : 32,
    "tempWB" : 4500, # From 0 to 10 000
    "autoWB" : 0,
    "gamma" : 220,
    "gain" : 0, # From 0 to 100
    "sharpness" : 0,
    "exposure" : 817, # From 0 to 10 000
    "autoExposure" : 1
}


def setAttributes(cap):
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('U','Y','V','Y'))
    cap.set(cv2.CAP_PROP_CONVERT_RGB, False)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cameraSettingsList.get("width"))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cameraSettingsList.get("height"))
    cap.set(cv2.CAP_PROP_BRIGHTNESS, cameraSettingsList.get("brightness"))
    cap.set(cv2.CAP_PROP_CONTRAST, cameraSettingsList.get("contrast"))
    cap.set(cv2.CAP_PROP_SATURATION, cameraSettingsList.get("saturation"))
    cap.set(cv2.CAP_PROP_WB_TEMPERATURE, cameraSettingsList.get("tempWB")) 
    cap.set(cv2.CAP_PROP_AUTO_WB, cameraSettingsList.get("autoWB"))
    cap.set(cv2.CAP_PROP_GAMMA, cameraSettingsList.get("gamma"))
    cap.set(cv2.CAP_PROP_GAIN, cameraSettingsList.get("gain")) 
    cap.set(cv2.CAP_PROP_SHARPNESS, cameraSettingsList.get("sharpness"))
    cap.set(cv2.CAP_PROP_EXPOSURE, cameraSettingsList.get("exposure")) 
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, cameraSettingsList.get("autoExposure"))

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


def initCamSettings(cameraIndex):
    cap = cv2.VideoCapture()
    v = cap.open(cameraIndex, apiPreference=cv2.CAP_V4L2)
    if not v:
        logging.warning("Skip invalid stream ID {}".format(cameraIndex))
        cap.release()
        return

    setAttributes(cap)

    status, frame = cap.read() # Read a frame seems to be required to make it work
    cap.release()

    return