from abc import ABC, abstractmethod
from enum import Enum, auto

class CameraSetting(Enum):
    Auto_White_Balance = auto()
    Auto_Exposure = auto()
    Auto_Iso = auto()
    Brightness = auto()
    Contrast = auto()
    Exposure = auto()
    Enable_HDR = auto()
    Enable_Stabilization = auto()
    Gamma = auto()
    Hue = auto()
    Iso = auto()
    Saturation = auto()
    Sharpness = auto()
    White_Balance  = auto()


class IUvcCamera(ABC):

    @abstractmethod
    def GetCameraId(self):
        """Returns the camera ID"""
        pass

    @abstractmethod
    def GetCameraName(self):
        """Returns the camera name"""
        pass

    @abstractmethod
    def GetSupportedFormats(self):
        """Returns the available formats for this device"""
        pass

    @abstractmethod
    def SetFormat(self, form):
        """Set current width & height"""
        pass

    @abstractmethod
    def GetFormat(self):
        """Returns the current capability used"""
        pass


    @abstractmethod
    def GetSupportedSettings(self):
        """Returns the available settings for this device"""
        pass

    @abstractmethod
    def SetSetting(self, setting, value):
        """Set a specific setting"""
        pass  

    @abstractmethod
    def GetSetting(self, setting):
        """Returns the value of a specific setting"""
        pass  


    @abstractmethod
    def SetSaveDirectory(self, path):
        """Set the saving directory"""
        pass  

    @abstractmethod
    def SaveLastFrame(self):
        """Save the frame into the specified directory"""
        pass  

    @abstractmethod
    def GetLastFrame(self):
        """Returns the last frame taken"""
        pass  