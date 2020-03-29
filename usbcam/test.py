import usbcam
import cv2
import numpy as np

# Create camera
myList = usbcam.GetDevicesList()
print(myList[0].name)
myCam0 = usbcam.CreateCamera(0)

# Change camera settings
formats = myCam0.GetSupportedFormats()
myCam0.SetFormat(formats[0])

settings = myCam0.GetSupportedSettings()
myCam0.SetSetting(usbcam.CameraSetting.Exposure, 200)
myCam0.SetSetting(usbcam.CameraSetting.White_Balance, 1000)

# Preview camera
while(True):
    buffer = np.array(myCam0.GetLastFrame(), copy=False)
    cv2.imshow('USBCam with OpenCv', cv2.imdecode(buffer, cv2.IMREAD_COLOR))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
