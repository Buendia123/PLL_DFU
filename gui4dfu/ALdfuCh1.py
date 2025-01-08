#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Simplified firmware upgrader script for the Astera Taurus and Taurus1 devices.
"""
import argparse
import datetime
import os
from pathlib import Path
import sys
import time
import traceback
import uuid

import pymssql
from PyQt5.QtCore import *

import DbProvider as DB
import TestMonitor
import firmware_upgrader
from MesTest import MesPostResult
from module_info import *


class UDPThread(QThread):
    Ch1ResultEvent = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(UDPThread, self).__init__()
        self.SN = kwargs.get('SN')
        self.port = kwargs.get('port')
        self.Logger = kwargs.get('logger')
        self.form = kwargs.get('form')
        self.Ch1ResultEvent.connect(self.form.Ch1ResultShow)
        self.start_date_time = kwargs.get('start_date_time')
        self.time_string = kwargs.get('time_string')

    def run(self):
        result = FWUpgradeCh1(self.SN, self.Logger, self.start_date_time, self.time_string, port=self.port)
        if (result == True):
            ret = 'OK'
        else:
            ret = 'NG'
        print('UDPThreadResult' + ret)
        self.Ch1ResultEvent.emit(ret)


def FWUpgradeCh1(SN, Logger, start_date_time, time_string, **kwargs):
    test_id = uuid.uuid4()
    DFU_BIN_PATH = "binaries"
    sn = SN
    try:
        cur_file_loc = os.path.abspath(os.path.dirname(__file__))
        sys.path.append(os.path.join(cur_file_loc, "../../"))
        import ALSetPath
        ALSetPath.set_path_common()
        parser = argparse.ArgumentParser(
            description='Script to perform a DFU on the MCU, MSA, or DSP (or multiple components)')
        parser.add_argument('-device', '-d', action='store', default='linux',
                            help='I2C Device: switch, arduino, aardvark, linux')
        parser.add_argument('-port', '-p', action='store', default=kwargs.get('port'),
                            help='Switch port or serial port number')
        parser.add_argument('-component', '-c', action='store', default='ALL',
                            help='Component to upgrade: MCU, MSA, DSP, SUP, ALL')
        parser.add_argument('-binary', '-b', action='store', default='firmware/EM200QDX.0.52.0',
                            help='Path to binary or folder containing DFU binary')
        parser.add_argument('-version', '-v', action='store_true', default=None,
                            help='Report version number for currently active firmware image')
        parser.add_argument('-switch', '-s', action='store_true', default=None,
                            help='Switch to the slot not currently in use (MCU and MSA only)')
        args = parser.parse_args()
        max_chunk = 64
        log_port = ""
        rc = 0
        if args.device == "arduino":
            import controller.i2c_driver_arduino as i2c_driver
            dev_file = args.port
        elif args.device == "aardvark":
            import controller.i2c_driver_aardvark as i2c_driver
            dev_file = args.port
        elif args.device == "linux":
            import controller.i2c_driver_linux as i2c_driver
            dev_file = args.port
            log_port = f'_port_{args.port}'
            max_chunk = 32  # Linux SMBUS() caps at 32-bytes
        else:
            logger.error("No driver found for {}.".format(args.device))
            # sys.exit(1)
        driver = i2c_driver.I2CDriver(device_filename=dev_file)
        #  AFTER the port determination, for log file naming
        logger = Logger
        modulesn = module_sn_info(driver=driver, logger=logger)
        # if (modulesn == SN) and SN.endswith('-T1'):
        #     logger.info('Ch1 SN Right')
        # else:
        #     logger.info('Ch1 SN Wrong')
        #     return False
        logger.info(f'Starting ALdfu: device {args.device}, dev_file {dev_file}, max_chunk {max_chunk}')

        if args.device == "arduino":
            logger.info("Controller FW version: {}".format(driver.get_driver_object().fw_version()))

        if not args.binary:
            upgrade_file = DFU_BIN_PATH
        else:
            upgrade_file = args.binary
        pwd = os.path.dirname(os.path.realpath(__file__))
        upgrade_file = f'{pwd}/{upgrade_file}'

        args.component = args.component.upper()
        upgrader = firmware_upgrader.FirmwareUpgrader(driver_object=driver, component=args.component, logger=logger)
        #  parameterized and passing max_chunk to the upgrader
        upgrader.chunk_size = max_chunk

        print_version(upgrader, logger)
        if args.version:
            # We already printed the version, so just exit
            pass
        elif args.switch:
            upgrader.switch_slot(args.component)
            upgrader.unlock_system()
            print_version(upgrader, logger)
        else:
            try:
                fw_info_dict = upgrader.upgrade_firmware(upgrade_file, verify=True, skip_status_check=False)
            except firmware_upgrader.FirmwareUpgraderException as err:
                logger.error("FirmwareUpgraderException occurred!")
                logger.info(err.get_message())
                logger.info(err.get_explanation())
                rc = 1
            else:
                print_version(upgrader, logger)

        module_info(driver=driver, logger=logger)

        logger.info('CH1 Module Upgrade OK')
        TestMonitor.TestAbout.Ch1Result = True
        TestMonitor.TestAbout.Ch1Finished = True
        sn = SN

        while (TestMonitor.TestAbout.Ch2Finished != True):
            time.sleep(1)
            continue
        # Mes Communicate 
        if (upload_result_to_database(sn, logger, 'OK', start_date_time, test_id) != True):
            return False
        if (TestMonitor.TestAbout.Ch2Result == True):
            # Mes Pass
            if (MesPostResult(DB.DbProvider.Mes.operationId, sn.split('_')[0], DB.DbProvider.Mes.userid, "PASS",
                              DB.DbProvider.Mes.host_postresult) != True):
                sn_info = sn.split('_')[0]
                logger.info(f'SN:{sn_info},Mes Post Result fail,Check the net connection and Restart')
                return False
            pass
        else:
            # Mes Fail
            if (MesPostResult(DB.DbProvider.Mes.operationId, sn.split('_')[0], DB.DbProvider.Mes.userid, "FAIL",
                              DB.DbProvider.Mes.host_postresult) != True):
                sn_info = sn.split('_')[0]
                logger.info(f'SN:{sn_info},Mes Post Result fail,Check the net connection and Restart')
                return False
            logger.info('Ch1&2:Report to Mes Result = Fail')
            pass
        if (upload_log_to_database(sn, logger, test_id, time_string) != True):
            return False
        return True
    except ImportError:
        traceback.print_exc()
    except:
        sn = SN
        while (TestMonitor.TestAbout.Ch2Finished != True):
            time.sleep(1)
            continue
        logger.info('CH1 Module Upgrade NG')
        logger.info('CH1&2 Report to Mes Result = Fail')
        # Mes Communicate
        # Mes Fail
        if (upload_result_to_database(sn, logger, 'NG', start_date_time, test_id) != True):
            return False
        if (MesPostResult(DB.DbProvider.Mes.operationId, sn.split('_')[0], DB.DbProvider.Mes.userid, "FAIL",
                          DB.DbProvider.Mes.host_postresult) != True):
            sn_info = sn.split('_')[0]
            logger.info(f'SN:{sn_info},Mes Post Result fail,Check the net connection and Restart')
            return False
        upload_log_to_database(sn, logger, test_id, time_string)
        return False


def print_version(upgrader, logger):
    """
    Prints version information for all components
    """
    # for component in ["MCU", "MSA", "DSP"]:
    for component in upgrader.components:
        version = upgrader.fw_info[component]["version"]
        logger.info("###########################")
        logger.info("Component: {}".format(component.upper()))
        logger.info("Version: {}.{}.{}".format(version[0], version[1], (version[2] << 8) | version[3]))
        active_slot = upgrader.get_active_image(component)
        if active_slot:
            logger.info("Slot: {}".format(active_slot))

    logger.info("###########################")


def read_file_as_binary(file_path):
    try:
        with open(file_path, 'rb') as file:
            binary_data = file.read()
        return binary_data
    except Exception as e:
        raise Exception(f"Failed to read file '{file_path}': {str(e)}")


def upload_result_to_database(SN, logger, Result, start_date_time, test_id):
    try:
        conn = pymssql.connect(DB.DbProvider.Db.server, DB.DbProvider.Db.user, DB.DbProvider.Db.password,
                               DB.DbProvider.Db.database)
        cursor = conn.cursor()
        result = Result
        Date = datetime.datetime.now()
        sqltask = f"INSERT INTO {DB.DbProvider.Db.resulttable} (Id, TestBeginTime, TestEndTime, TestUserId, SN, TestResult, TestItem, TestDetail) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sqltask, (str(test_id), start_date_time, Date, 'TestUser', SN, result, 'DFU', 'Cable.Firmware.Version=0.52;'))
        conn.commit()
        time.sleep(2)
        logger.info(f"{SN}:upload result to database success,test result:{Result}")
        return True
    except:
        logger.info(f"{SN}:upload result to database fail,test result:{Result}")


def upload_log_to_database(sn, logger, test_id, time_string):
    try:
        # 连接到 SQL Server 数据库
        conn = pymssql.connect(DB.DbProvider.Db.server, DB.DbProvider.Db.user, DB.DbProvider.Db.password,
                               DB.DbProvider.Db.database)
        cursor = conn.cursor()

        # 获取当前时间
        test_time = datetime.datetime.now()

        # 读取日志文件并将其转换为二进制数据
        logname = f'{sn}_DFU_{time_string}.log'
        log_file_path = f'./DFU_LOGS.dir/{logname}'  # 替换为实际的文件路径
        log_image = read_file_as_binary(log_file_path)

        # 插入记录到数据库表
        cursor.execute(
            f"INSERT INTO {DB.DbProvider.Db.logtable} (Id, UTPTestID, SN, LogFileName, TestLog, TestTime) VALUES (%s, %s, %s, %s, %s, %s)",
            (str(uuid.uuid4()), str(test_id), sn, logname, log_image, test_time))

        # 提交更改并关闭连接
        conn.commit()
        conn.close()

        Path(log_file_path).unlink()

        logger.info("Log upload successful.")

        return True

    except Exception as e:
        logger.info("Log upload failed:", str(e))


if __name__ == "__main__":
    """
    Entry point
    """
    FWUpgradeCh1('sn', port=3, Logger=None)
    # Parse the arguments

    #  2023-Aug-14: CHL
    #  Adding max_chunk as a param, default 64
