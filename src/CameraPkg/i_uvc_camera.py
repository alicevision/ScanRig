from abc import ABC, abstractmethod

class IUvcCamera(ABC):

    # ------------------- Control Methods ----------------- #

    @abstractmethod
    def getLastFrame(self):
        """Returns last frame data"""
        pass

    @abstractmethod
    def saveLastFrame(self):
        """Save last frame to a file"""
        pass

    # ------------------- Getters & Setters ----------------- #
    
    @abstractmethod
    def setDefaultSettings(self):
        """Set all setters to their respective defaults"""
        pass

    @abstractmethod
    def capabilities(self):
        """Returns the resolution & encoding capabilities of the camera"""
        pass

    @property
    @abstractmethod
    def format(self):
        """Returns the current capability used"""
        pass

    @format.setter
    @abstractmethod
    def setFormat(self, capability):
        """Set width, height & encoding"""
        pass

    @property
    @abstractmethod
    def brightness(self):
        pass

    @brightness.setter
    @abstractmethod
    def setBrightness(self, value):
        """Change camera brightness, from 0 to 10 000"""
        pass

    @property
    @abstractmethod
    def contrast(self):
        pass

    @contrast.setter
    @abstractmethod
    def setContrast(self, value):
        """Change camera constrast, from ? to ?"""
        pass

    @property
    @abstractmethod
    def saturation(self):
        pass
    
    @saturation.setter
    @abstractmethod
    def setSaturation(self, value):
        """Change camera saturation, from ? to ?"""
        pass

    @property
    @abstractmethod
    def whiteBalance(self):
        pass

    @whiteBalance.setter
    @abstractmethod
    def setWhiteBalance(self, value):
        """Change camera white balance, from ? to ?"""
        pass

    @property
    @abstractmethod
    def gamma(self):
        pass

    @gamma.setter
    @abstractmethod
    def setGamma(self, value):
        """Change camera gamma, from ? to ?"""
        pass

    @property
    @abstractmethod
    def gain(self):
        pass

    @gain.setter
    @abstractmethod
    def setGain(self, value):
        """Change camera gain, from ? to ?"""
        pass

    @property
    @abstractmethod
    def sharpness(self):
        pass

    @sharpness.setter
    @abstractmethod
    def setSharpness(self, value):
        """Change camera sharpness, from ? to ?"""
        pass

    @property
    @abstractmethod
    def exposure(self):
        pass

    @exposure.setter
    @abstractmethod
    def setExposure(self, value):
        """Change camera exposure, from ? to ?"""
        pass
