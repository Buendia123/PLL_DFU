# -*- coding: utf-8 -*-
import json

from PyQt5 import QtCore, QtWidgets

from ALdfuCh1 import *
from ALdfuCh2 import *
from ALdfuCh3 import *
from ALdfuCh4 import *
from LogProvider import *


# Form implementation generated from reading ui file 'Widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


class Ui_Form(object):
    def __init__(self):
        self.count = 0
        self.window = None

    def setupUi(self, Window: QtWidgets.QMainWindow):
        self.window = Window
        Window.setObjectName("Window")
        Window.resize(1116, 641)

        self.centralwidget = QtWidgets.QWidget(Window)
        self.centralwidget.setObjectName("centralwidget")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.widget = QtWidgets.QWidget(self.groupBox)
        self.widget.setObjectName("widget")

        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setVerticalSpacing(6)

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignmentFlag.AlignLeading)
        self.formLayout.setSpacing(6)

        self.snA1 = QtWidgets.QLineEdit(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.snA1.sizePolicy().hasHeightForWidth())
        self.snA1.setSizePolicy(sizePolicy)
        self.snA1.setMinimumSize(QtCore.QSize(160, 0))
        self.snA1.setObjectName("snA1")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.snA1)

        self.Ch1Result = QtWidgets.QLineEdit(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Ch1Result.sizePolicy().hasHeightForWidth())
        self.Ch1Result.setSizePolicy(sizePolicy)
        self.Ch1Result.setMinimumSize(QtCore.QSize(160, 0))
        self.Ch1Result.setReadOnly(True)
        self.Ch1Result.setObjectName("Ch1Result")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.Ch1Result)

        self.snA2 = QtWidgets.QLineEdit(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.snA2.sizePolicy().hasHeightForWidth())
        self.snA2.setSizePolicy(sizePolicy)
        self.snA2.setMinimumSize(QtCore.QSize(160, 0))
        self.snA2.setObjectName("snA2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.snA2)

        self.Ch2Result = QtWidgets.QLineEdit(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Ch2Result.sizePolicy().hasHeightForWidth())
        self.Ch2Result.setSizePolicy(sizePolicy)
        self.Ch2Result.setMinimumSize(QtCore.QSize(160, 0))
        self.Ch2Result.setReadOnly(True)
        self.Ch2Result.setObjectName("Ch2Result")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.Ch2Result)

        self.snA3 = QtWidgets.QLineEdit(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.snA3.sizePolicy().hasHeightForWidth())
        self.snA3.setSizePolicy(sizePolicy)
        self.snA3.setMinimumSize(QtCore.QSize(160, 0))
        self.snA3.setObjectName("snA3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.snA3)

        self.Ch3Result = QtWidgets.QLineEdit(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Ch3Result.sizePolicy().hasHeightForWidth())
        self.Ch3Result.setSizePolicy(sizePolicy)
        self.Ch3Result.setMinimumSize(QtCore.QSize(160, 0))
        self.Ch3Result.setReadOnly(True)
        self.Ch3Result.setObjectName("Ch3Result")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.Ch3Result)

        self.snA4 = QtWidgets.QLineEdit(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.snA4.sizePolicy().hasHeightForWidth())
        self.snA4.setSizePolicy(sizePolicy)
        self.snA4.setMinimumSize(QtCore.QSize(160, 0))
        self.snA4.setObjectName("snA4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.snA4)

        self.Ch4Result = QtWidgets.QLineEdit(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Ch4Result.sizePolicy().hasHeightForWidth())
        self.Ch4Result.setSizePolicy(sizePolicy)
        self.Ch4Result.setMinimumSize(QtCore.QSize(160, 0))
        self.Ch4Result.setReadOnly(True)
        self.Ch4Result.setObjectName("Ch4Result")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.Ch4Result)

        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.widget)

        self.ClickButton = QtWidgets.QPushButton(self.groupBox)
        self.ClickButton.setObjectName("ClickButton")
        self.verticalLayout_2.addWidget(self.ClickButton)

        self.ClearButton = QtWidgets.QPushButton(self.groupBox)
        self.ClearButton.setObjectName("ClearButton")
        self.verticalLayout_2.addWidget(self.ClearButton)

        self.verticalLayout.addWidget(self.groupBox)

        spacerItem = QtWidgets.QSpacerItem(20, 10000, QtWidgets.QSizePolicy.Policy.Minimum,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName("groupBox_2")

        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.LogTextEdit = QtWidgets.QTextEdit(self.groupBox_2)
        self.LogTextEdit.setReadOnly(True)
        self.LogTextEdit.setObjectName("LogTextEdit")
        self.LogTextEdit.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.gridLayout_2.addWidget(self.LogTextEdit, 0, 0, 1, 1)

        self.horizontalLayout.addWidget(self.groupBox_2)

        Window.setCentralWidget(self.centralwidget)

        menuBar = Window.menuBar()
        helpMenu = menuBar.addMenu('&Help')

        aboutAct = QtWidgets.QAction('&About', Window)
        aboutAct.triggered.connect(self.showAbout)
        helpMenu.addAction(aboutAct)

        self.retranslateUi(Window)
        QtCore.QMetaObject.connectSlotsByName(Window)
        self.ClickButton.clicked.connect(self.On_Click)
        self.ClearButton.clicked.connect(self.ClearSN)
        self.ClearButton.clicked.connect(self.snA1.setFocus)
        self.snA1.returnPressed.connect(self.snA2.setFocus)
        self.snA2.returnPressed.connect(self.snA3.setFocus)
        self.snA3.returnPressed.connect(self.snA4.setFocus)
        self.snA4.returnPressed.connect(self.On_Click)
        self.logThread = LogThread(self)
        self.logThreadRunning = False
        self.loggerQ1 = self.create_logger('ALdfuCh1')
        self.loggerQ2 = self.create_logger('ALdfuCh2')
        self.loggerQ3 = self.create_logger('ALdfuCh3')
        self.loggerQ4 = self.create_logger('ALdfuCh4')
        self.logThread.start()

    def retranslateUi(self, Window):
        _translate = QtCore.QCoreApplication.translate
        Window.setWindowTitle(_translate("Window", "DFU"))
        self.groupBox.setTitle(_translate("Window", "DFU"))
        self.ClickButton.setText(_translate("Window", "Start"))
        self.ClearButton.setText(_translate("attemptWindow", "Clear"))
        self.snA1.setPlaceholderText(_translate("Window", "SN - Slot 1"))
        self.snA2.setPlaceholderText(_translate("Window", "SN - Slot 2"))
        self.snA3.setPlaceholderText(_translate("Window", "SN - Slot 3"))
        self.snA4.setPlaceholderText(_translate("Window", "SN - Slot 4"))
        self.Ch1Result.setPlaceholderText(_translate("Window", "Result - Slot 1"))
        self.Ch2Result.setPlaceholderText(_translate("Window", "Result - Slot 2"))
        self.Ch3Result.setPlaceholderText(_translate("Window", "Result - Slot 3"))
        self.Ch4Result.setPlaceholderText(_translate("Window", "Result - Slot 4"))
        self.groupBox_2.setTitle(_translate("Window", "Log"))

    def preTesting(self):
        self.snA1.setReadOnly(True)
        self.snA2.setReadOnly(True)
        self.snA3.setReadOnly(True)
        self.snA4.setReadOnly(True)
        self.ClickButton.setDisabled(True)
        self.ClearButton.setDisabled(True)
        self.count = 0

    def postTesting(self, count=1):
        self.count -= count
        if self.count != 0:
            return
        self.snA1.setReadOnly(False)
        self.snA2.setReadOnly(False)
        self.snA3.setReadOnly(False)
        self.snA4.setReadOnly(False)
        self.ClickButton.setEnabled(True)
        self.ClearButton.setEnabled(True)

    def validateSN(self):
        snA1 = self.snA1.text().strip()
        snA2 = self.snA2.text().strip()
        snA3 = self.snA3.text().strip()
        snA4 = self.snA4.text().strip()

        validA1 = False
        validA2 = False
        validA3 = False
        validA4 = False
        try:
            snC1T1, t1 = snA1.split('-')
            snC1T2, t2 = snA2.split('-')
            if snC1T1 != snC1T2 or t1 != 'T1' or t2 != 'T2':
                raise ValueError('Slot 1 and Slot 2 SN INVALID')
            validA1 = True
            validA2 = True
        except:
            pass
        try:
            snC2T1, t1 = snA3.split('-')
            snC2T2, t2 = snA4.split('-')
            if snC2T1 != snC2T2 or t1 != 'T1' or t2 != 'T2':
                raise ValueError('Slot 3 and Slot 4 SN INVALID')
            validA3 = True
            validA4 = True
        except:
            pass
        try:
            if snC1T1 == snC2T1:
                raise ValueError('Error: Cable 1 and Cable 2 SN SAME')
        except ValueError:
            validA1 = False
            validA2 = False
            validA3 = False
            validA4 = False
        except:
            pass

        self.snA1.setText(snA1)
        self.snA2.setText(snA2)
        self.snA3.setText(snA3)
        self.snA4.setText(snA4)

        return validA1, validA2, validA3, validA4

    def showAbout(self):
        pwd = os.path.dirname(os.path.realpath(__file__))
        project = json.loads(Path(f'{pwd}/pyproject.json').read_text())
        if 'buildtime' not in project:
            project['buildtime'] = 'Dev'
        QtWidgets.QMessageBox.information(self.window, 'About', (
            f'Version: {project["version"]}\n'
            f'Build Time: {project["buildtime"]}\n'
        ))

    def ClearSN(self):
        self.snA1.clear()
        self.snA2.clear()
        self.snA3.clear()
        self.snA4.clear()

    def On_Click(self):
        if not self.ClickButton.isEnabled():
            return
        self.preTesting()
        validA1, validA2, validA3, validA4 = self.validateSN()
        self.LogTextEdit.setText('')
        self.Ch1Result.setText('')
        self.Ch2Result.setText('')
        self.Ch3Result.setText('')
        self.Ch4Result.setText('')
        # self.SNLeft.setText('lefttest')
        # self.SNRight.setText('righttest')
        # if(MesCheckSN(DB.DbProvider.Mes.operationId,self.SNLeft.toPlainText().strip(),DB.DbProvider.Mes.userid,DB.DbProvider.Mes.host_checksn) == False):
        #     self.LogWrite(f'sn:{self.SNLeft.toPlainText().strip()},mes check fail')
        #     # return
        # if(MesCheckSN(DB.DbProvider.Mes.operationId,self.SNRight.toPlainText().strip(),DB.DbProvider.Mes.userid,DB.DbProvider.Mes.host_checksn) == False):
        #     self.LogWrite(f'sn:{self.SNRight.toPlainText().strip()},mes check fail')
        #     # return
        start_date_time = datetime.datetime.now()
        time_string = start_date_time.strftime("%Y%m%d_%H%M%S")
        self.modify_logger_filename(self.loggerQ1, self.snA1.text(), time_string)
        self.modify_logger_filename(self.loggerQ2, self.snA2.text(), time_string)
        self.modify_logger_filename(self.loggerQ3, self.snA3.text(), time_string)
        self.modify_logger_filename(self.loggerQ4, self.snA4.text(), time_string)
        import os
        pwd = os.path.dirname(os.path.realpath(__file__))
        os.system(f'{pwd}/utb_util -init')

        TestMonitor.TestAbout.Ch1Finished = False
        TestMonitor.TestAbout.Ch2Finished = False
        TestMonitor.TestAbout.Ch3Finished = False
        TestMonitor.TestAbout.Ch4Finished = False
        TestMonitor.TestAbout.Ch1Result = False
        TestMonitor.TestAbout.Ch2Result = False
        TestMonitor.TestAbout.Ch3Result = False
        TestMonitor.TestAbout.Ch4Result = False
        # loggerCh1 = self.create_logger(self.SNLeft.toPlainText().strip()+'-T1')
        # loggerCh2 = self.create_logger(self.SNLeft.toPlainText().strip()+'-T2')
        self.ProcessCh1 = UDPThread(SN=self.snA1.text(), port=3, logger=self.loggerQ1, form=self,
                                    start_date_time=start_date_time, time_string=time_string)
        self.ProcessCh2 = UDPThread2(SN=self.snA2.text(), port=4, logger=self.loggerQ2, form=self,
                                     start_date_time=start_date_time, time_string=time_string)
        self.ProcessCh3 = UDPThread3(SN=self.snA3.text(), port=5, logger=self.loggerQ3, form=self,
                                     start_date_time=start_date_time, time_string=time_string)
        self.ProcessCh4 = UDPThread4(SN=self.snA4.text(), port=6, logger=self.loggerQ4, form=self,
                                     start_date_time=start_date_time, time_string=time_string)

        # self.timer.start(5000)

        if validA1 and validA2:
            self.ProcessCh1.start()
            self.ProcessCh2.start()
            self.count += 2
            self.Ch1Result.setText('Testing')
            self.Ch2Result.setText('Testing')
            self.Ch1Result.setStyleSheet("background-color: yellow;")
            self.Ch2Result.setStyleSheet("background-color: yellow;")
        else:
            self.Ch1Result.setText('SN Error')
            self.Ch1Result.setStyleSheet("background-color: red;")
            self.Ch2Result.setText('SN Error')
            self.Ch2Result.setStyleSheet("background-color: red;")
        if validA3 and validA4:
            self.ProcessCh3.start()
            self.ProcessCh4.start()
            self.count += 2
            self.Ch3Result.setText('Testing')
            self.Ch4Result.setText('Testing')
            self.Ch3Result.setStyleSheet("background-color: yellow;")
            self.Ch4Result.setStyleSheet("background-color: yellow;")
        else:
            self.Ch3Result.setText('SN Error')
            self.Ch3Result.setStyleSheet("background-color: red;")
            self.Ch4Result.setText('SN Error')
            self.Ch4Result.setStyleSheet("background-color: red;")
        
        if not ((validA1 and validA2) or (validA3 and validA4)):
            self.postTesting(count=0)

    def On_Timer(self):
        self.On_Click()

    def LogWrite(self, logstring):
        self.LogTextEdit.append(logstring)

    def Ch1ResultShow(self, Result):
        self.Ch1Result.setText(Result)
        if (Result == 'OK'):
            self.Ch1Result.setStyleSheet("background-color: green;")
        else:
            self.Ch1Result.setStyleSheet("background-color: red;")
        self.postTesting()

    def Ch2ResultShow(self, Result):
        self.Ch2Result.setText(Result)
        if (Result == 'OK'):
            self.Ch2Result.setStyleSheet("background-color: green;")
        else:
            self.Ch2Result.setStyleSheet("background-color: red;")
        self.postTesting()

    def Ch3ResultShow(self, Result):
        self.Ch3Result.setText(Result)
        if (Result == 'OK'):
            self.Ch3Result.setStyleSheet("background-color: green;")
        else:
            self.Ch3Result.setStyleSheet("background-color: red;")
        self.postTesting()

    def Ch4ResultShow(self, Result):
        self.Ch4Result.setText(Result)
        if (Result == 'OK'):
            self.Ch4Result.setStyleSheet("background-color: green;")
        else:
            self.Ch4Result.setStyleSheet("background-color: red;")
        self.postTesting()

    def create_logger(self, classname):
        """
        Create and return a logger
        """
        # Create a logging object
        logger = logging.getLogger(classname)
        logger.setLevel(logging.INFO)

        # create a file handler which logs all levels, including DEBUG
        log_path = "DFU_LOGS.dir"
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        # fh = logging.FileHandler("%s/ALdfu%s_%s.log" % (log_path, log_port, time_string))
        fh = logging.FileHandler(f'{log_path}/UNEXPECTED.log', delay=True)
        fh.setLevel(logging.INFO)
        # create a console handler which logs levels above DEBUG
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Set the formatting
        formatter = logging.Formatter("%(asctime)s [%(name)15s] %(levelname)8s: %(message)s")
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        loghandler = LogQueHandler()
        loghandler.setFormatter(formatter)
        logger.addHandler(loghandler)
        # logger.addHandler(handler)
        # Add the handlers to logger
        logger.addHandler(ch)
        logger.addHandler(fh)
        # logger.info(f'LOG_FILE:{log_file_name}')
        return logger

    def modify_logger_filename(self, logger, newfilename, time_string):
        if isinstance(logger, logging.Logger):
            for handler in logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    log_path = "DFU_LOGS.dir"
                    new_log_name = f'{log_path}/{newfilename}_DFU_{time_string}.log'
                    handler.close()
                    handler.stream = open(new_log_name, 'a')
                    break
