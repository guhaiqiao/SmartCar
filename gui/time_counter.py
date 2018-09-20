# 定时器模块
from PyQt5 import QtCore
# import os
import time
import threading


# class TimeCounter(QtCore.Qtime):
#     def __init__(self):
#         QtCore.Qtime.__init__(self)
#         self.second = 0

#     def time_count(self):
#         self.second += 0.1
#         self.sec = str(int(self.second * 10) / 10)


class Timer(QtCore.QTime):
    def __init__(self, mainwindow):
        QtCore.QTime.__init__(mainwindow)
        self.time_init = time.strftime('%H:%M:%S',
                                       time.localtime(time.time()))  # 初始化当前时间
        self.time_now = self.time_init

    def get_time(self):
        self.timenow = time.strftime('%H:%M:%S',
                                     time.localtime(time.time()))  # 获取现在时间
        return self.timenow


class TimerThread(threading.Thread):
    def __init__(self, func, args):
        threading.Thread.__init__(self)
        self.timer = Timer()
        self.func = func
        self.args = args
