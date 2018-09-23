from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt
import os
import serial
import serial.tools.list_ports
# import time
import threading
import sys
import map_info as mp
import traffic_info as trf

path = os.getcwd() + os.sep + 'Upper Computer' + os.sep + 'Program'
GUI = path + os.sep + 'pc2.ui'
TRAFFIC = path + os.sep + 'traffic_test.dat'
MAP = path + os.sep + 'map_test.txt'

# print(GUI)
Ui_MainWindow, QtBaseClass = uic.loadUiType(GUI)
# 后期UI界面文字字体及颜色修改
_translate = QtCore.QCoreApplication.translate
traffic_info = ''


class Info(QtWidgets.QMessageBox):
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
        self.portlist = []
        self.team_name = ''
        self.score = '0'
        self.set_port_flag = False
        self.width = 881
        self.height = 631

        self.actionsave.triggered.connect(self.save)
        self.pushButton_start.clicked.connect(self.start)
        self.pushButton_start.setEnabled(False)
        self.pushButton_pause.clicked.connect(self.pause)
        self.pushButton_pause.setEnabled(False)
        self.pushButton_end.clicked.connect(self.end)
        self.pushButton_end.setEnabled(False)
        self.pushButton_file.clicked.connect(self.fileRead)
        self.pushButton_connect.clicked.connect(self.port_connect)
        self.pushButton_connect.setEnabled(False)

        self.PortChoice.addItem('')
        # self.PortChoice.addItem('COM2')
        self.PortWatch = threading.Thread(target=self.portWatch)
        self.PortWatch.setDaemon(True)
        self.PortWatch.start()
        self.PortChoice.activated[str].connect(self.onActivated)
        self.Team.textChanged[str].connect(self.onChanged)

        self.mapSet()
        self.trfSet()
        self.drawmap()
        self.show()

    def start(self):
        # self.ser.open()  # 打开串口
        print(self.pushButton_start.text())
        if self.pushButton_start.text() == '开始':
            # if self.team_name == '':
            #     WrongInfo = ErrorInfo('请先输入队名')
            #     WrongInfo.display()
            #     return
            self.Timer.start(10)
            self.score = 0
            self.pushButton_start.setEnabled(False)
            self.pushButton_pause.setEnabled(True)
            self.pushButton_end.setEnabled(True)

        elif self.pushButton_start.text() == '继续':
            self.Timer.start(10)
            self.pushButton_pause.setEnabled(True)
            self.pushButton_start.setEnabled(False)

        else:  # 清零操作
            self.second = 0
            self.TimeCounter.display('0')
            self.pushButton_start.setText('开始')
            self.pushButton_start.repaint()
            self.Team.setText('')
            global traffic_info
            traffic_info = ''

    def pause(self):
        self.Timer.stop()
        # self.pushButton_end.setEnabled(True)
        self.pushButton_start.setEnabled(True)
        self.pushButton_start.setText('继续')
        self.pushButton_pause.setEnabled(False)

    def end(self):
        self.Timer.stop()
        # self.ser.close()
        self.score = self.time_now
        self.pushButton_start.setText('清零')
        self.pushButton_start.repaint()
        self.pushButton_end.setEnabled(False)
        self.pushButton_start.setEnabled(True)
        self.pushButton_pause.setEnabled(False)

    def portWatch(self):
        while True:
            if self.portlist != serial.tools.list_ports.comports():
                self.portlist = serial.tools.list_ports.comports()
                if len(self.portlist) <= 0:
                    pass
                else:
                    self.PortChoice.addItem(str(self.portlist[0])[-5:-1])
            else:
                pass

    def onActivated(self, text):  # 选择串口（下拉栏）
        if (self.port == text):
            pass
        else:
            self.port = text
            self.pushButton_connect.setText('连接')
            if self.port != '':
                self.pushButton_connect.setEnabled(True)
            else:
                self.pushButton_connect.setEnabled(False)

    def onChanged(self, text):  # 队名输入
        self.team_name = text
        global traffic_info
        if self.team_name != '' and self.set_port_flag and traffic_info != '':
            self.pushButton_start.setEnabled(True)
            print(self.team_name)
        else:
            self.pushButton_start.setEnabled(False)

    def port_connect(self):
        # if self.port == '':
        #     WrongInfo = ErrorInfo('请先选择端口')
        #     WrongInfo.display()
        #     # QtWidgets.QMessageBox.information(
        #         # self, '提示', '请先选择端口', QtWidgets.QMessageBox.Close)
        #     return
        self.ser = serial.Serial()
        self.ser.port = self.port
        self.set_port_flag = True
        connect = Info('连接成功')
        connect.display()
        self.pushButton_connect.setText('已连接 ' + self.port)
        self.pushButton_connect.setEnabled(False)
        print('connect')

    def fileRead(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, '请选择载入的路况', 'D:\Computer\AST\SmartCar\SmartCar\gui',
            'Document ( *.txt)')
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
        reply = QtWidgets.QMessageBox.question(
            self, '提示', "你竟然要退出？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def mapsize(self):
        # while True:
        # if (self.width, self.height) != (self.Map.width,
        #                                     self.Map.height()):
        self.width = self.Map.width()
        self.height = self.Map.height()
            # print([self.width, self.height])
        # else:
            # pass

    def mapSet(self):
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.clear()
        self.Map.setScene(self.scene)
        self.pen1 = QtGui.QPen(
            Qt.white, 30, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        self.pen2 = QtGui.QPen(
            Qt.black, 3, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        self.brush = QtGui.QBrush(Qt.white)
        self.graph = mp.Graph()
        self.graph.read(MAP)
        self.x_max = max(self.graph.x)
        self.y_max = max(self.graph.y)
        self.circle_size = self.pen1.width() * 0.5

    def drawmap(self):
        self.scene.clear()
        self.x_scale = self.width / self.x_max * 9 / 10
        self.y_scale = self.height / self.y_max * 9 / 10
        for i in range(self.graph.point_num):
            # x = (self.graph.x[i]) * self.x_scale - self.circle_size / 2 + self.width / 35
            # y = (self.graph.y[i]) * self.y_scale - self.circle_size / 2 + self.width / 35
            # self.scene.addEllipse(
            #     x, y, self.circle_size, self.circle_size, self.pen1, self.brush)
            for j in range(self.graph.point_num):
                if self.graph.line[i][j] != 0:
                    x1 = self.graph.x[i] * self.x_scale + self.width / 35
                    y1 = self.graph.y[i] * self.y_scale + self.height / 35
                    x2 = self.graph.x[j] * self.x_scale + self.width / 35
                    y2 = self.graph.y[j] * self.y_scale + self.height / 35
                    self.scene.addLine(x1, y1, x2, y2, self.pen1)
        self.drawtrf()

        for i in range(self.graph.point_num):
            for j in range(self.graph.point_num):
                if self.graph.line[i][j] != 0:
                    x1 = self.graph.x[i] * self.x_scale + self.width / 35
                    y1 = self.graph.y[i] * self.y_scale + self.height / 35
                    x2 = self.graph.x[j] * self.x_scale + self.width / 35
                    y2 = self.graph.y[j] * self.y_scale + self.height / 35
                    self.scene.addLine(x1, y1, x2, y2, self.pen2)
        # scene.setBackgroundBrush(QPixmap("./test.jpg"))  #设置背景图

    def resizeEvent(self, QResizeEvent):
        self.mapsize()
        self.drawmap()

    def trfSet(self):
        self.traffic = trf.Traffic()
        self.traffic.read(TRAFFIC)
        self.pen = []
        self.color = [Qt.green, Qt.green, Qt.green, Qt.yellow, Qt.yellow, Qt.red, Qt.red, Qt.red]
        for item in self.color:
            self.pen.append(QtGui.QPen(item, 15, QtCore.Qt.SolidLine,  # 颜色数字
                              QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))

    def drawtrf(self):
        for i in range(self.traffic.point_num):
            for j in range(self.traffic.point_num):
                if self.traffic.line[i][j] != 0:
                    x1 = self.graph.x[i] * self.x_scale + self.width / 35
                    y1 = self.graph.y[i] * self.y_scale + self.height / 35
                    x2 = self.graph.x[j] * self.x_scale + self.width / 35
                    y2 = self.graph.y[j] * self.y_scale + self.height / 35
                    self.scene.addLine(
                        x1, y1, x2, y2, self.pen[self.traffic.line[i][j] - 1])

    # def showEvent(self):
    #     self.Map.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    ex = MainUi()
    sys.exit(app.exec_())
