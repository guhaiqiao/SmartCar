from PyQt5 import QtWidgets, uic, QtCore, QtGui
import os
import serial
# import time
# import threading
import sys

path = os.getcwd()
File = path + os.sep + 'pc2.ui'
print(File)
Ui_MainWindow, QtBaseClass = uic.loadUiType(File)
# 后期UI界面文字字体及颜色修改
_translate = QtCore.QCoreApplication.translate
traffic_info = ''


class ErrorInfo(QtWidgets.QMessageBox):
    def __init__(self, info=''):
        QtWidgets.QMessageBox.__init__(self)
        self.info = info

    def display(self):
        self.information(self, '提示', self.info, self.Close)


class MainUi(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.init_Ui()

    def init_Ui(self):
        self.Timer = QtCore.QTimer()  # 计时器
        self.second = 0  # 初始化计时器秒数
        self.Timer.timeout.connect(self.timeout)
        self.port = ''
        self.team_name = ''
        self.score = '0'

        self.actionsave.triggered.connect(self.save)
        self.pushButton_start.clicked.connect(self.start)
        self.pushButton_pause.clicked.connect(self.pause)
        self.pushButton_end.clicked.connect(self.end)
        self.pushButton_file.clicked.connect(self.fileRead)
        self.pushButton_connect.clicked.connect(self.port_connect)
        self.PortChoice.activated[str].connect(self.onActivated)
        self.Team.textChanged[str].connect(self.onChanged)
        self.DrawMap()
        self.show()

    def start(self):
        # self.ser.open()  # 打开串口
        if self.team_name == '':
            WrongInfo = ErrorInfo('请先输入队名')
            WrongInfo.display()
            return
        self.Timer.start(10)
        self.score = 0

    def pause(self):
        self.Timer.stop()

    def end(self):
        self.Timer.stop()
        self.ser.close()
        self.score = self.time_now

    def onActivated(self, text):  # 选择串口（下拉栏）
        self.port = text

    def onChanged(self, text):  # 队名输入
        self.team_name = text
        print(self.team_name)

    def port_connect(self):
        if self.port == '':
            WrongInfo = ErrorInfo('请先选择端口')
            WrongInfo.display()
            # QtWidgets.QMessageBox.information(
                # self, '提示', '请先选择端口', QtWidgets.QMessageBox.Close)
            return
        self.ser = serial.Serial()
        self.ser.port = self.port
        print('connect')

    def fileRead(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, '请选择载入的路况', 'D:\Computer\AST\SmartCar\SmartCar\gui', 'Document ( *.txt)')
        if fname[0]:
            f = open(fname[0], 'r')
            with f:
                global traffic_info
                traffic_info = f.read()
                print(traffic_info)

    def timeout(self):
        self.second += 0.01
        self.sec = int(self.second * 10) / 10
        self.time_now = str(self.sec)
        self.TimeCounter.display(self.time_now)  # 显示时间
        self.DrawMap()

    def save(self):
        score = open('score.txt', 'a')
        score.write(self.team_name + ' ' + self.score + '\n')

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, '提示',
            "你竟然要退出？", QtWidgets.QMessageBox.Yes |
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def DrawMap(self):
        scene = QtWidgets.QGraphicsScene()
        scene.clear()
        self.Map.setScene(scene)
        pen = QtGui.QPen(QtCore.Qt.green)
        scene.addLine(0, 0, 0, 200, pen)
        scene.addLine(0, 0, 100, 200, pen)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    ex = MainUi()
    sys.exit(app.exec_())
