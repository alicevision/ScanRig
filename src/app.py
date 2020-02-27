import sys
import threading
import time
from UIPkg.image_provider import ImageProvider
from UIPkg.palette import Palette
from backend import Backend

from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt, QCoreApplication
from PySide2.QtQml import QQmlApplicationEngine

class App():
    def __init__(self):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        sys_argv = sys.argv
        sys_argv += ['--style', 'fusion']
        app = QApplication(sys_argv)
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

        # Set up the application window
        engine = QQmlApplicationEngine()
        ctx = engine.rootContext()

        # Create a Backend object to communicate with QML
        self.backend = Backend()
        ctx.setContextProperty("backend", self.backend)
        ctx.setContextProperty("preview", self.backend.preview)
        ctx.setContextProperty("acquisition", self.backend.acquisition)
        ctx.setContextProperty("availableUvcCameras", self.backend.preview.previewDevices.availableUvcCameras())

        engine.addImageProvider("imageProvider", self.backend.preview.imageProvider)

        # Apply palette
        darkPalette = Palette(engine)
        
        # Run app
        engine.load("UIPkg/App.qml")
        sys.exit(app.exec_())