import pyqt2
import sys
from PyQt5 import QtWidgets, uic, QtCore, QtGui

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = pyqt2.MainUi()
    window.show()
    sys.exit(app.exec_())
