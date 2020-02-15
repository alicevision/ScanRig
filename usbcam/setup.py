from distutils.core import setup, Extension, DEBUG

sfc_module = Extension('usbcam', sources = ['src/camera.cpp'])

setup(name = 'usbcam', version = '1.0',
    description = 'Python Package with usbcam C++ extension',
    ext_modules = [sfc_module])
