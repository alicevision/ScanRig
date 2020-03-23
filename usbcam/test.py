import usbcam

myList = usbcam.GetDevicesList()

print(myList[0].number)

capManager = usbcam.CaptureManager([myList[0].number])

print(capManager)

# cam0 = capManager.GetCam(0)
