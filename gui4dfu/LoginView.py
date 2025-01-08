# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LoginView.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


# import pymssql
import DbProvider as DB
from UDPViewNew import *


class Ui_LoginForm(object):
    def __init__(self, MainView):
        super().__init__()
        # self.setupUi()
        self.MainView = MainView

    def setupUi(self, Window):
        Window.setObjectName("Window")
        Window.resize(480, 320)

        self.centralwidget = QtWidgets.QWidget(Window)
        self.centralwidget.setObjectName("centralwidget")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout.addItem(spacerItem)

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setContentsMargins(-1, -1, -1, 12)
        self.formLayout.setVerticalSpacing(12)
        self.formLayout.setObjectName("formLayout")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)

        self.UserTextbox = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.UserTextbox.sizePolicy().hasHeightForWidth())
        self.UserTextbox.setSizePolicy(sizePolicy)
        self.UserTextbox.setObjectName("UserTextbox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.UserTextbox)

        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)

        self.PasswordTextbox = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PasswordTextbox.sizePolicy().hasHeightForWidth())
        self.PasswordTextbox.setSizePolicy(sizePolicy)
        self.PasswordTextbox.setObjectName("PasswordTextbox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.PasswordTextbox)

        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)

        self.RegioncomboBox = QtWidgets.QComboBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.RegioncomboBox.sizePolicy().hasHeightForWidth())
        self.RegioncomboBox.setSizePolicy(sizePolicy)
        self.RegioncomboBox.setObjectName("RegioncomboBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.RegioncomboBox)

        self.verticalLayout.addLayout(self.formLayout)

        self.LoginButton = QtWidgets.QPushButton(self.centralwidget)
        self.LoginButton.setObjectName("LoginButton")

        self.verticalLayout.addWidget(self.LoginButton)

        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)

        self.horizontalLayout.addLayout(self.verticalLayout)

        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout.addItem(spacerItem3)

        Window.setCentralWidget(self.centralwidget)

        # self.LoginButton = QtWidgets.QPushButton(LoginForm)
        # self.LoginButton.setGeometry(QtCore.QRect(200, 220, 121, 30))
        # self.LoginButton.setObjectName("LoginButton")
        # self.LoginButton.clicked.connect(self.LoginEventHandler)
        # self.label = QtWidgets.QLabel(LoginForm)
        # self.label.setGeometry(QtCore.QRect(120, 30, 61, 31))
        # self.label.setObjectName("label")
        # self.label_2 = QtWidgets.QLabel(LoginForm)
        # self.label_2.setGeometry(QtCore.QRect(70, 90, 111, 31))
        # self.label_2.setObjectName("label_2")
        # self.label_3 = QtWidgets.QLabel(LoginForm)
        # self.label_3.setGeometry(QtCore.QRect(80, 150, 81, 31))
        # self.label_3.setObjectName("label_3")
        # self.UserTextbox = QtWidgets.QTextEdit(LoginForm)
        # self.UserTextbox.setGeometry(QtCore.QRect(200, 30, 121, 31))
        # self.UserTextbox.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.UserTextbox.setObjectName("UserTextbox")
        # self.PasswordTextbox = QtWidgets.QTextEdit(LoginForm)
        # self.PasswordTextbox.setGeometry(QtCore.QRect(200, 90, 121, 31))
        # self.PasswordTextbox.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.PasswordTextbox.setObjectName("PasswordTextbox")
        # self.RegioncomboBox = QtWidgets.QComboBox(LoginForm)
        # self.RegioncomboBox.setGeometry(QtCore.QRect(200, 150, 121, 30))
        # self.RegioncomboBox.setObjectName("RegioncomboBox")
        # self.RegioncomboBox.addItem("")
        # self.RegioncomboBox.addItem("")

        self.retranslateUi(Window)

        self.LoginButton.clicked.connect(self.LoginEventHandler)

        QtCore.QMetaObject.connectSlotsByName(Window)

    def retranslateUi(self, Window):
        _translate = QtCore.QCoreApplication.translate
        Window.setWindowTitle(_translate("Window", "Login"))
        self.LoginButton.setText(_translate("Window", "Login"))
        self.label.setText(_translate("Window", "User"))
        self.label_2.setText(_translate("Window", "Password"))
        self.label_3.setText(_translate("Window", "Region"))
        self.RegioncomboBox.addItem(_translate("Window", "SuZhou"))
        self.RegioncomboBox.addItem(_translate("Window", "Batam"))
        # self.RegioncomboBox.setItemText(0, _translate("LoginForm", "SuZhou"))
        # self.RegioncomboBox.setItemText(1, _translate("LoginForm", "Batam"))

    def LoginEventHandler(self):
        if self.MainView is not None:
            self.MainView.show()
            self.hide()
        return
        server = 'SUZ-VM-SQL-002'
        database = 'ACCCableTest_DEV'
        table = 'UserInfo'
        user = 'acccable'
        password = 'K6$7uAuegP'
        conn = pymssql.connect(server, user, password, database)
        cursor = conn.cursor()
        query = f"SELECT * FROM {table} WHERE UserID ='{self.UserTextbox.toPlainText().strip()}'"
        cursor.execute(query)
        record = cursor.fetchone()
        region = self.RegioncomboBox.currentText()
        if (region == "SuZhou"):
            DB.DbProvider.Db = DB.SZDbSetting()
            DB.DbProvider.Mes = DB.SZMesSetting()
        if record:
            db_password = record[1]
            if self.PasswordTextbox.toPlainText().strip() == db_password:
                if self.MainView is not None:
                    self.MainView.show()
                    self.hide()
            else:
                self.PasswordTextbox.setText('Password Wrong')
        else:
            self.UserTextbox.setText('User Wrong')