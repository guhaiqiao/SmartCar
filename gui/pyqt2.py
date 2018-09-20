from PyQt5 import QtWidgets, uic, QtCore, QtGui
# import time_counter as tc
import os
import time
import threading
# import sys
path = os.getcwd()
File = path + os.sep + 'gui' + os.sep + 'pc.ui'
Ui_MainWindow, QtBaseClass = uic.loadUiType(File)
# 后期UI界面文字字体及颜色修改
_translate = QtCore.QCoreApplication.translate


class MainUi(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.time_displayer = QtCore.QTimer(self)  # 设置时钟
        time_display_thread = threading.Thread(
            target=self.time_display, args=())
        time_display_thread.start()

    def time_display(self):
        time_init = time.strftime(
            '%H:%M:%S', time.localtime(time.time()))
        self.TimeDisplay.display(time_init)
        self.time_displayer.start(1000)
        self.time_displayer.timeout.connect(self.time_show)

    def time_show(self):
        time_now = time.strftime(
            '%H:%M:%S', time.localtime(time.time()))
        self.TimeDisplay(time_now)
