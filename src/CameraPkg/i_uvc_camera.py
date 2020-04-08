from abc import ABC, abstractmethod
from enum import Enum, auto

class CameraSetting(Enum):
    _UNKNOWN = auto()
    AUTO_WHITE_BALANCE = auto()
    AUTO_EXPOSURE = auto()
    AUTO_ISO = auto()
    BRIGHTNESS = auto()
    CONTRAST = auto()
    EXPOSURE = auto()
    ENABLE_HDR = auto()
    ENABLE_STABILIZATION = auto()
    GAMMA = auto()
    HUE = auto()
    ISO = auto()
    SATURATION = auto()
    SHARPNESS = auto()
    WHITE_BALANCE  = auto()


class IUvcCamera(ABC):

    @abstractmethod
    def getCameraId(self):
        """Returns the camera ID"""
        pass

    @abstractmethod
    def getSupportedFormats(self):
        """Returns the available formats for this device"""
        pass

    @abstractmethod
    def setFormat(self, form):
        """Set current width & height"""
        pass

    @abstractmethod
    def getFormat(self):
        """Returns the current capability used"""
        pass


    @abstractmethod
    def getSupportedSettings(self):
        """Returns the available settings for this device"""
        pass

    @abstractmethod
    def setSetting(self, setting, value):
        """Set a specific setting"""
        pass  

    @abstractmethod
    def getSetting(self, setting):
        """Returns the value of a specific setting"""
        pass  


    @abstractmethod
    def setSaveDirectory(self, path):
        """Set the saving directory"""
        pass  

    @abstractmethod
    def saveLastFrame(self):
        """Save the frame into the specified directory"""
        pass  

    @abstractmethod
    def getLastFrame(self):
        """Returns the last frame taken"""
        pass  