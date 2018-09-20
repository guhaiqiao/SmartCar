from PyQt5 import QtWidgets, uic, QtCore, QtGui
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
        self.initiate()

    def time_counter_init(self):
        self.time_counter = QtCore.QTimer(self)  # 设置定时器
        self.TimeCounter.display('0')  # 初始化计时器
        self.time_counter.timeout.connect(self.time_count)
        self.second = 0

    def time_now_init(self):
        self.time_displayer = QtCore.QTimer(self)  # 设置时钟
        self.time_init = time.strftime(
            '%H:%M:%S', time.localtime(time.time()))
        self.TimeDisplay.display(self.time_init)
        self.time_displayer.start(1000)
        self.time_displayer.timeout.connect(self.time_display)

    def initiate(self):
        self.pushButton_start.clicked.connect(self.start)
        self.pushButton_pause.clicked.connect(self.pause)
        self.pushButton_end.clicked.connect(self.end)
        self.time_counter_threading = threading.Thread(
            target=self.time_counter_init, args=())
        self.time_now_threading = threading.Thread(
            target=self.time_now_init, args=())
        self.time_now_threading.start()

    def start(self):
        self.time_counter.start(100)  # 每秒执行一次
        self.time_counter_threading.start()

    def pause(self):
        self.time_counter.stop()

    def end(self):
        self.time_counter.stop()
        self.second = 0  # 刷新秒数
        self.TimeCounter.display('0')  # 重置时间

    def time_count(self):
        self.second += 0.1
        self.sec = str(int(self.second * 10) / 10)
        self.TimeCounter.display(self.sec)  # 显示时间

    def time_display(self):
        self.time_now = time.strftime(
            '%H:%M:%S', time.localtime(time.time()))
        self.TimeDisplay.display(self.time_now)
