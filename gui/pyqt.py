from PyQt5 import QtWidgets, uic, QtCore, QtGui
import os
import time
import sys
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
        self.pushButton_start.clicked.connect(self.start)
        self.pushButton_pause.clicked.connect(self.pause)
        self.pushButton_end.clicked.connect(self.end)
        self.timer = QtCore.QTimer(self)  # 设置定时器
        self.TimeCounter.display('0 s')  # 初始化计时器
        self.timer.timeout.connect(self.timeout)
        self.second = 0

    def start(self):
        self.timer.start(100)  # 每秒执行一次

    def pause(self):
        self.timer.stop()

    def end(self):
        self.timer.stop()
        self.second = 0  # 刷新秒数
        self.TimeCounter.display('0 s')  # 显示时间

    def timeout(self):
        # self.time_now = time.strftime(
        #     '%H:%M:%S', time.localtime(time.time()))
        self.second += 0.1
        self.sec = int(self.second * 10) / 10
        self.time_now = str(self.sec) + ' s'
        print(self.time_now)
        self.TimeCounter.display(self.time_now)  # 显示时间
