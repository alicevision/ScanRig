import numpy as np
import os
import threading, logging, cv2
from .i_uvc_camera import CameraSetting, IUvcCamera

class OpencvCamera(IUvcCamera):
    """Class used for UVC Cameras working with the OpenCV API."""
    def __init__(self, id, saveDirectory):
        """OpencvCamera constructor.

        Args:
            id (int): ID of the camera.
            saveDirectory (str): Path used to store the images taken by this camera.
        """
        self.id = id
        (self.status, self.frame) = (None, None)
        self.frameCount = 0

        # Initialize settings for the camera
        self.settings = self.__initSettings()

        self.capture = cv2.VideoCapture()
        self.__start()
        self.formats = self.GetSupportedFormats()
        print(self.formats)
        self.SetFormat(self.formats[0])
        self.acquisitionFormat = self.formats[0]

        self.saveDirectory = saveDirectory
        self.SetSaveDirectory(saveDirectory)
        self.savingQueue = None

    
    def __del__(self):
        """OpencvCamera destructor."""
        self.__stop()
        print(f"Camera {self.id} is self-desctructed")



    def GetCameraId(self):
        """"Getter id

        Returns:
            int: ID of the camera.
        """
        return self.id

    def GetCameraName(self):
        """Method to return the camera name.

        Returns:
            str: Name of the camera.
        """
        return "UVC: " + str(self.id)

    def GetSupportedFormats(self):
        """Method to return supported resolutions/formats by the camera.

        Returns:
            [Object]: List of Object describing supported resolutions/formats.
        """
        formats = []
        toTest = [(4208, 3120), (4096, 2160), (3840, 2160), (2880, 2160), (1920, 1440), (1920, 1080), (1280, 960), (1280, 720), (640,480)]

        for (w,h) in toTest:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

            actualWidth = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            actualHeight = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

            if actualWidth == w and actualHeight == h:
                formats.append({"width": w, "height": h})

        return formats

    def SetFormat(self, form):
        """Method to set the current resolution/format.

        Args:
            form (Object): Object describing the resolution/format.
        """
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, form.get("width"))
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, form.get("height"))
        
        self.__fillBuffer()

    def GetFormat(self):
        """Method to return the current resolution/format.

        Returns:
            Object: Object describing the resolution/format.
        """
        w = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

        return {"width": int(w), "height": int(h)}

    def SetAcquisitionFormat(self, form):
        """Setter acquisitionFormat: resolution/format used during the acquisition only.

        Args:
            form (Object): Object describing the resolution/format.
        """
        self.acquisitionFormat = form

    def GetAcquisitionFormat(self):
        """Getter acquisitionFormat: resolution/format used during the acquisition only.

        Returns:
            Object: Object describing the acquisition resolution/format.
        """
        return self.acquisitionFormat

    def GetSupportedSettings(self):
        """Does nothing"""
        pass

    def SetSetting(self, setting, value):
        """Method to set a specific setting to the camera.

        Args:
            setting (CameraSetting): Enum representing a camera setting.
            value (int): Value to set.
        """
        if setting == CameraSetting.Brightness:
            self.capture.set(cv2.CAP_PROP_BRIGHTNESS, value)
        elif setting == CameraSetting.Contrast:
            self.capture.set(cv2.CAP_PROP_CONTRAST, value)
        elif setting == CameraSetting.Saturation:
            self.capture.set(cv2.CAP_PROP_SATURATION, value)
        elif setting == CameraSetting.White_Balance:
            self.capture.set(cv2.CAP_PROP_WB_TEMPERATURE, value)
        elif setting == CameraSetting.Auto_White_Balance:
            self.capture.set(cv2.CAP_PROP_AUTO_WB, value)
        elif setting == CameraSetting.Gamma:
            self.capture.set(cv2.CAP_PROP_GAMMA, value)
        elif setting == CameraSetting.Iso:
            self.capture.set(cv2.CAP_PROP_GAIN, value)
        elif setting == CameraSetting.Sharpness:
            self.capture.set(cv2.CAP_PROP_SHARPNESS, value)
        elif setting == CameraSetting.Exposure:
            self.capture.set(cv2.CAP_PROP_EXPOSURE, value)
        elif setting == CameraSetting.Auto_Exposure:
            self.capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, value)

    def GetSetting(self, setting):
        """Method to return the value of a specific setting.

        Args:
            setting (CameraSetting): Enum representing a camera setting.

        Returns:
            int: Value of the setting.
        """
        if setting == CameraSetting.Brightness:
            return self.capture.get(cv2.CAP_PROP_BRIGHTNESS)
        elif setting == CameraSetting.Contrast:
            return self.capture.get(cv2.CAP_PROP_CONTRAST)
        elif setting == CameraSetting.Saturation:
            return self.capture.get(cv2.CAP_PROP_SATURATION)
        elif setting == CameraSetting.White_Balance:
            return self.capture.get(cv2.CAP_PROP_WB_TEMPERATURE)
        elif setting == CameraSetting.Auto_White_Balance:
            return self.capture.get(cv2.CAP_PROP_AUTO_WB)
        elif setting == CameraSetting.Gamma:
            return self.capture.get(cv2.CAP_PROP_GAMMA)
        elif setting == CameraSetting.Iso:
            return self.capture.get(cv2.CAP_PROP_GAIN)
        elif setting == CameraSetting.Sharpness:
            return self.capture.get(cv2.CAP_PROP_SHARPNESS)
        elif setting == CameraSetting.Exposure:
            return self.capture.get(cv2.CAP_PROP_EXPOSURE)
        elif setting == CameraSetting.Auto_Exposure:
            return self.capture.get(cv2.CAP_PROP_AUTO_EXPOSURE)

    def SetSaveDirectory(self, rootDirectory):
        """Method to set the saving directory path to this camera.

        Args:
            rootDirectory (str): Path to the root directory where we want to save pictures.
        """
        path = os.path.join(rootDirectory, f"cam_{self.id}")
        os.makedirs(path, exist_ok=True)
        self.saveDirectory = path

    def SaveLastFrame(self):
        """Method to save the frame into the specified directory"""
        if self.savingQueue:
            self.savingQueue.put((self.id, self.frameCount, self.frame, self.saveDirectory))
            self.frameCount += 1

    def GetLastFrame(self):
        """Method to get and return the lasr frame.

        Returns:
            numpy.ndarray: Array describing the image.
        """
        self.status, self.frame = self.capture.read()
        print(type(self.frame))
        if not self.status:
            logging.warning("Image cannot be read")
        
        return self.frame


#---------- METHOD ONLY FOR THIS CLASS (NOT HERITED FROM INTERFACE)

    def SetSavingQueue(self, savingQueue):
        """Setter savingQueue: used to send frame into another where they are saved.

        Args:
            savingQueue (Queue): Queue where the frames are storred.
        """
        self.savingQueue = savingQueue

#---------- PRIVATE METHODS

    def __start(self):
        """Method to open the camera."""
        if not self.capture.isOpened():
            v = self.capture.open(self.id, apiPreference=cv2.CAP_V4L2)
            if v:
                self.__fillBuffer()
                self.__setAllSettings()

            else:
                logging.warning(f"Skip invalid stream ID {self.id}")
                self.__stop()

    def __stop(self):
        """Method to stop the camera."""
        self.capture.release()
        if not self.capture.isOpened():
            print(f"Device n°{self.id} closed")

    def __fillBuffer(self):
        """Method to fill the camera buffer."""
        for i in range(int(self.capture.get(cv2.CAP_PROP_BUFFERSIZE)) + 1):
            self.GetLastFrame()

    def __initSettings(self):
        """Method to init the default camera settings.

        Returns:
            Object: Object decribing the camera settings.
        """
        settings = {
            "width" : 1280,
            "height" : 720,
            "draftWidth" : 1280,
            "draftHeight" : 720,
            "brightness" : 0,
            "contrast" : 0,
            "saturation" : 32,
            "tempWB" : 4500, # From 0 to 10 000
            "autoWB" : 0,
            "gamma" : 220,
            "gain" : 0, # From 0 to 100
            "sharpness" : 0,
            "exposure" : 500, # From 0 to 10 000
            "autoExposure" : 1
        }
        return settings

    def __setAllSettings(self):
        """Method to set all the settings to the camera."""
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.get("width"))
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.get("height"))
        self.capture.set(cv2.CAP_PROP_BRIGHTNESS, self.settings.get("brightness"))
        self.capture.set(cv2.CAP_PROP_CONTRAST, self.settings.get("contrast"))
        self.capture.set(cv2.CAP_PROP_SATURATION, self.settings.get("saturation"))
        self.capture.set(cv2.CAP_PROP_WB_TEMPERATURE, self.settings.get("tempWB")) 
        self.capture.set(cv2.CAP_PROP_AUTO_WB, self.settings.get("autoWB"))
        self.capture.set(cv2.CAP_PROP_GAMMA, self.settings.get("gamma"))
        self.capture.set(cv2.CAP_PROP_GAIN, self.settings.get("gain")) 
        self.capture.set(cv2.CAP_PROP_SHARPNESS, self.settings.get("sharpness"))
        self.capture.set(cv2.CAP_PROP_EXPOSURE, self.settings.get("exposure")) 
        self.capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, self.settings.get("autoExposure"))

        self.__fillBuffer()

        return