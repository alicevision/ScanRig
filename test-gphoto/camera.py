import gphoto2 as gp

context = gp.Context()
camera = gp.Camera()
camera.init(context)
text = camera.get_summary(context)
print('Summary')
print('=======')
print(str(text))
camera.exit(context)
