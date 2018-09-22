from PyQt5 import QtWidgets, uic, QtCore, QtGui
import os
import serial
import serial.tools.list_ports
# import time
import threading
import sys

path = os.getcwd()
File = path + os.sep + 'Upper Computer' + os.sep + 'Program' + os.sep + 'pc2.ui'
print(File)
Ui_MainWindow, QtBaseClass = uic.loadUiType(File)
# 后期UI界面文字字体及颜色修改
_translate = QtCore.QCoreApplication.translate
traffic_info = ''
port_avail = []

class Info(QtWidgets.QMessageBox):
    def __init__(self, info=''):
        QtWidgets.QMessageBox.__init__(self)
        self.info = info

    def display(self):
        self.information(self, '提示', self.info, self.Close)


# class Port(threading.Thread, QObject):
#     def __init__(self):
#         threading.Thread.__init__(self)
#         self.list = []
#         global port_avail
#         signal = QtCore.pyqtSignal(port_avail)

#     def run(self):
#         global port_avail
#         while True:
#             if self.list != serial.tools.list_ports.comports():
#                 self.list = serial.tools.list_ports.comports()
#                 if len(self.list) <= 0:
#                     port_avail = []
#                 else:
#                     for i in len(list):
#                         port_avail[i] = self.list[i]
#             else:
#                 pass



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
        # self.find_port = Port()  # 实时监测串口名称
        # self.find_port.start()
        # self.load_map_flag = False

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
        self.DrawMap()
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

        else:  #清零操作
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
        global port_avail
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
