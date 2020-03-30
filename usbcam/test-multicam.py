import usbcam
import cv2
import numpy as np

# Create camera
myList = usbcam.GetDevicesList()
print(myList[1].name)
myCam1 = usbcam.CreateCamera(1)
myCam2 = usbcam.CreateCamera(2)
myCam3 = usbcam.CreateCamera(3)

# Change camera settings
formats = myCam1.GetSupportedFormats()
myCam1.SetFormat(formats[12])
myCam2.SetFormat(formats[12])
myCam3.SetFormat(formats[12])

# Preview camera
i = 0
while(i < 30):
    i = i + 1
    myCam1.SaveLastFrame()
    myCam2.SaveLastFrame()
    myCam3.SaveLastFrame()
