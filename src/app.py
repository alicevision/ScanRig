import sys
import threading
import time
import os
import logging
from CameraPkg.streaming_api import CHOSEN_STREAMING_API
from UIPkg.image_provider import ImageProvider
from UIPkg.palette import Palette
from backend import Backend
from utils import QmlInstantEngine

from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt, QCoreApplication, QUrl, Slot, QJsonValue, Property, qInstallMessageHandler, QtMsgType
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtGui import QIcon

# During development process
os.environ["MESHROOM_OUTPUT_QML_WARNINGS"] = "1"
os.environ["MESHROOM_INSTANT_CODING"] = "1"
logging.basicConfig(level=logging.DEBUG)


class MessageHandler(object):
    """
    MessageHandler that translates Qt logs to Python logging system.
    Also contains and filters a list of blacklisted QML warnings that end up in the
    standard error even when setOutputWarningsToStandardError is set to false on the engine.
    """

    outputQmlWarnings = bool(os.environ.get("MESHROOM_OUTPUT_QML_WARNINGS", False))

    logFunctions = {
        QtMsgType.QtDebugMsg: logging.debug,
        QtMsgType.QtWarningMsg: logging.warning,
        QtMsgType.QtInfoMsg: logging.info,
        QtMsgType.QtFatalMsg: logging.fatal,
        QtMsgType.QtCriticalMsg: logging.critical,
        QtMsgType.QtSystemMsg: logging.critical
    }

    # Warnings known to be inoffensive and related to QML but not silenced
    # even when 'MESHROOM_OUTPUT_QML_WARNINGS' is set to False
    qmlWarningsBlacklist = (
        'Failed to download scene at QUrl("")',
        'QVariant(Invalid) Please check your QParameters',
        'Texture will be invalid for this frame',
    )

    @classmethod
    def handler(cls, messageType, context, message):
        """ Message handler remapping Qt logs to Python logging system. """
        # discard blacklisted Qt messages related to QML when 'output qml warnings' is set to false
        if not cls.outputQmlWarnings and any(w in message for w in cls.qmlWarningsBlacklist):
            return
        MessageHandler.logFunctions[messageType](message)


class App():
    """Class used to initiate the Application instance."""

    def __init__(self):
        """App constructor"""
        self.streamingAPI = CHOSEN_STREAMING_API

        print(self.streamingAPI)

        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        sys_argv = sys.argv
        sys_argv += ['--style', 'fusion']
        app = QApplication(sys_argv)
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

        # Set up the application window
        pwd = os.path.dirname(__file__)
        qmlDir = os.path.join(pwd, "UIPkg")
        self.engine = QmlInstantEngine()
        self.engine.addFilesFromDirectory(qmlDir, recursive=True)
        self.engine.setWatching(os.environ.get("MESHROOM_INSTANT_CODING", False))

        # whether to output qml warnings to stderr (disable by default)
        self.engine.setOutputWarningsToStandardError(MessageHandler.outputQmlWarnings)
        qInstallMessageHandler(MessageHandler.handler)

        ctx = self.engine.rootContext()

        # Create a Backend object to communicate with QML
        self.backend = Backend()
        ctx.setContextProperty("backend", self.backend)
        ctx.setContextProperty("preview", self.backend.preview)
        ctx.setContextProperty("acquisition", self.backend.acquisition)

        self.engine.addImageProvider("imageProvider", self.backend.preview.imageProvider)

        # Apply palette
        darkPalette = Palette(self.engine)
        
        # Run app
        self.engine.load("UIPkg/App.qml")
        sys.exit(app.exec_())