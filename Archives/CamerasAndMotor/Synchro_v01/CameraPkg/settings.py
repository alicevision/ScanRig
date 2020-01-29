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
    "exposure" : 200, # From 0 to 10 000
    "autoExposure" : 1,
    "bufferSize" : 1
}

def changeBrightness(value):
    global cameraSettingsList
    cameraSettingsList["brightness"] = value
    return

def changeContrast(value):
    global cameraSettingsList
    cameraSettingsList["contrast"] = value
    return
    
def changeSaturation(value):
    global cameraSettingsList
    cameraSettingsList["saturation"] = value
    return

def changeTempWB(value):
    global cameraSettingsList
    cameraSettingsList["tempWB"] = value
    return

def changeGamma(value):
    global cameraSettingsList
    cameraSettingsList["gamma"] = value
    return

def changeGain(value):
    global cameraSettingsList
    cameraSettingsList["gain"] = value
    return

def changeSharpness(value):
    global cameraSettingsList
    cameraSettingsList["sharpness"] = value
    return

def changeExposure(value):
    global cameraSettingsList
    cameraSettingsList["exposure"] = value
    return


def setDefaultAttributes(cap):
    # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('U','Y','V','Y')) # To use only with the FSCAM_CU135
    # cap.set(cv2.CAP_PROP_CONVERT_RGB, False) # To use only with the FSCAM_CU135
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
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
    formatting = cap.get(cv2.CAP_PROP_FORMAT)
    logging.info(f'width={width}, height={height}, fps={fps}, exposure={exposure}, gain={gain}, wb={wb}, bright{brightness}, contrast{contrast}, sat{saturation}, sharp{sharpness}, format{formatting}')
    logging.info(f'Backend = {cap.get(cv2.CAP_PROP_BACKEND)}')

    return