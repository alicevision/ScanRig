import usbcam
import cv2
import numpy as np

# Create camera
myList = usbcam.GetDevicesList()
print(myList[0].name)
myCam0 = usbcam.CreateCamera(0)

# Manipulate camera
frame = myCam0.GetLastFrame()
cvFrame = np.array(frame, copy=False)

cv2.imshow('Example', cvFrame)

cv2.waitKey(0)
cv2.destroyAllWindows()
