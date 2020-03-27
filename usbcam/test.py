import usbcam

# Create camera
myList = usbcam.GetDevicesList()
print(myList[0].name)
myCam0 = usbcam.CreateCamera(0)

# Manipulate camera
myCam0.SetSetting(usbcam.CameraSetting.Brightness, 10)
myCam0.SaveLastFrame()
myCam0.SetSetting(usbcam.CameraSetting.Brightness, 100)
myCam0.SaveLastFrame()
