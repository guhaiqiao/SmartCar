import pyqt
import sys
from PyQt5 import QtWidgets, uic, QtCore, QtGui

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = pyqt.MainUi()
    window.show()
    sys.exit(app.exec_())
