from PyQt5 import QtWidgets, uic, QtCore, QtGui
import cv2 as cv
import os
import sys
import numpy as np

PANEL = os.getcwd() + os.sep + 'panel.ui'
ui_panel, QtBaseClass_panel = uic.loadUiType(PANEL)


class Panel(ui_panel, QtBaseClass_panel):
    def __init__(self):
        QtBaseClass_panel.__init__(self)
        ui_panel.__init__(self)
        self.setupUi(self)
        self.pushbutton_save.clicked.connect(self.save)
        self.radiobutton_point1.toggled.connect(self.toggled_point1)
        self.radiobutton_point2.toggled.connect(self.toggled_point2)
        self.radiobutton_point3.toggled.connect(self.toggled_point3)
        self.radiobutton_point4.toggled.connect(self.toggled_point4)
        self.show()

        self.point_position = [[0, 0] for _ in range(4)]
        self.current_point = 1
        self.frame_width = 0
        self.frame_height = 0
        self.cap = cv.VideoCapture(0)
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)

        while not self.init_frame():
            pass
        self.loop()

    def init_frame(self):
        ret, img = self.cap.read()
        if ret:
            self.slider_x.setMaximum(img.shape[1] - 1)   #graph coordinate
            self.slider_y.setMaximum(img.shape[0] - 1)
            self.point_position[0] = [0, 0]
            self.point_position[1] = [img.shape[1] - 1, 0]
            self.point_position[2] = [img.shape[1] - 1, img.shape[0] - 1]
            self.point_position[3] = [0, img.shape[0] - 1]
            self.frame_width = img.shape[1]
            self.frame_height = img.shape[0]

            return True
        else:
            return False

    def save(self):
        with open('./save.txt', 'w') as f:
            f.write('Frame size: (' + str(self.frame_width) + ', ' + str(self.frame_height) + ')\n\n')

            f.write('Point 1 (upper left): (' + str(self.point_position[0][0]) + ', ' + str(
                self.point_position[0][1]) + ')\n')
            f.write('Point 2 (upper right): (' + str(self.point_position[1][0]) + ', ' + str(
                self.point_position[1][1]) + ')\n')
            f.write('Point 3 (lower right): (' + str(self.point_position[2][0]) + ', ' + str(
                self.point_position[2][1]) + ')\n')
            f.write('Point 4 (lower left): (' + str(self.point_position[3][0]) + ', ' + str(
                self.point_position[3][1]) + ')\n')

    def toggled_point1(self):
        self.slider_x.setValue(self.point_position[0][0])
        self.slider_y.setValue(self.point_position[0][1])
        self.current_point = 1

    def toggled_point2(self):
        self.slider_x.setValue(self.point_position[1][0])
        self.slider_y.setValue(self.point_position[1][1])
        self.current_point = 2

    def toggled_point3(self):
        self.slider_x.setValue(self.point_position[2][0])
        self.slider_y.setValue(self.point_position[2][1])
        self.current_point = 3

    def toggled_point4(self):
        self.slider_x.setValue(self.point_position[3][0])
        self.slider_y.setValue(self.point_position[3][1])
        self.current_point = 4

    def loop(self):
        while True:
            self.point_position[self.current_point - 1][0] = self.slider_x.value()
            self.point_position[self.current_point - 1][1] = self.slider_y.value()

            ret, img = self.cap.read()
            if ret:
                img2 = cv.polylines(img.copy(), np.array(self.point_position, np.int32).reshape((1,-1,2)), True, (255, 255, 255), 1)

                perspectiveMatrix = cv.getPerspectiveTransform(np.array(self.point_position, np.float32), np.array([[0, 0], [600, 0], [600, 600], [0, 600]], np.float32))
                img3 = cv.warpPerspective(img, perspectiveMatrix, (600, 600))

                cv.imshow('Original Image', cv.resize(img2, None, fx=1, fy=1, interpolation=cv.INTER_CUBIC))
                cv.imshow('Transformed Image', cv.resize(img3, None, fx=1, fy=1, interpolation=cv.INTER_CUBIC))
                k = cv.waitKey(1) & 0xff
                if k == 27:
                    break

        cv.destroyAllWindows()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Panel()
    sys.exit(app.exec_())
