import gphoto2 as gp

context = gp.Context()
camera = gp.Camera()
camera.init(context)
text = camera.get_summary(context)

# TODO adapt this code https://github.com/jim-easterbrook/python-gphoto2/blob/master/examples/camera-config-gui.py

config = camera.get_config()

for child in config.get_children():
    print('=======')
    print('--- ' + child.get_label() + ' ---')
    for prop in child.get_children():
        print(prop.get_label())
        if (prop.get_label() == 'Color Temperature'):
            prop.set_value('2500')
    
print('Summary')
print('=======')
print(str(text))

camera.set_config(config)

camera.exit(context)
