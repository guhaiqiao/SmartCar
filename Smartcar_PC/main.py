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
import absorp
import picture_rc
import dijkstra

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

        # 初始化罚时
        self.Penalty.display('0')

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
        self.x = 0   # unit: mm
        self.y = 0
        self.carsize = 20

        #初始化定位道路
        self.start_num = 0
        self.end_num = 0

        #比赛开始标志
        self.start_flag = True

        #未走道路信息
        self.end_dist = -1
        self.end_path = []

    def init_ui(self):
        # self.actionsave.triggered.connect(self.save)
        self.pushButton_point.clicked.connect(self.choose_points)
        self.pushButton_start.clicked.connect(self.start)
        self.pushButton_end.clicked.connect(self.end)
        self.pushButton_end.setEnabled(False)
        self.pushButton_traffic.clicked.connect(self.traffic_read)
        self.pushButton_connect.clicked.connect(self.connect)
        self.pushButton_positioning.clicked.connect(self.positioning_control)

        self.scene = QtWidgets.QGraphicsScene()
        self.scene.clear()
        self.Map.setScene(self.scene)

        #初始化视觉定位信息
        self.positioning = positioning.VisionPositioning()
        self.positioning_flag = False
        self.positioning_timer = QtCore.QTimer()
        self.positioning_timer.timeout.connect(self.update_position)

        #笔型初始化
        self.pen_start_point = QtGui.QPen(Qt.blue)
        self.brush_start = QtGui.QBrush(Qt.blue)
        self.pen_end_point = QtGui.QPen(Qt.yellow)
        self.brush_end = QtGui.QBrush(Qt.yellow)
        self.pen_car = QtGui.QPen(Qt.red)
        self.brush_car = QtGui.QBrush(Qt.red)
        self.pens = []
        self.colors = [
            QtGui.QColor(28, 255, 11),
            QtGui.QColor(97, 232, 12),
            QtGui.QColor(181, 255, 0),
            QtGui.QColor(232, 230, 12),
            QtGui.QColor(255, 229, 5),
            QtGui.QColor(255, 182, 0),
            QtGui.QColor(232, 146, 12),
            QtGui.QColor(255, 121, 0),
            QtGui.QColor(232, 84, 12),
            QtGui.QColor(255, 50, 5),
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

    ####################
    # Below are methods about popup dialogs.
    ####################
    def choose_points(self):
        point_choose_dialog = DialogUi_Point(self.client, self.team.team_macs[self.team.team_names.index(self.comboBox_team.currentText())])
        if point_choose_dialog.exec_():
            self.depart_point, self.arrive_point = point_choose_dialog.get_point()
            self.pushButton_point.setText('起点:' + str(self.depart_point) +
                                          ' 终点:' + str(self.arrive_point))
            
            self.positioning.initial_position = [(6000 - self.graph.y[self.depart_point - 1]) // 10 * self.positioning.factor,
                                                800,
                                                self.graph.x[self.depart_point - 1] // 10 * self.positioning.factor,
                                                800]
            if self.positioning.track_flag:
                self.positioning.stop_track()
                self.positioning.begin_track()

            self.drawall()

    def traffic_read(self):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, '请选择载入的路况变化', path)
        if dirname:
            self.traffic = []
            for i in range(200):
                self.traffic.append(extdata.Traffic())
                self.traffic[-1].read(dirname + '/' + str(i + 1) + '.txt')
            self.pushButton_traffic.setText('路况' + dirname.split('/')[-1])

    ####################
    # Below are methods about mqtt communication.
    ####################
    def connect(self):
        self.client = mqtt.Client(client_id='SmartcarPC', userdata='SmartcarPC')
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.username_pw_set('smartcar', 'smartcar')
        self.client.connect('mqtt.gycis.me')
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self.pushButton_connect.setText('连接成功')
        self.pushButton_connect.setEnabled(False)

    def on_disconnect(self, client, userdata, rc):
        self.pushButton_connect.setText('连接')
        self.pushButton_connect.setEnabled(True)

    ####################
    # Below are methods to control the vision positioning and update car's position in the window.
    ####################
    def positioning_control(self):
        if self.pushButton_positioning.text() == '启动定位':
            self.positioning.begin_track()
            self.positioning_timer.start(100)
            self.pushButton_positioning.setText('停止定位')
        else:
            self.positioning.stop_track()
            self.positioning_timer.stop()
            self.pushButton_positioning.setText('启动定位')

    def update_position(self):
        x_img, y_img = self.positioning.get_position()
        self.x = int(x_img / self.positioning.factor * 10)
        self.y = int(y_img / self.positioning.factor * 10)

        self.drawall()
        if math.sqrt((self.x - self.graph.x[self.arrive_point - 1])**2 + (6000 - self.y - self.graph.y[self.arrive_point - 1])**2) < 300:
            self.end()

    def draw_end_dist(self):
        if self.end_dist == -1:      # 如果是第一次计算
            end_road_start, end_road_stop, end_road_dist = absorp.absorp(self.x, self.y, self.graph)
            route_from_start = dijkstra.get_route(end_road_start, self.arrive_point)
            cost_from_start = route_from_start['cost'] + end_road_dist
            route_from_end = dijkstra.get_route(end_road_stop, self.arrive_point)
            cost_from_end = route_from_end['cost'] + dijkstra.get_cost(end_road_start, end_road_stop) - end_road_dist
            if cost_from_start < cost_from_end:
                end_route = route_from_start
            else:
                end_route = route_from_end
            self.end_dist = end_route['cost']
            self.end_path = end_route['path']

            dist = math.sqrt((self.x - self.graph.x[self.arrive_point - 1])**2 + (6000 - self.y - self.graph.y[self.arrive_point - 1])**2)
            print('real dist: ' + str(dist))
            if dist <= 300:  # 认为到达终点
                self.end_dist = 0
                self.end_path = []
            
            print('end_dist: ' + str(self.end_dist))
            route = dijkstra.get_route(self.depart_point, self.arrive_point)
            self.Penalty.display(min(self.end_dist / route['cost'] * 120.0, 120.0))

        for i in range(len(self.end_path) - 1):
            start_point = int(self.end_path[i])
            end_point = int(self.end_path[i + 1])
            start_x = self.graph.x[start_point - 1] * self.x_scale + self.width / 35
            start_y = (6000 - self.graph.y[start_point - 1]) * self.y_scale + self.height / 35
            end_x = self.graph.x[end_point - 1] * self.x_scale + self.width / 35
            end_y = (6000 - self.graph.y[end_point - 1]) * self.y_scale + self.height / 35
            self.scene.addLine(start_x, start_y, end_x, end_y, QtGui.QPen(
                    Qt.darkRed,
                    10,
                    QtCore.Qt.SolidLine,  # 颜色数字
                    QtCore.Qt.RoundCap,
                    QtCore.Qt.RoundJoin))

    def drawall(self):
        ### 画地图
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
                    # self.scene.addLine(x1, y1, x2, y2, self.pens[self.traffic[self.current_traffic].line[i][j]])
                    self.scene.addLine(x1, y1, x2, y2, QtGui.QPen(
                        Qt.black,
                        10,
                        QtCore.Qt.SolidLine,  # 颜色数字
                        QtCore.Qt.RoundCap,
                        QtCore.Qt.RoundJoin))   #去掉路况后用黑色线画地图
        
        ### 画最短路径
        route = dijkstra.get_route(self.depart_point, self.arrive_point)
        path = route['path']
        for i in range(len(path) - 1):
            start_point = int(path[i])
            end_point = int(path[i + 1])
            start_x = self.graph.x[start_point - 1] * self.x_scale + self.width / 35
            start_y = (6000 - self.graph.y[start_point - 1]) * self.y_scale + self.height / 35
            end_x = self.graph.x[end_point - 1] * self.x_scale + self.width / 35
            end_y = (6000 - self.graph.y[end_point - 1]) * self.y_scale + self.height / 35
            self.scene.addLine(start_x, start_y, end_x, end_y, QtGui.QPen(
                    Qt.cyan,
                    10,
                    QtCore.Qt.SolidLine,  # 颜色数字
                    QtCore.Qt.RoundCap,
                    QtCore.Qt.RoundJoin))

        ### 画当前位置
        self.start_x = self.graph.x[self.start_num - 1] * self.x_scale + self.width / 35
        self.start_y = (6000 - self.graph.y[self.start_num - 1]) * self.y_scale + self.height / 35
        self.end_x = self.graph.x[self.end_num - 1] * self.x_scale + self.width / 35
        self.end_y = (6000 - self.graph.y[self.end_num - 1]) * self.y_scale + self.height / 35
        self.scene.addLine(self.start_x, self.start_y, self.end_x, self.end_y, QtGui.QPen(
                        Qt.darkGreen,
                        10,
                        QtCore.Qt.SolidLine,  # 颜色数字
                        QtCore.Qt.RoundCap,
                        QtCore.Qt.RoundJoin))

        ### 画小车
        # self.x = 1000 + 500 * math.cos(self.second)   #模拟生成位置
        # self.y = 1000 + 500 * math.sin(self.second)
        x = self.x * self.x_scale + self.width / 35 - self.carsize / 20
        y = self.y * self.y_scale + self.height / 35 - self.carsize / 20
        self.scene.addEllipse(x, y, self.carsize, self.carsize, self.pen_car,
                              self.brush_car)

        ### 画起终点
        start_x = self.graph.x[self.depart_point - 1] * self.x_scale + self.width / 35 - self.circle_size / 2
        start_y = (6000 - self.graph.y[self.depart_point - 1]) * self.y_scale + self.height / 35 - self.circle_size / 2
        end_x = self.graph.x[self.arrive_point - 1] * self.x_scale + self.width / 35 - self.circle_size / 2
        end_y = (6000 - self.graph.y[self.arrive_point - 1]) * self.y_scale + self.height / 35 - self.circle_size / 2
        self.scene.addEllipse(start_x, start_y, self.circle_size,
                              self.circle_size, self.pen_start_point,
                              self.brush_start)
        self.scene.addEllipse(end_x, end_y, self.circle_size, self.circle_size,
                              self.pen_end_point, self.brush_end)

        ### 画未走路线
        if self.start_flag == False:
            self.draw_end_dist()


    ####################
    # Below are methods about competition.
    ####################
    def start(self):
        if self.pushButton_start.text() == '开始':
            self.Timer.start(100)
            self.score = '0'
            self.time_init = time.perf_counter()
            self.pushButton_start.setText('暂停')
            self.pushButton_end.setEnabled(True)
            self.start_flag = True
            self.client.publish('/smartcar/' + self.team.team_macs[
                self.team.team_names.index(self.comboBox_team.currentText())] + '/command', qos=1,
                                payload=bytes([0]))

        elif self.pushButton_start.text() == '暂停':
            self.Timer.stop()
            self.time_stop_init = time.perf_counter()
            self.pushButton_start.setText('继续')
            self.client.publish('/smartcar/' + self.team.team_macs[
                self.team.team_names.index(self.comboBox_team.currentText())] + '/command', qos=1,
                                payload=bytes([2]))

        elif self.pushButton_start.text() == '继续':
            self.time_stop_finl = time.perf_counter()
            self.Timer.start(100)
            self.time_stop += self.time_stop_finl - self.time_stop_init
            self.pushButton_start.setText('暂停')
            self.client.publish('/smartcar/' + self.team.team_macs[
                self.team.team_names.index(self.comboBox_team.currentText())] + '/command', qos=1,
                                payload=bytes([0]))

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
        self.start_flag = False
        self.save()
        self.client.publish('/smartcar/' + self.team.team_macs[
            self.team.team_names.index(self.comboBox_team.currentText())] + '/command', qos=1, payload=bytes([1]))

    def timeout(self):
        self.time_now = time.perf_counter()
        self.second = self.time_now - self.time_init - self.time_stop
        self.second = int(self.second * 1000) / 1000
        self.time_display = str(self.second)
        self.time_display = self.time_display[:self.time_display.find('.') + 2]
        self.TimeCounter.display(self.time_display)

        self.start_num, self.end_num, dist = absorp.absorp(self.x, self.y, self.graph)
        self.current_traffic = math.floor(self.second) // 1 if math.floor(self.second) // 1 < len(self.traffic) else len(self.traffic) - 1   ###更改其中的1可改变路况变化速率
        self.client.publish('/smartcar/' + self.team.team_macs[self.team.team_names.index(self.comboBox_team.currentText())] + '/position', bytes([self.start_num , self.end_num, dist % 256, dist // 256, self.x % 256, self.x // 256, self.y % 256, self.y // 256]))
        # if self.second - math.floor(self.second) < 0.2:
        #     self.client.publish('/smartcar/' + self.comboBox_team.currentText() + '/traffic', bytes(self.traffic[self.current_traffic].original_data, 'utf-8'))
        if int(self.second) >= 180:
            self.end()

    def save(self):
        score = open(path + os.sep + 'scores.txt', 'a')
        score.write(self.comboBox_team.currentText() + ' ' + self.score + '\n')
        score.close()

    ####################
    # Below are methods about window control.
    ####################
    def resizeEvent(self, QResizeEvent):
        self.width = self.Map.width()
        self.height = self.Map.height()
        self.drawall()

    def keyPressEvent(self, event):
        if event.text() == 'r':
            self.rc = RcUi(self, self.client, self.comboBox_team.currentText())

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
    def __init__(self, client, team):
        QtBaseClass_Dialog_Point.__init__(self)
        Ui_Dialog_Team.__init__(self)
        self.setupUi(self)
        self.start_point_flag = False
        self.end_point_flag = False
        self.pushButton.clicked.connect(self.get)
        self.pushButton.setEnabled(False)
        self.start_point.textChanged[str].connect(self.start_point_set)
        self.end_point.textChanged[str].connect(self.end_point_set)

        self.client = client
        self.topic = '/smartcar/' + team + '/task'

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
        self.client.publish(self.topic, qos=1, payload=bytes([self.s_point, self.e_point]))
        self.accept()

    def get_point(self):
        return self.s_point, self.e_point


class RcUi(Ui_rc, QtBaseClass_rc):
    def __init__(self, parent, client, team):
        QtBaseClass_rc.__init__(self, parent)
        Ui_rc.__init__(self)
        self.setupUi(self)
        self.show()

        self.client = client
        self.topic = '/smartcar/' + team + '/rccontrol'
        self.control_flag = False
        self.smoothcontrol_flag = False
        self.smoothcontrol_thread = None
        self.slider_speed.setEnabled(False)
        self.slider_radius.setEnabled(False)
        self.setFocusPolicy(Qt.ClickFocus)
        self.setFocus(True)
        self.icon.setFocusPolicy(Qt.NoFocus)

    def keyPressEvent(self, event):
        if not event.isAutoRepeat():
            if event.text() == 'w' and not self.control_flag:
                self.icon.setStyleSheet('border-image: url(:/background/images/forward.jpg);')
                self.client.publish(self.topic, 'forward')
            elif event.text() == 's' and not self.control_flag:
                self.icon.setStyleSheet('border-image: url(:/background/images/backward.jpg);')
                self.client.publish(self.topic, 'backward')
            elif event.text() == 'a' and not self.control_flag:
                self.icon.setStyleSheet('border-image: url(:/background/images/left.jpg);')
                self.client.publish(self.topic, 'left')
            elif event.text() == 'd' and not self.control_flag:
                self.icon.setStyleSheet('border-image: url(:/background/images/right.jpg);')
                self.client.publish(self.topic, 'right')
            elif event.text() == 'e': 
                self.icon.setStyleSheet('border-image: url(:/background/images/clockwise.jpg);')
                self.client.publish(self.topic, 'clockwise')
            elif event.text() == 'q':
                self.icon.setStyleSheet('border-image: url(:/background/images/anticlockwise.jpg);')
                self.client.publish(self.topic, 'anti-clockwise')

            elif event.text() == 'w'and self.control_flag:
                self.icon.setStyleSheet('border-image: url(:/background/images/forward.jpg);')
                self.client.publish(self.topic, 'forward' + str(self.slider_speed.value()))
            elif event.text() == 's'and self.control_flag:
                self.icon.setStyleSheet('border-image: url(:/background/images/backward.jpg);')
                self.client.publish(self.topic, 'backward' + str(self.slider_speed.value()))
            elif event.text() == 'a'and self.control_flag:
                self.icon.setStyleSheet('border-image: url(:/background/images/left.jpg);')
                self.client.publish(self.topic, 'left' + str(self.slider_radius.value()))
            elif event.text() == 'd'and self.control_flag:
                self.icon.setStyleSheet('border-image: url(:/background/images/right.jpg);')
                self.client.publish(self.topic, 'right' + str(self.slider_radius.value()))
            elif event.text() == 'f':
                self.control_flag = not self.control_flag
                self.slider_speed.setEnabled(self.control_flag)
                self.slider_radius.setEnabled(self.control_flag)
            elif event.text() == 'g':
                if not self.smoothcontrol_flag:
                    self.smoothcontrol_flag = True
                    self.smoothcontrol_thread = threading.Thread(target=self.smoothcontrol, daemon=True)
                    self.smoothcontrol_thread.start()
                else:
                    self.smoothcontrol_flag = False
                    if threading.current_thread() != self.smoothcontrol_thread:
                        self.smoothcontrol_thread.join()
                        self.smoothcontrol_thread = None
            elif event.text() == '1':
                self.client.publish(self.topic, 'other1')
            elif event.text() == '2':
                self.client.publish(self.topic, 'other2')
            elif event.text() == '3':
                self.client.publish(self.topic, 'other3')

    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            self.icon.setStyleSheet('border-image: url(:/background/images/stop.jpg);')
            self.client.publish(self.topic, 'stop')

    def smoothcontrol(self):
        while self.smoothcontrol_flag:
            self.client.publish(self.topic, 'motor-left' + str(self.slider_speed.value()))
            self.client.publish(self.topic, 'motor-right' + str(self.slider_radius.value()))
            time.sleep(0.1)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = MainUi()
    sys.exit(app.exec_())
