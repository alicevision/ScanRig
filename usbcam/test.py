import usbcam
import cv2

# Create camera
myList = usbcam.GetDevicesList()
print(myList[0].name)
myCam0 = usbcam.CreateCamera(0)

# Manipulate camera
frame = myCam0.SaveLastFrame()
print("here")
cv2.imshow('Example', frame.data)
