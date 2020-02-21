import usbcam

myList = usbcam.GetDevicesList()

print(myList[0].name)
