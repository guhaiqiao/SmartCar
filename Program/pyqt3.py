from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt
import os
import serial
import serial.tools.list_ports
import time
# import threading
import sys
import map_info as mp
import traffic_info as trf

path1 = os.getcwd() + os.sep + 'Upper Computer' + os.sep + 'Program'
path = os.getcwd()
MAINWINDOW = path + os.sep + 'pc2.ui'
DIALOG_POINT = path + os.sep + 'dialog_point.ui'
DIALOG_SERIAL = path + os.sep + 'dialog_serial.ui'
# print(GUI)
TRAFFIC = path + os.sep + 'traffic' + os.sep + '0.dat'
MAP = path + os.sep + 'map_test.txt'
path_trf = path + os.sep + 'traffic'
# print(GUI)
Ui_MainWindow, QtBaseClass = uic.loadUiType(MAINWINDOW)
Ui_Dialog_Team, QtBaseClass_Dialog_Point = uic.loadUiType(DIALOG_POINT)
Ui_Dialog_Serial, QtBaseClass_Dialog_Serial = uic.loadUiType(DIALOG_SERIAL)
# 后期UI界面文字字体及颜色修改
_translate = QtCore.QCoreApplication.translate
traffic_info = ''


class Info(QtWidgets.QMessageBox):
    def __init__(self, info=''):
        QtWidgets.QMessageBox.__init__(self)
        self.info = info

    def display(self):
        self.information(self, '提示', self.info, self.Close)


class DialogUi_Point(Ui_Dialog_Team, QtBaseClass_Dialog_Point):
    def __init__(self):
        QtBaseClass_Dialog_Point.__init__(self)
        Ui_Dialog_Team.__init__(self)
        self.setupUi(self)
        self.start_point_flag = False
        self.end_point_flag = False
        self.pushButton.clicked.connect(self.get)
        self.pushButton.setEnabled(False)
        self.start_point.textChanged[str].connect(self.start_point_set)
        self.end_point.textChanged[str].connect(self.end_point_set)

    def start_point_set(self, text):
        if text != '':
            self.start_point_flag = True
        if self.start_point_flag and self.end_point_flag:
            self.pushButton.setEnabled(True)

    def end_point_set(self, text):
        if text != '':
            self.end_point_flag = True
        if self.start_point_flag and self.end_point_flag:
            self.pushButton.setEnabled(True)

    def get(self):
        self.s_point = int(self.start_point.text())
        self.e_point = int(self.end_point.text())
        self.accept()

    def get_point(self):
        return (self.s_point, self.e_point)


class DialogUi_Serial(Ui_Dialog_Serial, QtBaseClass_Dialog_Serial):
    def __init__(self):
        QtBaseClass_Dialog_Serial.__init__(self)
        Ui_Dialog_Serial.__init__(self)
        self.setupUi(self)
        self.load_ports()
        self.comboBox_ports.activated[str].connect(self.onActivated)
        self.pushButton_connect.clicked.connect(self.connect)
        # self.pushButton_connect.setEnabled(False)
        self.port = ''

    def load_ports(self):
        self.comboBox_ports.addItem('')
        self.portlist = serial.tools.list_ports.comports()
        if len(self.portlist) <= 0:
            pass
        else:
            for i in range(0, len(self.portlist)):
                self.comboBox_ports.addItem(str(self.portlist[i])[-5:-1])

    def onActivated(self, text):
        self.port = text
        # self.pushButton_connect.setEnabled(True)

    def connect(self):
        print('connect')
        self.accept()

    def get_port(self):
        return self.port


class MainUi(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.init_Ui()

    def init_Ui(self):
        self.Timer = QtCore.QTimer()  # 计时器
        self.second = 0  # 初始化计时器秒数
        self.time_stop = 0
        self.Timer.timeout.connect(self.timeout)
        self.port = ''
        self.portlist = []
        self.team_name = ''
        self.score = '0'
        self.team_flag = False
        self.point_flag = False
        self.port_flag = False
        self.traffic_flag = False
        self.x = 0  # 小车x坐标
        self.y = 0  # 小车y坐标

        self.pushButton_start.clicked.connect(self.start)
        self.pushButton_start.setEnabled(False)
        self.pushButton_end.clicked.connect(self.end)
        self.pushButton_end.setEnabled(False)
        self.pushButton_file.clicked.connect(self.fileRead)
        self.pushButton_connect.clicked.connect(self.port_connect)
        self.pushButton_point.clicked.connect(self.point_choose)
        self.load_team()
        self.Team.activated[str].connect(self.onActivated)
        # self.Team.textChanged[str].connect(self.onChanged)

        self.mapSet()
        self.trfSet()
        self.show()
        self.width = 783
        self.height = 511
        self.drawmap()

    def start(self):
        # self.ser.open()  # 打开串口
        print(self.pushButton_start.text())
        if self.pushButton_start.text() == '开始':
            self.drawmap()
            self.Timer.start(100)
            self.score = '0'
            self.time_init = time.perf_counter()
            self.pushButton_start.setText('暂停')
            self.pushButton_end.setEnabled(True)

        elif self.pushButton_start.text() == '暂停':
            self.Timer.stop()
            self.time_stop_init = time.perf_counter()
            self.pushButton_start.setText('继续')

        elif self.pushButton_start.text() == '继续':
            self.time_stop_finl = time.perf_counter()
            self.Timer.start(100)
            self.time_stop += self.time_stop_finl - self.time_stop_init
            print(self.time_stop)
            self.pushButton_start.setText('暂停')

        else:  # 清零操作
            self.second = 0
            self.time_stop = 0
            self.TimeCounter.display('0')
            self.pushButton_start.setText('开始')
            self.pushButton_file.setText('载入路况')
            self.pushButton_file.setEnabled(True)
            self.pushButton_point.setText('选择起终点')
            self.team_flag = False
            self.point_flag = False
            self.port_flag = False
            self.traffic_flag = False
            self.pushButton_start.setEnabled(False)
            self.traffic.read(TRAFFIC)
            self.x = 0
            self.y = 0
            self.start_point = ''
            self.end_point = ''
            self.drawmap()

    def end(self):
        self.Timer.stop()
        self.ser.close()
        self.score = self.time_display
        self.pushButton_start.setText('清零')
        self.pushButton_end.setEnabled(False)
        self.pushButton_start.setEnabled(True)
        self.pushButton_connect.setText('串口连接')
        self.pushButton_connect.setEnabled(True)
        self.save()

    def check_start(self):
        if self.team_flag and self.port_flag and self.traffic_flag and self.point_flag:
            self.pushButton_start.setEnabled(True)

    def onActivated(self, text):  # 选择队伍（下拉栏）
        if text != '选择队伍':
            self.team_name = text
            self.team_flag = True
            # print(self.team_name)
        self.check_start()

    def load_team(self):
        team_f = open(path + os.sep + 'team.txt', 'r')
        team_name = team_f.readlines()
        team_name_num = len(team_name)
        for i in range(0, team_name_num):
            if i != team_name_num - 1:
                team_name[i] = team_name[i][:-1]
            self.Team.addItem(team_name[i])
        # print(team_name)

    # def onChanged(self, text):  # 队名输入
    #     self.team_name = text
    #     global traffic_info
    #     if self.team_name != '' and self.port_flag and self.traffic_flag:
    #         self.pushButton_start.setEnabled(True)
    #         print(self.team_name)
    #     else:
    #         self.pushButton_start.setEnabled(False)

    def port_connect(self):  # 连接串口，构造小车类实例
        port_connect_dialog = DialogUi_Serial()
        if port_connect_dialog.exec_():
            self.port = port_connect_dialog.get_port()
        self.ser = serial.Serial()
        self.ser.port = self.port
        self.ser.open()
        self.port_flag = True
        connect = Info('连接成功')
        connect.display()
        self.pushButton_connect.setText('已连接 ' + self.port)
        self.pushButton_connect.setEnabled(False)
        self.check_start()

    def fileRead(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, '请选择载入的路况变化', path,
                                                      'Document ( *.txt)')
        if fname[0]:
            # print(fname[0])
            # self.traffic.read(fname[0])
            self.trfChange(fname[0])
            self.traffic_flag = True
            self.pushButton_file.setEnabled(False)
            self.pushButton_file.setText('路况' + fname[0][-5:-4])
            self.check_start()

    def trfChange(self, file):
        c_f = open(file, 'r')
        c_list = c_f.readlines()
        self.c_info = {}
        self.c_time = []
        c_number = len(c_list)
        for i in range(0, c_number):
            list = [int(x) for x in c_list[i].split()]
            self.c_info[list[0]] = list[1]
            # c_info.append(list)
        for my_key in self.c_info.keys():
            self.c_time.append(my_key)
        # print(self.c_time)

    def timeout(self):
        self.time_now = time.perf_counter()
        self.second = self.time_now - self.time_init - self.time_stop
        self.second = int(self.second * 1000) / 1000
        self.time_display = str(self.second)
        self.time_display = self.time_display[:self.time_display.find('.') + 2]
        self.TimeCounter.display(self.time_display)
        self.c_trf()
        self.mapsize()
        self.drawmap()
        self.draw_point()
        self.drawcar()

    def save(self):
        score = open(path + os.sep + 'score.txt', 'a')
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
        self.width = self.Map.width()
        self.height = self.Map.height()

    def mapSet(self):
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.clear()
        self.Map.setScene(self.scene)
        self.pen_street = QtGui.QPen(Qt.white, 30, QtCore.Qt.SolidLine,
                                     QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        self.pen_separate = QtGui.QPen(Qt.black, 3, QtCore.Qt.SolidLine,
                                       QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        self.pen_start_point = QtGui.QPen(Qt.black)
        self.brush_start = QtGui.QBrush(Qt.black)
        self.pen_end_point = QtGui.QPen(Qt.red)
        self.brush_end = QtGui.QBrush(Qt.red)
        self.graph = mp.Graph()
        self.graph.read(MAP)
        self.x_max = max(self.graph.x)
        self.y_max = max(self.graph.y)
        self.circle_size = self.pen_street.width() * 0.9

    def drawmap(self):
        self.scene.clear()
        self.x_scale = self.width / self.x_max * 9 / 10
        self.y_scale = self.height / self.y_max * 9 / 10
        for i in range(self.graph.point_num):
            for j in range(self.graph.point_num):
                if self.graph.line[i][j] != 0:
                    x1 = self.graph.x[i] * self.x_scale + self.width / 35
                    y1 = self.graph.y[i] * self.y_scale + self.height / 35
                    x2 = self.graph.x[j] * self.x_scale + self.width / 35
                    y2 = self.graph.y[j] * self.y_scale + self.height / 35
                    self.scene.addLine(x1, y1, x2, y2, self.pen_street)
        self.drawtrf()

        for i in range(self.graph.point_num):
            for j in range(self.graph.point_num):
                if self.graph.line[i][j] != 0:
                    x1 = self.graph.x[i] * self.x_scale + self.width / 35
                    y1 = self.graph.y[i] * self.y_scale + self.height / 35
                    x2 = self.graph.x[j] * self.x_scale + self.width / 35
                    y2 = self.graph.y[j] * self.y_scale + self.height / 35
                    self.scene.addLine(x1, y1, x2, y2, self.pen_separate)
        # scene.setBackgroundBrush(QPixmap("./test.jpg"))  #设置背景图

    def draw_point(self):
        start_x = self.graph.x[self.start_point -
                               1] * self.x_scale + self.width / 35 - self.circle_size / 2
        start_y = self.graph.y[self.start_point -
                               1] * self.y_scale + self.height / 35 - self.circle_size / 2
        end_x = self.graph.x[self.end_point -
                             1] * self.x_scale + self.width / 35 - self.circle_size / 2
        end_y = self.graph.y[self.end_point -
                             1] * self.y_scale + self.height / 35 - self.circle_size / 2
        self.scene.addEllipse(start_x, start_y, self.circle_size,
                              self.circle_size, self.pen_start_point,
                              self.brush_start)
        self.scene.addEllipse(end_x, end_y, self.circle_size, self.circle_size,
                              self.pen_end_point, self.brush_end)

    def resizeEvent(self, QResizeEvent):
        self.mapsize()
        self.drawmap()
        self.drawcar()
        # self.draw_point()

    def point_choose(self):
        point_choose_dialog = DialogUi_Point()
        if point_choose_dialog.exec_():
            self.start_point, self.end_point = point_choose_dialog.get_point()
            self.point_flag = True
            self.pushButton_point.setText('起点:' + str(self.start_point) +
                                          ' 终点:' + str(self.end_point))
            self.check_start()
            self.draw_point()
            # print(self.start_point, self.end_point)

    def trfSet(self):
        self.traffic = trf.Traffic()
        self.traffic.read(TRAFFIC)
        self.pen = []
        self.color = [
            Qt.green, Qt.green, Qt.green, Qt.yellow, Qt.yellow, Qt.red, Qt.red,
            Qt.red, Qt.white
        ]
        for item in self.color:
            self.pen.append(
                QtGui.QPen(
                    item,
                    15,
                    QtCore.Qt.SolidLine,  # 颜色数字
                    QtCore.Qt.RoundCap,
                    QtCore.Qt.RoundJoin))

    def drawtrf(self):
        for i in range(self.traffic.point_num):
            for j in range(self.traffic.point_num):
                if self.traffic.line[i][j] != 0:
                    x1 = self.graph.x[i] * self.x_scale + self.width / 35
                    y1 = self.graph.y[i] * self.y_scale + self.height / 35
                    x2 = self.graph.x[j] * self.x_scale + self.width / 35
                    y2 = self.graph.y[j] * self.y_scale + self.height / 35
                    self.scene.addLine(x1, y1, x2, y2,
                                       self.pen[self.traffic.line[i][j] - 1])

    def c_trf(self):
        # print(1)
        for i in range(0, len(self.c_time)):
            if abs(self.second - self.c_time[i]) < 0.1:
                self.traffic.read(path_trf + os.sep +
                                  str(self.c_info[self.c_time[i]]) + '.dat')
                self.drawmap()
                break

    def coordinate(self, x, y):
        return (x * self.x_scale + self.width / 35,
                y * self.y_scale + self.height / 35)

    def car_position(self, x=0, y=0):
        self.x = x
        self.y = y

    def drawcar(self):
        # car_postition(x, y)  # 获取小车坐标
        (x, y) = self.coordinate(self.x, self.y)  # 坐标变化（暂时还很辣鸡）
        self.carsize = 20
        self.pen_car = QtGui.QPen(Qt.blue)
        self.brush_car = QtGui.QBrush(Qt.blue)
        x = x - self.carsize / 20
        y = y - self.carsize / 20
        self.scene.addEllipse(x, y, self.carsize, self.carsize, self.pen_car,
                              self.brush_car)
        self.x += 1
        # self.y += 1
        self.Map.repaint()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    ex = MainUi()
    sys.exit(app.exec_())
