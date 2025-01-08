import logging
import queue
import time

from PyQt5.QtCore import *


class LogThread(QThread):
    def __init__(self, form, *args, **kwargs):
        super(LogThread, self).__init__()
        self.logProvider = LogProvider(form)

    def run(self):
        self.logProvider.LogQueOut()


class LogThreadControl(QThread):
    def __init__(self, Form):
        super(LogThreadControl, self).__init__()
        self.Form = Form

    def run(self):
        LogProvider.LogQueOutToControl(self.Form)


class LogProvider(QObject):
    LogEvent = pyqtSignal(str)

    def __init__(self, form):
        super(LogProvider, self).__init__()
        self.LogEvent.connect(form.LogWrite)

    LogQue = queue.Queue()

    def LogQueIN(logstring):
        LogProvider.LogQue.put(logstring)

    def LogQueOut(self):
        # LogProvider.LogEvent.connect(form.LogWrite)
        while True:
            if (LogProvider.LogQue.empty == True):
                time.sleep(0.1)
                continue
            else:
                logstring = LogProvider.LogQue.get()
                self.LogEvent.emit(logstring)
                continue

    def LogQueOutToControl(Form):
        while True:
            if (LogProvider.LogQue.empty == True):
                time.sleep(1)
                continue
            else:
                logstring = LogProvider.LogQue.get()
                Form.LogTextEdit.append(logstring)
                continue


class LogQueHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        try:
            msg = self.format(record)
            LogProvider.LogQueIN(msg)
        except RecursionError:  # See issue 36272
            raise
        except Exception:
            self.handleError(record)
    # def create_logger(log_port = 1):
#     """
#     Create and return a logger
#     """
#     # Create a logging object
#     logger = logging.getLogger('ALdfu')
#     logger.setLevel(logging.INFO)
#     # create a file handler which logs all levels, including DEBUG
#     now = datetime.datetime.now()
#     time_string = now.strftime("%Y%m%d_%H%M%S")

#     log_path = "DFU_LOGS.dir"
#     if not os.path.exists(log_path):
#         os.makedirs(log_path)
#     log_file_name = "%s/ALdfu%s_%s.log" % (log_path, log_port, time_string)
#     #fh = logging.FileHandler("%s/ALdfu%s_%s.log" % (log_path, log_port, time_string))
#     fh = logging.FileHandler(log_file_name)
#     fh.setLevel(logging.INFO)
#     # create a console handler which logs levels above DEBUG
#     ch = logging.StreamHandler()
#     ch.setLevel(logging.INFO)

#     # Set the formatting
#     formatter = logging.Formatter("%(asctime)s [%(name)15s] %(levelname)8s: %(message)s")
#     ch.setFormatter(formatter)
#     fh.setFormatter(formatter)
#     loghandler = LogQueHandler()
#     logger.addHandler(loghandler)
#     # Add the handlers to logger
#     logger.addHandler(ch)
#     logger.addHandler(fh)
#     logger.info(f'LOG_FILE:{log_file_name}')

#     return logger

# logThread =  LogThread()
# taskLog = logThread.start()
# logger = create_logger()
# while True:
#     # LogProvider.LogQueIN('INSERT 1 Log')

#     logger.info('INSERT 1 Log')
#     time.sleep(1)
