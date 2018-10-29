from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt
import os
import time
import threading
import sys
import paho.mqtt.client as mqtt
import math
import extdata
import positioning

path = os.getcwd()

MAIN_WINDOW = path + os.sep + 'pc2.ui'
DIALOG_POINT = path + os.sep + 'dialog_point.ui'
RC = path + os.sep + 'rc.ui'

MAP = path + os.sep + 'map.txt'
TEAM = path + os.sep + 'teams.txt'

Ui_MainWindow, QtBaseClass_MainWindow = uic.loadUiType(MAIN_WINDOW)
Ui_Dialog_Team, QtBaseClass_Dialog_Point = uic.loadUiType(DIALOG_POINT)
Ui_rc, QtBaseClass_rc = uic.loadUiType(RC)

class Info(QtWidgets.QMessageBox):
    def __init__(self, info=''):
        QtWidgets.QMessageBox.__init__(self)
        self.info = info

    def display(self):
        self.information(self, '提示', self.info, self.Close)


class MainUi(Ui_MainWindow, QtBaseClass_MainWindow):
    def __init__(self):
        QtBaseClass_MainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.init_vars()
        self.init_ui()

    def init_vars(self):
        #初始化计时器
        self.Timer = QtCore.QTimer()  # 计时器
        self.second = 0  # 初始化计时器秒数
        self.time_stop = 0
        self.TimeCounter.display('0')
        self.Timer.timeout.connect(self.timeout)

        #初始化队伍名称
        self.team = extdata.Team()
        self.team.read(TEAM)
        self.comboBox_team.clear()
        self.comboBox_team.addItem('选择队伍')
        for name in self.team.team_names:
            self.comboBox_team.addItem(name)

        #初始化起终点
        self.depart_point = 0
        self.arrive_point = 0
        self.pushButton_point.setText('选择起终点')

        #初始化地图信息
        self.graph = extdata.Graph()
        self.graph.read(MAP)
        self.x_max = max(self.graph.x)
        self.y_max = max(self.graph.y)

        #初始化路况信息
        self.traffic = []
        self.traffic.append(extdata.Traffic(self.graph.point_num))
        self.current_traffic = 0

        self.score = '0'

        #初始化小车信息
        self.x = 0
        self.y = 0
        self.carsize = 20

    def init_ui(self):
        # self.actionsave.triggered.connect(self.save)
        self.pushButton_point.clicked.connect(self.choose_points)
        self.pushButton_start.clicked.connect(self.start)
        self.pushButton_end.clicked.connect(self.end)
        self.pushButton_end.setEnabled(False)
        self.pushButton_traffic.clicked.connect(self.traffic_read)
        self.pushButton_connect.clicked.connect(self.connect)

        self.scene = QtWidgets.QGraphicsScene()
        self.scene.clear()
        self.Map.setScene(self.scene)

        #笔型初始化
        self.pen_start_point = QtGui.QPen(Qt.black)
        self.brush_start = QtGui.QBrush(Qt.black)
        self.pen_end_point = QtGui.QPen(Qt.red)
        self.brush_end = QtGui.QBrush(Qt.red)
        self.pen_car = QtGui.QPen(Qt.blue)
        self.brush_car = QtGui.QBrush(Qt.blue)
        self.pens = []
        self.colors = [
            QtGui.QColor(28, 255, 11), QtGui.QColor(97, 232, 12), QtGui.QColor(181, 255, 0), QtGui.QColor(232, 230, 12), QtGui.QColor(255, 229, 5), 
            QtGui.QColor(255, 182, 0), QtGui.QColor(232, 146, 12), QtGui.QColor(255, 121, 0), QtGui.QColor(232, 84, 12), QtGui.QColor(255, 50, 5), 
            QtGui.QColor(255, 0, 0), 
        ]
        for color in self.colors:
            self.pens.append(
                QtGui.QPen(
                    color,
                    15,
                    QtCore.Qt.SolidLine,  # 颜色数字
                    QtCore.Qt.RoundCap,
                    QtCore.Qt.RoundJoin))

        self.circle_size = 20

        self.show()
        self.width = self.Map.width()
        self.height = self.Map.height()
        self.drawall()

    def choose_points(self):
        point_choose_dialog = DialogUi_Point()
        if point_choose_dialog.exec_():
            self.depart_point, self.arrive_point = point_choose_dialog.get_point()
            self.pushButton_point.setText('起点:' + str(self.depart_point) +
                                          ' 终点:' + str(self.arrive_point))
            self.drawall()

    def connect(self):
        self.client = mqtt.Client(client_id='SmartcarPC', userdata='SmartcarPC')
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.connect('test.mosquitto.org')
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        self.pushButton_connect.setText('连接成功')
        self.pushButton_connect.setEnabled(False)

    def on_disconnect(self, client, userdata, rc):
        self.pushButton_connect.setText('连接')
        self.pushButton_connect.setEnabled(True)

    def start(self):
        if self.pushButton_start.text() == '开始':
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
            self.pushButton_start.setText('暂停')

        else:  # 清零操作
            self.init_vars()
            self.pushButton_start.setText('开始')
            self.drawall()

    def end(self):
        self.Timer.stop()
        self.score = self.time_display
        self.pushButton_start.setText('清零')
        self.pushButton_end.setEnabled(False)
        self.pushButton_start.setEnabled(True)
        self.save()

    def traffic_read(self):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, '请选择载入的路况变化', path)
        if dirname:
            self.traffic = []
            for i in range(200):
                self.traffic.append(extdata.Traffic())
                self.traffic[-1].read(dirname + '/' + str(i + 1) + '.txt')
            self.pushButton_traffic.setText('路况' + dirname.split('/')[-1])

    def timeout(self):
        self.time_now = time.perf_counter()
        self.second = self.time_now - self.time_init - self.time_stop
        self.second = int(self.second * 1000) / 1000
        self.time_display = str(self.second)
        self.time_display = self.time_display[:self.time_display.find('.') + 2]
        self.TimeCounter.display(self.time_display)
        self.current_traffic = math.floor(self.second) // 1 if math.floor(self.second) // 1 < len(self.traffic) else len(self.traffic) - 1   ###更改其中的1可改变路况变化速率
        self.client.publish('/smartcar/final/' + self.comboBox_team.currentText() + '/position', bytes(str(self.x) + ' ' + str(self.y), 'utf-8'))
        if self.second - math.floor(self.second) < 0.2:
            self.client.publish('/smartcar/final/' + self.comboBox_team.currentText() + '/traffic', bytes(self.traffic[self.current_traffic].original_data, 'utf-8'))
        self.drawall()

    def save(self):
        score = open(path + os.sep + 'scores.txt', 'a')
        score.write(self.comboBox_team.currentText() + ' ' + self.score + '\n')
        score.close()

    def drawall(self):
        ###画地图
        self.scene.clear()
        self.x_scale = self.width / self.x_max * 9 / 10
        self.y_scale = self.height / self.y_max * 9 / 10
        for i in range(self.graph.point_num):
            for j in range(self.graph.point_num):
                if self.graph.line[i][j] != 0:
                    x1 = self.graph.x[i] * self.x_scale + self.width / 35
                    y1 = (6000 - self.graph.y[i]) * self.y_scale + self.height / 35
                    x2 = self.graph.x[j] * self.x_scale + self.width / 35
                    y2 = (6000 - self.graph.y[j]) * self.y_scale + self.height / 35
                    self.scene.addLine(x1, y1, x2, y2, self.pens[self.traffic[self.current_traffic].line[i][j]])

        ###画小车
        # car_postition(x, y)  # 获取小车坐标
        self.x = 1000 + 500 * math.cos(self.second)
        self.y = 1000 + 500 * math.sin(self.second)
        x = self.x * self.x_scale + self.width / 35 - self.carsize / 20
        y = self.y * self.y_scale + self.height / 35 - self.carsize / 20
        self.scene.addEllipse(x, y, self.carsize, self.carsize, self.pen_car,
                              self.brush_car)

        ###画起终点
        start_x = self.graph.x[self.depart_point] * self.x_scale + self.width / 35 - self.circle_size / 2
        start_y = (6000 - self.graph.y[self.depart_point]) * self.y_scale + self.height / 35 - self.circle_size / 2
        end_x = self.graph.x[self.arrive_point] * self.x_scale + self.width / 35 - self.circle_size / 2
        end_y = (6000 - self.graph.y[self.arrive_point]) * self.y_scale + self.height / 35 - self.circle_size / 2
        self.scene.addEllipse(start_x, start_y, self.circle_size,
                              self.circle_size, self.pen_start_point,
                              self.brush_start)
        self.scene.addEllipse(end_x, end_y, self.circle_size, self.circle_size,
                              self.pen_end_point, self.brush_end)

    def resizeEvent(self, QResizeEvent):
        self.width = self.Map.width()
        self.height = self.Map.height()
        self.drawall()

    def keyPressEvent(self, event):
        if event.text() == 'r':
            self.rc = RcUi(self, self.client)

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(
            self, '提示', "你竟然要退出？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

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

class RcUi(Ui_rc, QtBaseClass_rc):
    def __init__(self, parent, client):
        QtBaseClass_rc.__init__(self, parent)
        Ui_rc.__init__(self)
        self.setupUi(self)
        self.show()

        self.client = client

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.MoveToNextChar):
            self.icon.setStyleSheet('border-image: url(:/background/images/right.jpg);')
            self.client.publish('/smartcar/rccontrol', 'right')
        elif event.matches(QtGui.QKeySequence.MoveToPreviousChar):
            self.icon.setStyleSheet('border-image: url(:/background/images/left.jpg);')
            self.client.publish('/smartcar/rccontrol', 'left')
        elif event.matches(QtGui.QKeySequence.MoveToNextLine):
            self.icon.setStyleSheet('border-image: url(:/background/images/backward.jpg);')
            self.client.publish('/smartcar/rccontrol', 'backward')
        elif event.matches(QtGui.QKeySequence.MoveToPreviousLine):
            self.icon.setStyleSheet('border-image: url(:/background/images/forward.jpg);')
            self.client.publish('/smartcar/rccontrol', 'forward')
        elif event.matches(QtGui.QKeySequence.SelectNextChar):   #Shift+右
            self.icon.setStyleSheet('border-image: url(:/background/images/clockwise.jpg);')
            self.client.publish('/smartcar/rccontrol', 'clockwise')
        elif event.matches(QtGui.QKeySequence.SelectPreviousChar):   #Shift+左
            self.icon.setStyleSheet('border-image: url(:/background/images/anticlockwise.jpg);')
            self.client.publish('/smartcar/rccontrol', 'anti-clockwise')
        elif event.text() == 'w':
            self.icon.setStyleSheet('border-image: url(:/background/images/forward.jpg);')
            self.client.publish('/smartcar/rccontrol', 'forward' + str(self.slider_speed.value()))
        elif event.text() == 's':
            self.icon.setStyleSheet('border-image: url(:/background/images/backward.jpg);')
            self.client.publish('/smartcar/rccontrol', 'backward' + str(self.slider_speed.value()))
        elif event.text() == 'a':
            self.icon.setStyleSheet('border-image: url(:/background/images/left.jpg);')
            self.client.publish('/smartcar/rccontrol', 'left' + str(self.slider_radius.value()))
        elif event.text() == 'd':
            self.icon.setStyleSheet('border-image: url(:/background/images/right.jpg);')
            self.client.publish('/smartcar/rccontrol', 'right' + str(self.slider_radius.value()))

    def keyReleaseEvent(self, event):
        self.icon.setStyleSheet('border-image: url(:/background/images/stop.jpg);')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = MainUi()
    sys.exit(app.exec_())