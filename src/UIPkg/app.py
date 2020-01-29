#!/usr/bin/env python
# -*- conding: utf-8 -*-

import sys
from . import camera_provider
from . import backend
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt, QUrl, QCoreApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtQuick import QQuickView

class App():
    def __init__(self):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        app = QApplication()
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

        # Set up the application window
        engine = QQmlApplicationEngine()
        ctx = engine.rootContext()

        # Add objects
        model = backend.Backend()
        ctx.setContextProperty("backend", model)
        cameraProvider = camera_provider.CameraProvider()
        engine.addImageProvider("cameraProvider", cameraProvider)
        engine.load("UIPkg/App.qml")

        # Run app
        sys.exit(app.exec_())
