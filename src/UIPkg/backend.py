from PySide2 import QtWidgets
from PySide2.QtCore import QObject, Slot, Property

class Backend(QObject):
    def __init__(self, parent=None):
        super(Backend, self).__init__(parent)
