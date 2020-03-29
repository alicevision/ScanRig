import usbcam
import cv2
import numpy as np

# Create camera
myList = usbcam.GetDevicesList()
print(myList[0].name)
myCam0 = usbcam.CreateCamera(0)

# Manipulate camera
while(True):
    frame = np.array(myCam0.GetLastFrame(), copy=False)
    cv2.imshow('Example', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
