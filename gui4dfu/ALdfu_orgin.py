#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Simplified firmware upgrader script for the Astera Taurus and Taurus1 devices.
"""
import argparse
import datetime
import logging
import os
import sys

import firmware_upgrader
from module_info import *

DFU_BIN_PATH = "binaries"

__eeprom_map_cs8000 = {1: 37, 2: 38, 3: 35, 4: 36, 5: 41, 6: 40, 7: 50, 8: 39, 9: 47, 10: 46, 11: 49, 12: 45, 13: 44,
                       14: 48,
                       15: 42, 16: 43, 17: 60, 18: 66, 19: 63, 20: 59, 21: 64, 22: 61, 23: 56, 24: 65, 25: 62, 26: 57,
                       27: 51,
                       28: 58, 29: 53, 30: 55, 31: 54, 32: 52}

__eeprom_map_cs8260 = {1: 101, 2: 102, 3: 103, 4: 104, 5: 105, 6: 106, 7: 107, 8: 108, 9: 109, 10: 110, 11: 111,
                       12: 112, 13: 113, 14: 114,
                       15: 115, 16: 116, 17: 117, 18: 118, 19: 119, 20: 120, 21: 121, 22: 122, 23: 123, 24: 124,
                       25: 125, 26: 126, 27: 127,
                       28: 128, 29: 129, 30: 130, 31: 131, 32: 132}


def create_logger(log_port):
    """
    Create and return a logger
    """
    # Create a logging object
    logger = logging.getLogger('ALdfu')
    logger.setLevel(logging.INFO)
    # create a file handler which logs all levels, including DEBUG
    now = datetime.datetime.now()
    time_string = now.strftime("%Y%m%d_%H%M%S")

    log_path = "DFU_LOGS.dir"
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log_file_name = "%s/ALdfu%s_%s.log" % (log_path, log_port, time_string)
    # fh = logging.FileHandler("%s/ALdfu%s_%s.log" % (log_path, log_port, time_string))
    fh = logging.FileHandler(log_file_name)
    fh.setLevel(logging.INFO)
    # create a console handler which logs levels above DEBUG
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Set the formatting
    formatter = logging.Formatter("%(asctime)s [%(name)15s] %(levelname)8s: %(message)s")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.info(f'LOG_FILE:{log_file_name}')

    return logger


def print_version(upgrader):
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


if __name__ == "__main__":
    os.system('cd /home/volex123/下载/dfu_20230830/diag_bin')
    os.system('./utb_util -init')
    import time

    time.sleep(0.5)
    """
    Entry point
    """
    try:
        # Get the path to the I2C drivers
        cur_file_loc = os.path.abspath(os.path.dirname(__file__))
        sys.path.append(os.path.join(cur_file_loc, "../../"))
        import ALSetPath

        ALSetPath.set_path_common()
    except ImportError:
        # Outside of the SDK, all drivers will be expected to be
        # in the same folder as this script
        pass

    # Parse the arguments
    parser = argparse.ArgumentParser(
        description='Script to perform a DFU on the MCU, MSA, or DSP (or multiple components)')
    parser.add_argument('-device', '-d', action='store', default='linux',
                        help='I2C Device: switch, arduino, aardvark, linux')
    parser.add_argument('-port', '-p', action='store', default='3', help='Switch port or serial port number')
    parser.add_argument('-component', '-c', action='store', default='all',
                        help='Component to upgrade: MCU, MSA, DSP, SUP, ALL')
    parser.add_argument('-binary', '-b', action='store', default='firmware/EM200QDX.0.52.0',
                        help='Path to binary or folder containing DFU binary')
    parser.add_argument('-version', '-v', action='store_true', default=None,
                        help='Report version number for currently active firmware image')
    parser.add_argument('-switch', '-s', action='store_true', default=None,
                        help='Switch to the slot not currently in use (MCU and MSA only)')
    args = parser.parse_args()

    #  2023-Aug-14: CHL
    #  Adding max_chunk as a param, default 64
    max_chunk = 64
    log_port = ""
    rc = 0
    if args.device == "arduino":
        import i2c_driver_arduino as i2c_driver

        dev_file = args.port
    elif args.device == "aardvark":
        import i2c_driver_aardvark as i2c_driver

        dev_file = args.port
    elif args.device == "linux":
        import i2c_driver_linux as i2c_driver

        dev_file = args.port
        log_port = f'_port_{args.port}'
        max_chunk = 32  # Linux SMBUS() caps at 32-bytes
    elif args.device == "switch":
        if args.port is None:
            raise Exception("Error: No port specified.")
        import i2c_driver_switch as i2c_driver

        port = int(args.port)
        dev_file_cs8000 = "/sys/devices/platform/soc/fd8be100.spi_aux/spi_master/spi1/spi1.0/i2c-34/i2c-" + str(
            __eeprom_map_cs8000[port]) + "/" + str(__eeprom_map_cs8000[port]) + "-0050/eeprom"
        dev_file_cs8260 = "/sys/devices/platform/soc/fd820000.pcie-external1/pci0002:00/0002:00:00.0/0002:01:00.0/i2c-" + str(
            __eeprom_map_cs8260[port]) + "/" + str(__eeprom_map_cs8260[port]) + "-0050/eeprom"
        if (os.path.isfile(dev_file_cs8000)):
            dev_file = dev_file_cs8000
        elif (os.path.isfile(dev_file_cs8260)):
            dev_file = dev_file_cs8260
    else:
        logger.error("No driver found for {}.".format(args.device))
        sys.exit(1)

    #  AFTER the port determination, for log file naming
    logger = create_logger(log_port)
    logger.info(f'Starting ALdfu: device {args.device}, dev_file {dev_file}, max_chunk {max_chunk}')

    driver = i2c_driver.I2CDriver(device_filename=dev_file)

    if args.device == "arduino":
        logger.info("Controller FW version: {}".format(driver.get_driver_object().fw_version()))

    if not args.binary:
        upgrade_file = DFU_BIN_PATH
    else:
        upgrade_file = args.binary

    args.component = args.component.upper()
    upgrader = firmware_upgrader.FirmwareUpgrader(driver_object=driver, component=args.component, logger=logger)
    #  parameterized and passing max_chunk to the upgrader
    upgrader.chunk_size = max_chunk

    print_version(upgrader)
    rc = 0
    if args.version:
        # We already printed the version, so just exit
        pass
    elif args.switch:
        upgrader.switch_slot(args.component)
        upgrader.unlock_system()
        print_version(upgrader)
    else:
        try:
            fw_info_dict = upgrader.upgrade_firmware(upgrade_file, verify=True, skip_status_check=False)
        except firmware_upgrader.FirmwareUpgraderException as err:
            logger.error("FirmwareUpgraderException occurred!")
            logger.info(err.get_message())
            logger.info(err.get_explanation())
            rc = 1
        else:
            print_version(upgrader)

    module_info(driver=driver, logger=logger)

    sys.exit(rc)
