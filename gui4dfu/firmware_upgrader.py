"""
This module provides a firmware upgrader wrapper for the
Astera Taurus module.

This module conforms to the custom API provided by a client.
This module must be compatible with Python 2.7 and Python 3.9
"""
import binascii
import datetime
import fnmatch
import logging
import os
import struct
import sys
import time

logger = logging.getLogger(__name__)

RESET_DELAY = 1

MANUFACTURER_PASSWORD = [0x88, 0x88, 0x88, 0x88]


###################
# Exception Class #
###################

class FirmwareUpgraderException(BaseException):
    """
    Firmware Upgrader specific exception type.

    This type extends generic Exception type to provide more details regarding
    the exceptions raised during optics the upgrade process.
    """
    detailed_error_message = ""
    error_explanation = ""
    filename = ""

    def __init__(self, detailed_error_message):
        """
        Constructor

        Args:
            detailed_error_message: string contains the detailed error message
                in regards to raised exception
        """
        self.detailed_error_message = detailed_error_message

        self.__parse_error_msg()

        if sys.version_info[:2] == (2, 7):
            super(FirmwareUpgraderException, self).__init__(self.detailed_error_message)
        elif sys.version_info[0] == 3:
            super().__init__(self.detailed_error_message)
        else:
            raise Exception("Unsupported Python version: {}, requires 2.7 or 3.x".format(sys.version_info))

    def get_message(self):
        """
        Returns the detailed error message that has been captured
        """
        return self.detailed_error_message

    def get_explanation(self):
        """
        Returns an explanation of the error message.
        """
        return self.error_explanation

    def __parse_error_msg(self):
        if "0102" in self.detailed_error_message:
            self.error_explanation = "Previous DFU aborted! Please restart DFU."
        elif "0101" in self.detailed_error_message:
            if "0x7f" in self.detailed_error_message:
                self.error_explanation = "Incorrect image slot. Provide binary for other image slot."
            elif "0x7c" in self.detailed_error_message:
                self.error_explanation = "Image is corrupted!"
            elif "0x46" in self.detailed_error_message:
                self.error_explanation = "No password or incorrect password."


class FirmwareUpgrader():
    """
    Base class for the firmware upgrader.

    An object of this type will be called for probing the device to retrieve
    identifier information and also to upgrade firmware
    """
    upgrader_version = (1, 4)
    skip_status_check = False
    module_state = None
    dfu_attempts = 3

    def __init__(self, driver_object, component, logger=None):
        """
        Constructor.

        Args:
            driver_object: I2CDriver: driver object for communication
            component: string: one of the following: ["MCU", "MSA", "DSP", "SUP", "ALL"]
        Returns:
            An object of type 'FirmwareUpgrader' for a given component
        Raises:
            FWUpgraderException: An error occurred during the object creation
        """
        self.fw_info = {
            "MCU": {
                "component": "MCU",
                "version": "0.0.0",
                "major": 0,
                "minor": 0,
                "build": 0,
                "active_image": "A",
                "crc": bytearray(),
                "filename": None
            },
            "MSA": {
                "component": "MSA",
                "version": "0.0.0",
                "major": 0,
                "minor": 0,
                "build": 0,
                "active_image": "A",
                "crc": bytearray(),
                "filename": None
            },
            "DSP": {
                "component": "DSP",
                "version": "0.0.0",
                "major": 0,
                "minor": 0,
                "build": 0,
                "active_image": None,
                "crc": bytearray(),
                "filename": None
            }
        }

        self.i2c_driver = driver_object
        self.group = component.upper()
        self.components = []

        # The arguments from the user are group designations, rather than actual components
        if self.group == "ALL":
            self.components = ["MCU", "MSA", "DSP"]
        elif self.group == "MCU":
            self.components = ["MCU", "MSA"]
        elif self.group == "SUP":
            self.components = ["MCU"]
        else:
            self.components = [self.group]

        if logger is None:
            self.logger = logging.getLogger('firmware_upgrader')
            self.logger.setLevel(logging.DEBUG)
            # create a file handler which logs all levels, including DEBUG
            log_path = "al_logs"
            if not os.path.exists(log_path):
                os.makedirs(log_path)
            now = datetime.datetime.now()
            time_string = now.strftime("%Y%m%d_%H%M%S")
            fh = logging.FileHandler("%s//AL_firmware_upgrader_%s_%s.log" % (log_path, self.group, time_string))
            fh.setLevel(logging.DEBUG)
            # create a console handler which logs levels above DEBUG
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            # create a formatter and add it to the handlers
            formatter = logging.Formatter("%(asctime)s [%(name)15s] %(levelname)8s: %(message)s")

            ch.setFormatter(formatter)
            fh.setFormatter(formatter)
            # Add the handlers to logger
            self.logger.addHandler(ch)
            self.logger.addHandler(fh)
        else:
            self.logger = logger

        self.chunk_size = 64

        # Collect the starting module state to return to after DFU is complete
        try:
            self.module_state = self.get_module_status()
        except:
            raise FirmwareUpgraderException("E999: I2C communication check failed.")

        if self.read_int(2, 0x00) & 0x80:
            raise FirmwareUpgraderException(
                "E000: Firmware Upgrade not supported on target. Please check if module is Active.")

        # Unlock the system and initialize the firmware info dictionary
        self.unlock_system()
        if "DSP" in self.components:
            self.set_low_power_mode(False, wait=True)
        self.update_firmware_info()

    def get_upgrader_version(self):
        """
        Returns the firmware upgrader version

        Returns:
            integer tuple: major version, minor version
        """
        return self.upgrader_version

    def get_driver(self):
        """
        Returns the current driver
        """
        return self.i2c_driver

    def get_components(self):
        """
        Returns the component group
        """
        return self.components

    def upgrade_firmware(self, upgrade_file, verify=False, **kwargs):
        """
        Upgrades firmware of specified component on the device.

        Firmware components are expected to conform to the following naming
        pattern:
            MCU: <TARGET>_module_fw_v<MAJOR_VER>.<MINOR_VER>.<BUILD>_<A/B>.bin
            MSA: <VARIANT>_cmis_fw_v<MAJOR_VER>.<MINOR_VER>.<BUILD>.bin
            DSP: <TARGET>_retimer_fw_v<MAJOR_VER>.<MINOR_VER>.<BUILD>.bin

        Args:
            upgrade_file: String: path to folder containing upgrade binaries
            verify: boolean: if true, needs to verify the firmware version after upgrade
            **kwargs: dict: vendor specific additional helper items
        Returns:
            A dictionary with upgraded firmware version and CRC info
            Example: {'version': None, 'crc': None}
        Raises:
            FirmwareUpgraderException: An error occurred during the upgrade process
        """

        def upgrade_procedure():
            expected_versions = {
                "MCU": (0, 0, 0),
                "MSA": (0, 0, 0),
                "DSP": (0, 0, 0)
            }
            if "DSP" in self.components:
                self.set_low_power_mode(False, wait=True)

            # Initialize the version info
            self.update_firmware_info()

            if not os.path.exists(upgrade_file):
                self.logger.error("Invalid firmware location.")
                raise FirmwareUpgraderException("E001: Invalid firmware location.")

            # Remove the filename and determine appropriate file internally
            if os.path.isdir(upgrade_file):
                fw_file = upgrade_file
            else:
                fw_file = os.path.dirname(upgrade_file)

            if os.path.isdir(fw_file):
                if self.fw_info["MCU"]["active_image"] == "A":
                    mcu_file = self._find("*_module_fw_v*_b.bin", fw_file)
                elif self.fw_info["MCU"]["active_image"] == "B":
                    mcu_file = self._find("*_module_fw_v*_a.bin", fw_file)
                msa_file = self._find("*_cmis_fw*_v*.bin", fw_file)
                dsp_file = self._find("*_retimer_fw_v*.bin", fw_file)

                self.fw_info["MCU"]["filename"] = os.path.abspath(mcu_file) if mcu_file else None
                self.fw_info["MSA"]["filename"] = os.path.abspath(msa_file) if msa_file else None
                self.fw_info["DSP"]["filename"] = os.path.abspath(dsp_file) if dsp_file else None
            else:
                raise FirmwareUpgraderException("E001: Invalid firmware location.")

            # Do a DFU Abort in case a previous DFU was cut off during CDB 0103 transfers
            self.dfu_abort()

            for component in self.components:
                if component == "MCU":
                    file = self.fw_info["MCU"]["filename"]
                elif component == "MSA":
                    file = self.fw_info["MSA"]["filename"]
                elif component == "DSP":
                    file = self.fw_info["DSP"]["filename"]
                else:
                    FirmwareUpgraderException("E008: Invalid component.")

                self.logger.info("Initiating FW upgrade using binary file: %s" % (file))

                if verify:
                    # Get the version information from the provided binary
                    header = HeaderV1(file)
                    header.load()
                    exp_major, exp_minor, exp_build = header.get_version()
                    expected_versions[component] = (exp_major, exp_minor, exp_build)

                    # Hold onto original slot for verification purposes
                    if component in ["MCU", "MSA"]:
                        self.fw_info[component]["old_slot"] = self.get_active_image(component)

                # Reformat the CRC value to a bytearray
                crc_value = self.dfu(file)
                self.fw_info[component]["crc"].append((crc_value >> 24) & 0xFF)
                self.fw_info[component]["crc"].append((crc_value >> 16) & 0xFF)
                self.fw_info[component]["crc"].append((crc_value >> 8) & 0xFF)
                self.fw_info[component]["crc"].append(crc_value & 0xFF)
                self.logger.info("File CRC: 0x%X", crc_value)

            # Restart
            if "MCU" in self.components:
                self.dfu_restart()
            else:
                self.reset_module()

            time.sleep(RESET_DELAY)
            self.unlock_system()

            if "MCU" in self.components:
                self.dfu_commit()

            if "DSP" in self.components:
                # Set the Taurus Firmware Load flag
                self.write_int(221, 0xF0, 1)

                self.set_low_power_mode(False)

                # Wait for the DSP DFU to complete
                if not self._poll_retimer():
                    raise FirmwareUpgraderException("Retimer DFU timed out.")

            # Update the firmware version
            self.update_firmware_info()

            # Return the system to Low Power
            if self.module_state != self.get_module_status():
                if self.module_state == 1:
                    self.set_low_power_mode(True)
                else:
                    self.set_low_power_mode(False, wait=True)

            for component in self.components:
                new_version = (
                self.fw_info[component]["major"], self.fw_info[component]["minor"], self.fw_info[component]["build"])

                if verify:
                    # Make sure the slot has changed
                    if component in ["MCU", "MSA"]:
                        if self.fw_info[component]["old_slot"] == self.fw_info[component]["active_image"]:
                            self.logger.error("Component: {}, Old Slot: {}, New Slot: {}".format(
                                component, self.fw_info[component]["old_slot"], self.fw_info[component]["active_image"]
                            ))
                            raise FirmwareUpgraderException("E002: Version Verification failed. Incorrect slot.")

                    if not self._assert_expected_version(expected_versions[component], new_version):
                        print("Expected Version : {}.{}.{}".format(expected_versions[component][0],
                                                                   expected_versions[component][1],
                                                                   expected_versions[component][2]))
                        print("New Version : {}.{}.{}".format(new_version[0], new_version[1], new_version[2]))
                        raise FirmwareUpgraderException("E002: Version Verification failed. Unexpected version.")
                    else:
                        self.logger.info("{}: verified.".format(component.upper()))

        # Check for vendor options
        if "skip_status_check" in kwargs:
            if kwargs["skip_status_check"]:
                self.skip_status_check = True
            else:
                self.skip_status_check = False

        # Attempt DFU 3 times and report last exception upon failure
        attempts_remaining = self.dfu_attempts
        error_occurred = False
        exception = None

        while attempts_remaining > 0:
            try:
                upgrade_procedure()
            except FirmwareUpgraderException as exc:
                exception = exc
                error_occurred = True

                msg = exc.get_message()
                explanation = exc.get_explanation()

                self.logger.error("Error: {}".format(msg))
                self.logger.error("Reason: {}".format(explanation))
                self.logger.error("Attempts remaining: {}".format(attempts_remaining - 1))
            except Exception as exc:
                exception = exc
                error_occurred = True

                self.logger.error("Error occurred during DFU: {}".format(exc.__str__()))
                self.logger.error("Attempts remaining: {}".format(attempts_remaining - 1))
            else:
                error_occurred = False
                attempts_remaining = 0
            finally:
                attempts_remaining -= 1

        if error_occurred:
            raise exception
        else:
            if self.group in ["MCU", "SUP", "ALL"]:
                return self.fw_info["MCU"]
            else:
                return self.fw_info[self.group]

    def update_firmware_info(self):
        """
        Updates the firmware info dictionary

        NOTE: DSP firmware will be invalid if firmware info updated in Low Power Mode.
        """
        # if 3 != self.get_module_status():
        #     logger.warning("Module in Low Power Mode. Retimer version info invalid.")

        # Request the firmware info via CDB
        self.cdb_cmd(0x100)

        # Read the firmware flags to determine running image
        firmware_flags = self.read_int(136, 0x9F)
        a_flags = firmware_flags & 0x0F
        b_flags = (firmware_flags >> 4) & 0x0F

        if a_flags & 0x01:
            self.fw_info["MCU"]["active_image"] = "A"
        elif b_flags & 0x01:
            self.fw_info["MCU"]["active_image"] = "B"
        else:
            raise FirmwareUpgraderException("E003: Invalid firmware flags.")

        # We are using the CMIS spec defined version registers here for backward
        # compatibility, but these versions should match those in Page 01h, bytes
        # 128 and 129
        self.fw_info["MCU"]["major"] = self.read_int(39, 0x00)
        self.fw_info["MCU"]["minor"] = self.read_int(40, 0x00)

        # Workaround for versions using incorrect build version register (TAURUS-599)
        if self.mcu_major == 0 and self.mcu_minor < 23:
            self.fw_info["MCU"]["build"] = (self.read_int(41, 0x00) << 8) | self.read_int(42, 0x00)
        else:
            self.fw_info["MCU"]["build"] = (self.read_int(64, 0x00) << 8) | self.read_int(65, 0x00)

        self.fw_info["DSP"]["major"] = self.read_int(194, 0x01)
        self.fw_info["DSP"]["minor"] = self.read_int(195, 0x01)
        self.fw_info["DSP"]["build"] = (self.read_int(197, 0x01) << 8) | self.read_int(196, 0x01)

        # Workaround for updates to firmware locations
        if self.mcu_major == 0 and self.mcu_minor < 27:
            self.fw_info["MSA"]["major"] = self.read_int(191, 0x01)
            self.fw_info["MSA"]["minor"] = self.read_int(192, 0x01)
            self.fw_info["MSA"]["build"] = (0 << 8) | self.read_int(193, 0x01)
        else:
            self.fw_info["MSA"]["major"] = self.read_int(204, 0x01)
            self.fw_info["MSA"]["minor"] = self.read_int(205, 0x01)
            self.fw_info["MSA"]["build"] = (0 << 8) | self.read_int(206, 0x01)

        msa_slot = self.read_int(202, 0x01)
        if msa_slot & 0x01:
            self.fw_info["MSA"]["active_image"] = "A"
        elif msa_slot & 0x02:
            self.fw_info["MSA"]["active_image"] = "B"
        else:
            raise FirmwareUpgraderException("E003: Invalid firmware flags.")

        # Update version byte arrays
        self.fw_info["MCU"]["version"] = bytearray([
            self.fw_info["MCU"]["major"],
            self.fw_info["MCU"]["minor"],
            (self.fw_info["MCU"]["build"] >> 8) & 0xFF,
            self.fw_info["MCU"]["build"] & 0xFF
        ])
        self.fw_info["MSA"]["version"] = bytearray([
            self.fw_info["MSA"]["major"],
            self.fw_info["MSA"]["minor"],
            (self.fw_info["MSA"]["build"] >> 8) & 0xFF,
            self.fw_info["MSA"]["build"] & 0xFF
        ])
        self.fw_info["DSP"]["version"] = bytearray([
            self.fw_info["DSP"]["major"],
            self.fw_info["DSP"]["minor"],
            (self.fw_info["DSP"]["build"] >> 8) & 0xFF,
            self.fw_info["DSP"]["build"] & 0xFF
        ])

    def get_firmware_version(self, component=None):
        """
        Returns the current firmware version as a bytearray. If no component is supplied,
        a dictionary of all component version bytearrays is returned.

        Raises:
            FirmwareUpgraderException: An error occurred during the retrieval process
        """
        if not component:
            if self.group in ["MCU", "SUP", "ALL"]:
                component = "MCU"
            else:
                component = self.group
        else:
            component = component.upper()

        self.update_firmware_info()

        return self.fw_info[component]["version"]

    def get_active_image(self, component=None):
        """
        Returns the active firmware image of the component (A or B)

        Raises:
            FirmwareUpgraderException: An error occurred during the retrieval process
        """
        if not component:
            if self.group in ["MCU", "SUP", "ALL"]:
                component = "MCU"
            else:
                component = self.group
        else:
            component = component.upper()

        return self.fw_info[component]["active_image"]

    def get_crc(self, component=None):
        """
        Returns the CRC of the latest image
        """
        if not component:
            if self.group in ["MCU", "SUP", "ALL"]:
                component = "MCU"
            else:
                component = self.group
        else:
            component = component.upper()

        return self.fw_info[component]["crc"]

    def get_file_header_info(self, file):
        """
        Returns a dictionary of the header info for the provided file.

        Args:
            file: string: DFU binary path
        """
        image = HeaderV1(file)
        image.load()
        _header_info = {
            "target": image.get_target(),
            "device_id": image.get_id(),
            "version": image.get_version(),
            "crc": image.get_crc()
        }

        return _header_info

    def get_dfu_filename(self, component=None):
        """
        Returns the full path to the file used in the last DFU attempt.
        """
        if not component:
            if self.group in ["MCU", "SUP", "ALL"]:
                component = "MCU"
            else:
                component = self.group
        else:
            component = component.upper()

        return self.fw_info[component]["filename"]

    def reset_module(self):
        """
        Perform a full software reset to the bootloader
        """
        self.i2c_driver.write(26, bytearray([0x08]), 0x00, 0)

    def get_module_status(self):
        """
        Get the current module status

        1 - ModuleLowPwr State
        2 - ModulePwrUp State
        3 - ModuleReady State
        4 - ModulePwrDn State
        5 - Fault State
        """
        val = self.i2c_driver.read(3, 0x00)
        if isinstance(val, list) or isinstance(val, bytearray):
            val = val[0]

        return (val & 0x0E) >> 1

    def set_low_power_mode(self, lp_mode=True, wait=False):
        """
        Move the module to Low Power Mode

        Args:
          lp_mode: bool: True to move to Low Power Mode, False to move to Normal mode
          wait: bool: Block until target state is reached
        """
        # self.i2c_driver.write(26, bytearray([0x00]), 0x00)
        module_controls = self.read_int(26, 0x00)

        if lp_mode:
            new_val = module_controls | 0x10
            target_state = 1
        else:
            new_val = module_controls & ~0x10
            target_state = 3

        self.write_int(26, 0x00, new_val)

        if wait:
            for _ in range(8):
                if self.get_module_status() == target_state:
                    return True
                time.sleep(1)
            return False
        else:
            return True

    ####################
    # Helper functions #
    ####################

    def dfu_abort(self):
        """
        Send a 0102 abort firmware download command.
        """
        try:
            self.cdb_cmd(0x0102)
        except FirmwareUpgraderException as exc:
            logger.error("Previous attempt failed with: {}".format(exc.get_message()))

    def dfu_restart(self, delay_ms=100):
        """
        Send a 0109 run image command with the desired delay.

        Args:
            delay_ms: int: Delay period in milliseconds
        """

        def format_0109(reset_mode, reset_delay):
            """
            Return a byte array containing the reset mode and reset delay 0109
            command.
            """
            # Struct format for the LPL data of a 0103 command
            #   >   Big endian
            #   B   Reserved (1 byte)
            #   B   Reset mode (1 byte)
            #   H   Reset delay (2 bytes)
            format_str = ">BBH"

            return struct.pack(format_str, 0, reset_mode, reset_delay)

        # Send Run image
        self.logger.info("Resetting ...")
        self.cdb_cmd(0x0109, lpl=format_0109(0, delay_ms))

    def dfu_commit(self):
        """
        Send a 010A commit image command.
        """
        self.logger.info("Committing image.")
        self.cdb_cmd(0x010A)

    def switch_slot(self, component=None):
        """
        Switch to the unused firmware/slot (MCU and MSA)
        """
        if not component:
            if self.group in ["MCU", "SUP", "ALL"]:
                component = "MCU"
            else:
                component = self.group

        if component == "MCU":
            self.dfu_restart()
        elif component == "MSA":
            curr_slot = chr(self.read_int(149, 0xF0))
            new_slot = 'B' if curr_slot == 'A' else 'A'
            self.write_int(149, 0xF0, ord(new_slot))
            self.reset_module()
        else:
            return

        time.sleep(RESET_DELAY)
        self.set_low_power_mode(False, wait=True)

    def unlock_system(self):
        """
        Unlock the module to enable the CDB commands.
        """
        OPERATION_MODE_DEBUG = 0x09

        # Enter the password
        self.write_int(122, 0x00, MANUFACTURER_PASSWORD)

        self.mcu_major = self.read_int(39, 0x00)
        self.mcu_minor = self.read_int(40, 0x00)

        # Workaround for change in operation mode location
        # module_fw_v0.27.0 on commit 5f8c7c3190c PR#158 in TAURUS/taurus_sw from feature/TAURUS-965-move-aws-operating-control-from-pg-b0-to-pg-d0 to dev
        if self.mcu_major == 0 and self.mcu_minor < 27:
            op_mode_page = 0xB0
        else:
            op_mode_page = 0xD0

        self.write_int(254, op_mode_page, OPERATION_MODE_DEBUG)

        # If system is still locked, the password was incorrect.
        if self.read_int(254, op_mode_page) != OPERATION_MODE_DEBUG:
            self.logger.error("Error: Incorrect password.")

    def lock_system(self):
        """
        lock the module to disable the CDB commands.
        """
        self.write_int(122, 0x0, [0x00, 0x00, 0x00, 0x00])

    def cdb_cmd(self, cmd=0x0, lpl=bytes(0), rlpl_len=0, verbose=False):
        """
        Send a CDB command to the given I2C peripheral address.

        Args:
            cmd: int: CDB command
            lpl: list: LPL data packet
            rlpl_len: int: RLPL length
            verbose: bool: Display verbose output
        """

        def cdb_chk_code(data):
            """
            Given an iterable, return the 1's complement sum of the values.

            Args:
                data: list: Data to calculate the CDB check code
            """
            total = 0
            for i in bytearray(data):
                total += i
            # Convert to 1's complement by subtracting from the largest byte.  We
            # do this so that the number returned is positive in the range of 0 to
            # 255.  That allows for the correct convertsion to hex for transmission.
            chk_code = 255 - (total & 0x00FF)

            return chk_code

        def cdb_status(block=1):
            """
            Return the CDB status for the given inteface.

            Args:
                block: int: CDB block (1 or 2)
            """
            # Check the CDB status flag for a given block
            if block == 1:
                status = self.read_int(37, 0x0)
            elif block == 2:
                status = self.read_int(38, 0x0)
            else:
                raise FirmwareUpgraderException("E007: Invalid block {}".format(block))

            return status

        def wait_cdb(block=1, timeout=0.200):
            """
            Busy wait for a CDB command to complete for timeout seconds.
            Returns True if the CDB command completed before the timeout, False otherwise.

            Args:
                block: int: CDB block (1 or 2)
                timeout: int: Timeout period in seconds
            """
            if sys.version_info[:2] == (2, 7):
                # TODO: Need to make sure this doesn't get stuck if time moves backwards during the execution
                time_func = time.clock
            elif sys.version_info[0] == 3:
                time_func = time.monotonic
            else:
                raise Exception("Unsupported Python version: {}, requires 2.7 or 3.x".format(sys.version_info))

            start = time_func()

            status = cdb_status(block)

            # Wait for CDB to become free (0x80 == busy)
            while status & 0x80:
                self.logger.debug("Waiting for CDB status to return 1, current status: {:04X}h".format(status))
                if time_func() - start > timeout:
                    return 0x00

                time.sleep(0.002)
                status = cdb_status(block)

            return status

        self.logger.debug("CDB command: {:04X}h".format(cmd))
        self.logger.debug(lpl)

        # Struct format for the CDB command field block
        #   >   Big endian
        #   H   Command code (2 bytes)
        #   H   EPL length (2 bytes)
        #   B   LPL length (1 byte)
        #   B   CdbChkCode (1 byte)
        #   B   RLPLLen (1 byte)
        #   B   RLPLChkCode (1 byte)
        command_fields_format = ">HHBBBB"

        # Struct format for the data covered by the check code
        check_code_format = command_fields_format + "{}s".format(len(lpl))

        epl_len = 0x0
        lpl_len = len(lpl)
        cdb_check_code = 0x0
        rlpl_check_code = 0x0

        # TODO: Determine if rlpl_len should be included in the check code calculation for 0103h.

        # The spec is vague on this point.  The description of byte 133 of
        # table 9-19 says it should be zero.  However, the description of byte
        # 144 says it should be the length of the block of vendor data.

        # This implementation will NOT insert the length of the vendor data
        # into the check code calculation at byte 133.

        # Pack the command fields and LPL data to calc the check code
        # pylint:   disable=bad-continuation
        data = struct.pack(check_code_format,
                           cmd,
                           epl_len,
                           lpl_len,
                           cdb_check_code,
                           0x0,
                           rlpl_check_code,
                           lpl,
                           )
        # pylint:   enable=bad-continuation

        # Calc the check code
        cdb_check_code = cdb_chk_code(data)

        # Pack the final command fields wth the check code
        # pylint:   disable=bad-continuation
        command_fields = struct.pack(command_fields_format,
                                     cmd,
                                     epl_len,
                                     lpl_len,
                                     cdb_check_code,
                                     rlpl_len,
                                     rlpl_check_code,
                                     )
        # pylint:   enable=bad-continuation

        if lpl_len:
            # We're limited in the number of bytes that we can write in a
            # single I2C transaction by the MKRZero.  The command will take
            # effect when the command fields are written.  So we write all of
            # the LPL data first and then the command fields to trigger it.
            self.write_int(136, 0x9f, list(lpl))

        self.write_int(128, 0x9f, list(command_fields))

        # CDB 0101h commands performs a full erase of the target partition.
        # The erase hangs the AHB bus, preventing I2C communication. So we
        # need at most a 1.750s delay before continuing with I2C traffic.
        # CDB 0103h commands perform flash writes. We give them a tiny
        # amount of headroom to avoid any delays in acknowledging the
        # subsequent status check for the same AHB bus reason above.
        if (cmd == 0x0101):
            time.sleep(1.750)
        elif (cmd == 0x0103):
            time.sleep(0.001)
        # elif (cmd == 0x0107):
        elif (cmd == 0x0107) or (cmd == 0x0100):
            time.sleep(0.1)

        # For quick DFUs, skip checking for the CDB Status. In this case,
        # it's assumed the delays in the hardware are more than sufficient
        # for the system to recover.
        if not self.skip_status_check:
            # Block until the command completesand get the result of the command
            self.logger.debug("Checking CDB status for cmd: {:04X}h".format(cmd))
            status = wait_cdb()

            # Check the result of the command
            if status != 0x01:
                raise FirmwareUpgraderException("E007: CMD {:04x} failed: 0x{:02x}".format(cmd, status))

    def read_int(self, offset, page):
        """
        Reads from the I2C driver and returns an integer value

        Args:
            offset: int: Byte offset
            page: int: CMIS page
        """
        if page != 0 and offset >= 128:
            offset = offset - 128

        data = self.i2c_driver.read(page=page, offset=offset, count=1)

        try:
            output = list(data)[0]
        except TypeError:
            output = data

        return output

    def write_int(self, offset, page, data):
        """
        Converts integer values to a bytearray and write using
        the provided I2C driver

        Args:
            offset: int: Byte offset
            page: int: CMIS page
            data: int|array: Data byte as integer or list
        """
        if isinstance(data, list) == False:
            data = [data]

        if page != 0 and offset >= 128:
            offset = offset - 128

        din = bytearray(data)
        length = len(data)

        # Break up data into chunks
        out_buf = list(self._chunks(din, self.chunk_size))

        for chunk in out_buf:
            length = len(chunk)

            self.i2c_driver.write(page=page, offset=offset, data=chunk)

            # Update the offset
            offset = offset + self.chunk_size

    def dfu(self, filename, limit=None, verbose=False):
        """
        Open an image file and send it via CDB commands for DFU.

        Args:
            filename: string: Path fo binary file
            limit: int: Limit as offset from start of file to use for DFU
            verbose: bool: Display verbose info
        Returns:
            CRC of the image file
        """
        # Open a firmware image with a version 1 header
        image_file = HeaderV1(filename)
        image_file.load()

        # Get the data to send
        header_data = image_file.header()
        header_size = len(header_data)
        image_data, image_offset = image_file.data()

        # TODO: Update tools to create image files without state section for DFU

        # Remove the state section from the data to send
        image_data = image_data[0:image_offset]

        # Send the CDB command 0101h to start a firmware download
        lpl = self._format_0101(len(image_data) + header_size, header_data)
        self.cdb_cmd(0x0101, lpl=lpl)

        # Set the starting address we're writing to
        image_address = 0

        # For debugging allow the ability to not send the entire image
        if limit is not None:
            image_data = image_data[0:limit]

        # Send a series of 0103 commands with the image data

        # Create a list of all of the chunks
        segments = list(self._chunks(image_data, self.chunk_size))
        count = 1
        total = len(segments)
        for i in segments:
            # Show a progress bar in non-verbose mode.  If we're verbose, the
            # cmis_self.cdb_cmd() method will do a hex dump of what it's sending.
            if not verbose:
                self._progress(count, total, "DFU")
                count += 1

            # Format the LPL data for a 0103 command
            lpl = self._format_0103(image_address, i)

            # Send the data
            self.cdb_cmd(0x0103, lpl=lpl, rlpl_len=len(i), verbose=verbose)

            image_address += len(i)

        if limit is None:
            # Send the Firmware Download Complete
            self.cdb_cmd(0x0107)

        return image_file.get_crc()

    def _format_0101(self, image_size, vendor_data):
        """
        Return a byte array containing the image size and vendor data
        formatted for a 0101 command.
        """
        # Struct format for the LPL data of a 0101 command
        #   >   Big endian
        #   I   Image size (4 bytes)
        #   4s  Reserved (4 bytes)
        #   ?s  Vendor data (variable length)
        format_str = ">I4s{}s".format(len(vendor_data))

        return struct.pack(format_str, image_size, bytes(0), vendor_data)

    def _format_0103(self, address, lpl):
        """
        Return a byte array containing the address and lpl formatted for a
        0103 command.
        """
        # Struct format for the LPL data of a 0103 command
        #   >   Big endian
        #   I   Image size (4 bytes)
        #   ?s  LPL data (variable length)
        format_str = ">I{}s".format(len(lpl))

        return struct.pack(format_str, address, lpl)

    def _poll_retimer(self):
        """
        Polls the retimer, waiting for it to return to the Ready State.

        Return: 0 on failure, 1 on success
        """
        success = 0

        sys.stdout.write("Updating DSP firmware...\n")
        sys.stdout.flush()

        # Fails if retimer doesn't return to Ready in 1:20
        for i in range(0, 60):
            # Read the retimer status
            status = self.get_module_status()

            # Show progress bar
            self._progress(i, 60, "DFU on Retimer")

            if status == 3:
                success = 1

                # Force the progress bar to jump to 100%
                self._progress(100, 100, "DFU on Retimer")
                break

            time.sleep(1)

        self.logger.info("\n")

        return success

    def _progress(self, count, total, process):
        """
        Simple progress bar.
        """
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percent = round(100.0 * count / float(total), 1)
        progress_bar = '=' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write("{}: [{}] {}%\r".format(process, progress_bar, int(percent)))
        sys.stdout.flush()

        if count == total:
            sys.stdout.write("\n")
            sys.stdout.flush()

    def _find(self, pattern, path):
        """
        Find and return the first file starting from 'path' matching 'pattern'
        """
        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))

        if not result:
            return None

        return result[0]

    def _assert_expected_version(self, expected, actual):
        """
        Asserts that expected version is equal to actual version
        """
        return (expected[0] == actual[0]) and (expected[1] == actual[1]) \
            and (expected[2] == actual[2])

    def _chunks(self, data, n):
        """
        Breaks a list up into N size chunks.  The last item in the list
        may have less than N items.
        """
        for i in range(0, len(data), n):
            yield data[i:i + n]


###############
# Image Tools #
###############

"""
Classes used to operate on image info headers for firmware images.
"""


# The nature of these classes is to have only few public methods and to keep
# the internal members of the structures as instance attributes.

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes

def check_magic(actual, expected):
    """
    Verifies that a magic number matches its expected value.
    """
    if actual != expected:
        raise Exception(
            "Unsupported binary.  "
            "Expected magic number of 0x{:08x}, found 0x{:08x}".format(expected, actual)
        )


def pack_s(value):
    """
    Convert a bytearray to string for Python 2 or to a bytes object for Python
    3 so that it can be used as an argument to struct.pack() for a 's' format.
    """
    if sys.version_info[:2] == (2, 7):
        return str(value)
    elif sys.version_info[0] == 3:
        return bytes(value)
    else:
        raise Exception("Unsupported Python version: {}, requires 2.7 or 3.x".format(sys.version_info))


class Header(object):
    """
    Class that implements a image header.
    """
    # pylint:   disable=bad-whitespace
    ENDIAN = "<"
    MAGIC = "I"
    VERSION = "B"
    HEADER_SIZE = "B"
    # pylint:   enable=bad-whitespace

    # Define the format of the header that is common to all versions.
    FORMAT = "".join(
        [
            ENDIAN,
            MAGIC,
            VERSION,
            HEADER_SIZE,
        ]
    )

    # The IMAGE_HEADER_MAGIC values must match the IMAGE_HEADER_MAGIC defined
    # in common/image_info.h.
    IMAGE_HEADER_MAGIC = 0xbeefcafe

    # The TARGET_DEVICE values must match the target_device_t enumeration.
    # pylint:   disable=bad-whitespace
    TARGET_DEVICE_STM = 1
    TARGET_DEVICE_TAURUS = 2
    TARGET_DEVICE_TAURUS1 = 3
    # pylint:   enable=bad-whitespace

    # The FW_ID values must match the fw_identifier_t enumeration.
    # pylint:   disable=bad-whitespace
    FW_ID_APPLICATION_A = 1
    FW_ID_APPLICATION_B = 2
    FW_ID_CMIS_REG_SLOT = 3
    FW_ID_TAURUS_OSFP = 4
    FW_ID_TAURUS_QDD = 5
    FW_ID_TAURUS1 = 6
    # pylint:   enable=bad-whitespace

    # Dictionary to convert a target device value to a string.
    MAP_TARGET_DEVICE = {
        TARGET_DEVICE_STM: "stm32",
        TARGET_DEVICE_TAURUS: "taurus",
        TARGET_DEVICE_TAURUS1: "taurus1"
    }

    # Dictionary to convert a command line argument of the target device to a value.
    MAP_TARGET_DEVICE_ARG = {value: key for key, value in MAP_TARGET_DEVICE.items()}

    # Dictionary to convert a firmware ID to a string.
    MAP_FW_ID = {
        FW_ID_APPLICATION_A: "a",
        FW_ID_APPLICATION_B: "b",
        FW_ID_CMIS_REG_SLOT: "crs",
        FW_ID_TAURUS_OSFP: "taurus_osfp",
        FW_ID_TAURUS_QDD: "taurus_qdd",
        FW_ID_TAURUS1: "taurus1"
    }

    # Dictionary to convert a command line argument of the firmware ID to a value.
    MAP_FW_ID_ARG = {value: key for key, value in MAP_FW_ID.items()}

    def __init__(self, filename, verbose):
        self._filename = filename
        self._verbose = verbose


class HeaderV1(Header):
    """
    Class that implements a version 1 image header.
    """
    # pylint:   disable=bad-whitespace
    TARGET_DEVICE = "B"
    FW_IDENTIFIER = "B"
    MAJOR = "B"
    MINOR = "B"
    BUILD = "H"
    EXTRA = "32s"
    IMAGE_SIZE = "I"
    IMAGE_CRC = "I"
    GIT_SHA = "12s"
    HEADER_CRC = "I"
    PAD_LEN = 4
    PAD = "{}s".format(PAD_LEN)
    # pylint:   enable=bad-whitespace

    FORMAT = "".join(
        [
            Header.FORMAT,
            TARGET_DEVICE,
            FW_IDENTIFIER,
            MAJOR,
            MINOR,
            BUILD,
            EXTRA,
            IMAGE_SIZE,
            IMAGE_CRC,
            GIT_SHA,
            HEADER_CRC,
            PAD,
        ]
    )

    def __init__(self, filename, verbose=True):
        if sys.version_info[:2] == (2, 7):
            super(HeaderV1, self).__init__(filename, verbose)
        elif sys.version_info[0] == 3:
            super().__init__(filename, verbose)
        else:
            raise Exception("Unsupported Python version: {}, requires 2.7 or 3.x".format(sys.version_info))

        # Unpack a blank header to create the class variables
        (
            self._magic,
            self._version,
            self._size,
            self._target_device,
            self._fw_identifier,
            self._major_version,
            self._minor_version,
            self._build,
            self._extra,
            self._image_size,
            self._image_crc,
            self._git_sha,
            self._header_crc,
            self._pad,
        ) = struct.unpack(self.FORMAT, bytearray(struct.calcsize(self.FORMAT)))

        self._data = pack_s(bytearray(0))
        self._common_header = pack_s(bytearray(0))
        self._full_header = pack_s(bytearray(0))
        self._offset = 0

        self._magic = Header.IMAGE_HEADER_MAGIC
        self._size = struct.calcsize(self.FORMAT)
        self._version = 1

    def load(self, debug=False):
        """
        Load the header and image data into memory.
        """
        # Load the common header
        try:
            with open(self._filename, "rb") as image:
                self._common_header = image.read(struct.calcsize(Header.FORMAT))
        except:
            raise FirmwareUpgraderException("E001: File not found")

        # Extract the components
        (
            self._magic,
            self._version,
            self._size,
        ) = struct.unpack(Header.FORMAT, self._common_header)

        # Verify that it's an image header
        check_magic(self._magic, Header.IMAGE_HEADER_MAGIC)

        # verify that is the correct version
        if self._version != 1:
            raise FirmwareUpgraderException("E002: Can't read a version {} image header".format(self._version))

        # Load the full header and the image data
        with open(self._filename, "rb") as image:
            # Read the full header
            self._full_header = image.read(self._size)
            if debug:
                self.logger.info("Header size: 0x{0:08x} ({0})".format(len(self._full_header)))

            # Read the image data
            self._data = image.read()
            if debug:
                self.logger.info("Data size: 0x{0:08x} ({0})".format(len(self._data)))

        # Unpack the header
        (
            self._magic,
            self._version,
            self._size,
            self._target_device,
            self._fw_identifier,
            self._major_version,
            self._minor_version,
            self._build,
            self._extra,
            self._image_size,
            self._image_crc,
            self._git_sha,
            self._header_crc,
            self._pad,
        ) = struct.unpack(self.FORMAT, self._full_header)

        # Create an instance of the state section for this image.  This will
        # give the offset to the start of the state section if it exists.
        try:
            state = StateV1(self._filename)
        except FirmwareUpgraderException as e:
            # We don't really care if the state version is incorrect, we just
            # need to know where the state section starts for purposes of
            # calculating the CRC.
            pass

        # We need to adjust the offset by the size of the header because the
        # CRC calculation is performed over the image data only.
        self._offset = state.offset() - len(self._full_header)
        if debug:
            self.logger.info("State offset: 0x{:08x}".format(self._offset))

    def set_version(self, major_version=None, minor_version=None, build=None):
        """
        Set the version and recalculate the CRC.

        major_version   An 8 bit integer that is the major version.

        minor_version   An 8 bit integer that is the minor version.

        build           A 16 bit integer that is the build number.

        """
        if major_version:
            self._major_version = int(major_version)

        if minor_version:
            self._minor_version = int(minor_version)

        if build:
            self._build = int(build)

        self._update_crc()

    def get_version(self):
        """
        Returns the major, minor, and build versions of the current image
        """
        return self._major_version, self._minor_version, self._build

    def get_crc(self):
        """
        Returns the CRC for the loaded firmware image
        """
        self._update_crc()

        return self._image_crc

    def get_target(self):
        """
        Returns the target device as a string (stm32, taurus, taurus1)
        """
        return self.MAP_TARGET_DEVICE[self._target_device]

    def get_id(self):
        """
        Returns the firmware identifier as a string (a, b, cmis, taurus_osfp,
        taurus_qdd, taurus1)
        """
        return self.MAP_FW_ID[self._fw_identifier]

    def create(self, image_id, image_target):
        """
        Add a header to an image where it doesn't already exist.

        image_id        A string describing the ID to set.  It must be a value
                        of the MAP_FW_ID dictionary.

        image_target    A string describing the target device.  It must be
                        value of the MAP_TARGET_DEVICE dictionary.
        """
        # Load the image data
        with open(self._filename, "rb") as image:
            # Load the image data
            self._data = image.read()

        # Set the file offset to the file size.  When we're creating a header,
        # we're assuming we're adding a header to a non-STM32 binary.  So it
        # won't have a state section.
        self._offset = len(self._data)

        try:
            self._fw_identifier = self.MAP_FW_ID_ARG[image_id]
        except KeyError:
            raise FirmwareUpgraderException("E003: Unexpected id: '{}'".format(image_id))

        try:
            self._target_device = self.MAP_TARGET_DEVICE_ARG[image_target]
        except KeyError:
            raise FirmwareUpgraderException("E005: Unexpected target: '{}'".format(image_target))

        self._update_crc()

        # Write the data back out as the header followed by the orginal data.
        # We don't use write as that expects to update and existing header and
        # to not create a new one.
        with open(self._filename, "wb") as image:
            image.write(self._full_header)
            image.write(self._data)

    def raw(self):
        """
        Attempt to read a header from a file without verifying the data.

        This can be useful for inspecting a possible misformed header.
        """
        with open(self._filename, "rb") as image:
            self._full_header = image.read(struct.calcsize(self.FORMAT))

        # Unpack the header
        (
            self._magic,
            self._version,
            self._size,
            self._target_device,
            self._fw_identifier,
            self._major_version,
            self._minor_version,
            self._build,
            self._extra,
            self._image_size,
            self._image_crc,
            self._git_sha,
            self._header_crc,
            self._pad,
        ) = struct.unpack(self.FORMAT, self._full_header)

    def __str__(self):
        """
        Return a string containing the header infomation
        """
        # Create string names of the device and firmware ID's
        try:
            target_name = self.MAP_TARGET_DEVICE[self._target_device]
        except KeyError:
            target_name = "unknown"

        try:
            fw_name = self.MAP_FW_ID[self._fw_identifier]
        except KeyError:
            fw_name = "unknown"

        descript = (
                "Image Header ({} bytes):\n".format(struct.calcsize(self.FORMAT)) +
                "  magic:          0x{:08x}\n".format(self._magic) +
                "  header version: 0x{:02x}\n".format(self._version) +
                "  header size:    0x{0:02x} ({0}) padded\n".format(self._size) +
                "  target:         0x{:02x} ({})\n".format(self._target_device, target_name) +
                "  firmware ID:    0x{:02x} ({})\n".format(self._fw_identifier, fw_name) +
                "  major version:  0x{:02x}\n".format(self._major_version) +
                "  minor version:  0x{:02x}\n".format(self._minor_version) +
                "  build:          0x{:04x}\n".format(self._build) +
                "  extra:          {}\n".format(self._extra) +
                "  image size:     0x{0:08x} ({0})\n".format(self._image_size) +
                "  image CRC:      0x{:08x}\n".format(self._image_crc) +
                "  git SHA:        {}\n".format(self._git_sha) +
                "  header CRC:     0x{:08x}\n".format(self._header_crc) +
                "  pad:            {}".format(self._pad)
        )

        return descript.strip()

    def _update_crc(self, debug=False):
        """
        Update the header CRC with the current values.
        """
        image_data = self._data[0:self._offset]
        if debug:
            self.logger.info("Image size: 0x{0:08x} ({0})".format(len(image_data)))

        self._image_size = len(image_data)
        self._image_crc = binascii.crc32(image_data) & 0xffffffff

        # Create a bytearray of the header with all of the values set so that
        # we can calculate the header CRC

        # Create the header to calculate the CRC of
        # pylint:   disable=bad-continuation
        header = struct.pack(self.FORMAT,
                             self._magic,
                             self._version,
                             self._size,
                             self._target_device,
                             self._fw_identifier,
                             self._major_version,
                             self._minor_version,
                             self._build,
                             self._extra,
                             self._image_size,
                             self._image_crc,
                             self._git_sha,
                             0x0,
                             pack_s(bytearray(0)),
                             )
        # pylint:   enable=bad-continuation

        self._header_crc = binascii.crc32(header) & 0xffffffff

        # Create the final header
        # pylint:   disable=bad-continuation
        self._full_header = struct.pack(self.FORMAT,
                                        self._magic,
                                        self._version,
                                        self._size,
                                        self._target_device,
                                        self._fw_identifier,
                                        self._major_version,
                                        self._minor_version,
                                        self._build,
                                        self._extra,
                                        self._image_size,
                                        self._image_crc,
                                        self._git_sha,
                                        self._header_crc,
                                        pack_s(bytearray(0)),
                                        )
        # pylint:   enable=bad-continuation

        # Unpack the final header to update our internal copy
        (
            self._magic,
            self._version,
            self._size,
            self._target_device,
            self._fw_identifier,
            self._major_version,
            self._minor_version,
            self._build,
            self._extra,
            self._image_size,
            self._image_crc,
            self._git_sha,
            self._header_crc,
            self._pad,
        ) = struct.unpack(self.FORMAT, self._full_header)

    def update(self, image_id=None, image_target=None):
        """
        Update the image header information to write the CRC's and image size.

        image_id        A string describing the ID to set.  It must be a value
                        of the MAP_FW_ID dictionary.

        image_target    A string describing the target device.  It must be
                        value of the MAP_TARGET_DEVICE dictionary.
        """
        self._image_size = len(self._data[0:self._offset])
        self._image_crc = binascii.crc32(self._data[0:self._offset]) & 0xffffffff

        # Create a bytearray of the header with all of the values set so that
        # we can calculate the header CRC

        if image_id:
            try:
                self._fw_identifier = self.MAP_FW_ID_ARG[image_id]
            except KeyError:
                raise FirmwareUpgraderException("E003: Unexpected id: '{}'".format(image_id))

        if image_target:
            try:
                self._target_device = self.MAP_TARGET_DEVICE_ARG[image_target]
            except KeyError:
                raise FirmwareUpgraderException("E005: Unexpected target: '{}'".format(image_target))

        self._update_crc()

    def write(self, filename=None):
        """
        Save the header out to a file.  If none is given, update the original file.
        """
        if not filename:
            # Save the state back to the file
            if self._verbose:
                self.logger.info("Updating {}".format(self._filename))
                self.logger.info("{}".format(self))
            with open(self._filename, "r+b") as image:
                image.write(self._full_header)
        else:
            with open(filename, "wb") as image:
                image.write(self._full_header)

    def header(self):
        """
        Return a byte array of the full header.
        """
        return self._full_header

    def data(self):
        """
        Return a tuple consisting of a byte array of the image data and the
        offset to where the CRC stops.  That is, the CRC only covers
        data[0:offset].
        """
        return self._data, self._offset


class State(object):
    """
    Class that implements a image state structure in flash.
    """
    # Define the format string used to unpack a image_state_t struct

    # pylint:   disable=bad-whitespace
    ENDIAN = "<"
    MAGIC = "I"
    VERSION = "B"
    SIZE = "B"
    # pylint:   enable=bad-whitespace

    # Define the format of the state that is common to all versions.
    FORMAT = "".join(
        [
            ENDIAN,
            MAGIC,
            VERSION,
            SIZE,
        ]
    )

    # The number of bytes in a state section
    SECTION_SIZE = 2048

    # The IMAGE_STATE_MAGIC values must match the IMAGE_STATE_MAGIC defined in
    # common/image_info.h.
    IMAGE_STATE_MAGIC = 0x0bedface

    # The offset from the start of an image file to the location that the state
    # header starts.  This is only applicable to STM32 images as they are the
    # only images that have a state section.
    #
    # This value is calculated by looking at the common/Linker/memory_map.ld
    # linker script and subtracting the origin of the image_X_state from the
    # origin of the image_X.  This calculation should be the same for either
    # the A or B image.
    #
    # offset = image_a_state - image_a
    OFFSET = 0x0803F800 - 0x0801C800

    # The FW_STATE values must match the fw_state_t enumeration.
    # pylint:   disable=bad-whitespace
    FW_STATE_IMAGE_DEFAULT = 0
    FW_STATE_IMAGE_WRITING = 1
    FW_STATE_IMAGE_VERIFIED = 2
    FW_STATE_IMAGE_ABORTED = 3
    FW_STATE_IMAGE_DEPRECATED = 4
    FW_STATE_IMAGE_COMMITTED = 5
    FW_STATE_IMAGE_ERASED = 0xff
    # pylint:   enable=bad-whitespace

    # Dictionary to convert a state value to a string.
    MAP_FW_STATE = {
        FW_STATE_IMAGE_DEFAULT: "default",
        FW_STATE_IMAGE_WRITING: "writing",
        FW_STATE_IMAGE_VERIFIED: "verified",
        FW_STATE_IMAGE_ABORTED: "aborted",
        FW_STATE_IMAGE_DEPRECATED: "deprecated",
        FW_STATE_IMAGE_COMMITTED: "committed",
        FW_STATE_IMAGE_ERASED: "erased",
    }

    # Dictionary to convert a command line argument of the state to a value.
    MAP_FW_STATE_ARG = {value: key for key, value in MAP_FW_STATE.items()}

    def __init__(self, filename, verbose):
        self._filename = filename
        self._verbose = verbose


class StateV1(State):
    """
    Class that implments a version 1 image state structure.
    """
    # pylint:   disable=bad-whitespace
    STATE = "B"
    PAD_LEN = 7
    PAD = "{}s".format(PAD_LEN)
    # pylint:   enable=bad-whitespace

    # Define the format of a version 1 state array entry
    FORMAT = "".join(
        [
            STATE,
            PAD,
        ]
    )

    def __init__(self, filename, verbose=True):
        if sys.version_info[:2] == (2, 7):
            super(StateV1, self).__init__(filename, verbose)
        elif sys.version_info[0] == 3:
            super().__init__(filename, verbose)
        else:
            raise Exception("Unsupported Python version: {}, requires 2.7 or 3.x".format(sys.version_info))

        # Unpack a blank header to create the class variables
        (
            self._magic,
            self._version,
            self._size,
        ) = struct.unpack(State.FORMAT, bytearray(struct.calcsize(State.FORMAT)))

        self._state = pack_s(bytearray(0))
        self._offset = State.OFFSET

    def load(self):
        """
        Load the state section into memory if possible.
        """
        with open(self._filename, "rb") as image:
            data = image.read()

        try:
            # Save the state section
            self._state = data[self._offset:self._offset + State.SECTION_SIZE]
        except IndexError:
            # Data read isn't large enough to have a state section, so set the
            # offset to the data size
            self._state = None
            self._offset = len(data)
            return

        # Extract the common header
        common_header = self._state[0:struct.calcsize(State.FORMAT)]

        # Extract the common header components
        (
            self._magic,
            self._version,
            self._size,
        ) = struct.unpack(State.FORMAT, common_header)

        # Verify that it's a state section
        check_magic(self._magic, State.IMAGE_STATE_MAGIC)

        if self._version != 1:
            raise FirmwareUpgraderException("E002: Can't read a version {} state header".format(self._version))

    def __str__(self):
        """
        Return a string containing the state infomation
        """
        if not self._state:
            return "No Image State"

        # Search through the remaining state data and print out array entries
        # until we find a state_entry of 0xff.

        # The state structure is 8 byte aligned, so skip the first 8 bytes, the
        # common header, and convert the remaining bytes to a list of 8 byte
        # chunks
        entries = [self._state[i:i + 8] for i in range(8, len(self._state), 8)]

        description = (
                "Image State ({} bytes):\n".format(State.SECTION_SIZE) +
                "  magic:    0x{:08x}\n".format(self._magic) +
                "  version:  0x{:02x}\n".format(self._version) +
                "  size:     0x{0:02x} ({0})\n".format(self._size)
        )

        index = 0
        count = 0
        states = []
        for i in entries:
            # Unpack the version 1 array entry
            (
                state_entry,
                _,
            ) = struct.unpack(self.FORMAT, i)

            if state_entry != 0xff:
                count += 1
                states.append("    [{}]:    0x{:02x}\n".format(index, state_entry))

            index += 1

        description += "  states:   {} of {} used\n".format(count, len(entries))
        for i in states:
            description += i

        return description.strip()

    def update(self, image_state):
        """
        Update the image state information to set an initial state.
        """
        # Pack the header back into a byte array with the expected padding
        padded_format = State.FORMAT
        padded_value = ''
        padding = self._size - struct.calcsize(State.FORMAT)
        if padding:
            padded_format += "{}s".format(padding)
            padded_value = pack_s(bytearray(b'\x00') * padding)

        # Add an array entry
        padded_format += self.FORMAT

        # Convert the string to a value
        try:
            state = self.MAP_FW_STATE_ARG[image_state]
        except KeyError:
            raise FirmwareUpgraderException("E006: Unexpected state: '{image_state}'".format(image_state))

        # Create a header with a single entry
        # pylint:   disable=bad-continuation
        self._state = struct.pack(padded_format,
                                  self._magic,
                                  self._version,
                                  self._size,
                                  padded_value,
                                  state,
                                  pack_s(bytearray(b'\x00') * self.PAD_LEN),
                                  )
        # pylint:   enable=bad-continuation

        # Pad out to STATE_SECTION_SIZE with 0xff
        self._state += bytearray(b'\xff') * (State.SECTION_SIZE - struct.calcsize(padded_format))

    def write(self, filename=None):
        """
        Save the header out to a file.  If none is given, update the original file.
        """
        if not filename:
            # Save the state back to the file
            if self._verbose:
                self.logger.info("Updating {}".format(self._filename))
                self.logger.info("{}".format(self))
            with open(self._filename, "r+b") as image:
                image.seek(self._offset)
                image.write(self._state)
        else:
            with open(filename, "wb") as image:
                image.write(self._state)

    def offset(self):
        """
        Returns the offset to the start of the state section from the start of
        the file.  If there is no state section, returns the size of the file.
        """
        return self._offset


# Define the bytearry that the state magic number will be encoded as.  This is
# used to search for the offset to the structure in the file.
STATE_KEY = struct.pack(
    "".join(
        [
            State.ENDIAN,
            State.MAGIC,
        ]
    ),
    State.IMAGE_STATE_MAGIC
)
