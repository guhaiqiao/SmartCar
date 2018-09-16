from PyQt5 import QtWidgets
import sys
import gui

app = QtWidgets.QApplication(sys.argv)
op = gui.Surface()
if op.exec():
    print("Start")
    demo = b"4"
    print(demo)
else:
    print("End")
sys.exit(app.exec())
