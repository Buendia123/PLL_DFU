# Copyright 2021 Astera Labs, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at:
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
import os
import sys

# Relative paths for SDK files
REL_CONTROLLER_PATH = 'controller/'
REL_BOARD_PATH = 'board/'
REL_TEST_PATH = 'test/'
REL_VALIDATION_PATH = 'validation/'
REL_MFG_PATH = 'mfg_test/'

REL_DEVICE_PATH = 'device/'
REL_BASE_PATH = REL_DEVICE_PATH + 'base/'
REL_TOOLS_PATH = REL_DEVICE_PATH + 'tools/'
REL_CMIS_PATH = REL_DEVICE_PATH + 'cmis/'
REL_MTB_PATH = REL_DEVICE_PATH + 'mtb/'
REL_CMIS_TOOLS_PATH = REL_CMIS_PATH + 'tools/'
REL_MTB_TEST_PATH = REL_MFG_PATH + 'em200qdx/'

REL_TAURUS1_PATH = REL_DEVICE_PATH + 'taurus1/'
REL_TAURUS1_PMA_PATH = REL_TAURUS1_PATH + 'pma/'
REL_TAURUS1_XML_PATH = REL_TAURUS1_PATH + 'xml/'
REL_TAURUS1_CSR_PATH = REL_TAURUS1_XML_PATH + 'csr/'
REL_TAURUS1_CSR_PUBLIC_PATH = REL_TAURUS1_XML_PATH + 'csr_public/'
REL_TAURUS1_FIRMWARE_PATH = 'firmware/EM200QDX/'

REL_TAURUS_PATH = REL_DEVICE_PATH + 'taurus/'
REL_TAURUS_PMD_PATH = REL_TAURUS_PATH + 'pmd/'
REL_TAURUS_XML_PATH = REL_TAURUS_PATH + 'xml/'
REL_TAURUS_CSR_PATH = REL_TAURUS_XML_PATH + 'csr/'
REL_TAURUS_CMIS_PATH = REL_TAURUS_XML_PATH + 'cmis/'
REL_TAURUS_FIRMWARE_PATH = 'firmware/taurus/'
REL_EM200QX_FIRMWARE_PATH = 'firmware/EM200QX/'
REL_EM400QDX_FIRMWARE_PATH = 'firmware/EM400QDX/'

# Relative paths for lab-tools-python files
REL_LAB_TOOLS_PATH = '../lab-tools-python/'
REL_LAB_CONTROLLER_PATH = REL_LAB_TOOLS_PATH + 'controller/'
REL_COMPONENT_PATH = REL_LAB_TOOLS_PATH + 'component/'
REL_DRIVER_PATH = REL_LAB_TOOLS_PATH + 'driver/'
REL_TOOL_PATH = REL_LAB_TOOLS_PATH + 'tool/'

# Relative paths for taurus_sw files
REL_MEM_MAP_PATH = "../taurus_sw/module/common"

cur_file_loc = os.path.abspath(os.path.dirname(__file__))


def set_path_common():
    sys.path.append(os.path.join(cur_file_loc, REL_DEVICE_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_BASE_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_TOOLS_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_MFG_PATH))

    sys.path.append(os.path.join(cur_file_loc, REL_CONTROLLER_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_BOARD_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_TEST_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_VALIDATION_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_CMIS_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_MTB_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_CMIS_TOOLS_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_MTB_TEST_PATH))

    sys.path.append(os.path.join(cur_file_loc, REL_LAB_TOOLS_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_LAB_CONTROLLER_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_COMPONENT_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_DRIVER_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_TOOL_PATH))


def set_path_taurus1():
    sys.path.append(os.path.join(cur_file_loc, REL_TAURUS1_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_TAURUS1_PMA_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_TAURUS1_XML_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_TAURUS1_CSR_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_TAURUS1_CSR_PUBLIC_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_TAURUS1_FIRMWARE_PATH))


# FIXME: Need to handle retimer FW dictionary being in different hw target folders
def set_path_taurus():
    sys.path.append(os.path.join(cur_file_loc, REL_TAURUS_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_TAURUS_PMD_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_TAURUS_XML_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_TAURUS_CSR_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_TAURUS_CMIS_PATH))
    sys.path.append(os.path.join(cur_file_loc, REL_EM200QX_FIRMWARE_PATH))


def set_path_firmware():
    sys.path.append(os.path.join(cur_file_loc, REL_MEM_MAP_PATH))
