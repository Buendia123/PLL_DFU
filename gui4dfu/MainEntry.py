#!/usr/bin/python3

import os.path
import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import *

from LoginView import *


class MainView(QMainWindow, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class LoginView(QMainWindow, Ui_LoginForm):
    def __init__(self):
        super().__init__(MainView=MainView())
        self.setupUi(self)


if __name__ == '__main__':
    pwd = os.path.dirname(os.path.realpath(__file__))

    app = QApplication(sys.argv)
    app_icon = QtGui.QIcon()
    app_icon.addFile(f'{pwd}/assets/Volex-Logo.ico', QtCore.QSize(16, 16))
    app_icon.addFile(f'{pwd}/assets/Volex-Logo.ico', QtCore.QSize(24, 24))
    app_icon.addFile(f'{pwd}/assets/Volex-Logo.ico', QtCore.QSize(32, 32))
    app_icon.addFile(f'{pwd}/assets/Volex-Logo.ico', QtCore.QSize(48, 48))
    app_icon.addFile(f'{pwd}/assets/Volex-Logo.ico', QtCore.QSize(256, 256))
    app.setWindowIcon(app_icon)

    main = MainView()

    main.show()

    # app.exec_()
    sys.exit(app.exec_())
