import usbcam
import cv2
import numpy as np

# Create camera
myList = usbcam.GetDevicesList()
print(myList[0].name)
myCam0 = usbcam.CreateCamera(0)

# Manipulate camera
while(True):
    buffer = np.array(myCam0.GetLastFrame(), dtype=np.ubyte, copy=False)
    frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    cv2.imshow('Example', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
