import sys
import threading
from UIPkg.camera_provider import CameraProvider
from UIPkg.backend import Backend
from acquisition import Acquisition

from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt, QCoreApplication
from PySide2.QtQml import QQmlApplicationEngine

class App():
    def __init__(self):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        app = QApplication()
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

        # Set up the application window
        engine = QQmlApplicationEngine()
        ctx = engine.rootContext()

        # Add qml objects
        backend = Backend()
        ctx.setContextProperty("backend", backend)

        self.acquisition = Acquisition()
        cameraProvider = CameraProvider(self.acquisition)
        engine.addImageProvider("cameraProvider", cameraProvider)
        ctx.setContextProperty("cameraProvider", cameraProvider)

        # Update cameras on another thread
        t = threading.Thread(target=self.updateCameras)
        t.start()
        
        # Run app
        engine.load("UIPkg/App.qml")
        sys.exit(app.exec_())

    def updateCameras(self):
        while(True):
            self.acquisition.captureDevices.grabFrames()
            self.acquisition.captureDevices.retrieveFrames()

    
