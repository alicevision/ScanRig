from abc import ABC, abstractmethod
from enum import Enum, auto

class CameraSetting(Enum):
    """Enum for the Camera Settings."""
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
    """Interface describing UVC Cameras implementations."""
    @abstractmethod
    def GetCameraId(self):
        """Getter: camera ID"""
        pass

    @abstractmethod
    def GetCameraName(self):
        """Getter: camera name"""
        pass

    @abstractmethod
    def GetSupportedFormats(self):
        """Getter: available formats for this device"""
        pass

    @abstractmethod
    def SetFormat(self, form):
        """Setter: current width & height"""
        pass

    @abstractmethod
    def GetFormat(self):
        """Getter: current capability used"""
        pass


    @abstractmethod
    def GetSupportedSettings(self):
        """Getter: available settings for this device"""
        pass

    @abstractmethod
    def SetSetting(self, setting, value):
        """Setter: a specific setting"""
        pass  

    @abstractmethod
    def GetSetting(self, setting):
        """Getter: value of a specific setting"""
        pass  


    @abstractmethod
    def SetSaveDirectory(self, path):
        """Setter: the saving directory"""
        pass  

    @abstractmethod
    def SaveLastFrame(self):
        """Method to save the frame into the specified directory"""
        pass  

    @abstractmethod
    def GetLastFrame(self):
        """Getter: last frame taken"""
        pass  