from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
import os

path = os.getcwd()
File = path + os.sep + "gui" + os.sep + "pc.ui"
# print(File)


class Surface(QtWidgets.QDialog):
    def __init__(self, *args):
        super(Surface, self).__init__(*args)
        loadUi('D:/VS-CODE/python/upper_monitor/SmartCar.ui', self)
        self.pushButtonStart.clicked.connect(self.slotStart)
        self.pushButtonEnd.clicked.connect(self.slotQuit)

    def slotStart(self):
        self.accept()

    def slotQuit(self):
        self.reject()
