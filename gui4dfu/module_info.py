#!/usr/bin/python
# -*- coding: ascii -*-
"""
Module info extract and decode, to be included as an from-<x>-import-star
"""


######################################################################
#  Decode page 00 and page c0 contents.  These should have proper values
#  by the time we're ready to run this.
######################################################################
def decode_page00_pagec0(page00=[], pagec0=[], logger=None):
    logger.info('Module info:')
    #  some stupid conversions because I can't just %s/%c/%x (I hate python)
    #  One of these days, I'll actually learn python.
    tmp_array = []
    for ii in range(16):
        offset = ii + 1  # 129-145, 16 bytes
        tmp_array.append(page00[offset])
    vendor_name = "".join([f'{ii:c}' for ii in tmp_array])

    tmp_array = []
    for ii in range(16):
        offset = ii + 20  # 148-164, 16 bytes
        tmp_array.append(page00[offset])
    vendor_pn = "".join([f'{ii:c}' for ii in tmp_array])

    #  164-165
    vendor_rev = chr(page00[36]) + chr(page00[37])

    tmp_array = []
    for ii in range(16):
        offset = ii + 38  # 166-182, 16 bytes
        tmp_array.append(page00[offset])
    vendor_sn = "".join([f'{ii:c}' for ii in tmp_array])

    tmp_array = []
    for ii in range(8):
        offset = ii + 54  # 166-182, 16 bytes
        tmp_array.append(page00[offset])
    date_code = "".join([f'{ii:c}' for ii in tmp_array])

    tmp_array = []
    for ii in range(16):
        offset = ii + 18  # 146-162, 16 bytes
        tmp_array.append(pagec0[offset])
    card_pn = "".join([f'{ii:c}' for ii in tmp_array])

    tmp_array = []
    for ii in range(16):
        offset = ii + 36  # 164-180, 16 bytes
        tmp_array.append(pagec0[offset])
    card_sn = "".join([f'{ii:c}' for ii in tmp_array])

    fct_version = f'{pagec0[0]}.{pagec0[1]}'
    test_date = f'{pagec0[52]:c}{pagec0[53]:c}-{pagec0[54]:c}{pagec0[55]:c}-{pagec0[56]:c}{pagec0[57]:c}'
    boot_loader = f'{pagec0[59]}.{pagec0[60]}.{pagec0[61]}'
    mcu_fw = f'{pagec0[62]}.{pagec0[63]}.{pagec0[64]}'
    cmis_fw = f'{pagec0[65]}.{pagec0[66]}.{pagec0[67]}'
    dsp_fw = f'{pagec0[68]}.{pagec0[69]}.{pagec0[70]}'

    tmp_array = []
    for ii in range(12):
        offset = ii + 77  # 205-217, 12 bytes
        tmp_array.append(pagec0[offset])
    csn = "".join([f'{ii:02x}' for ii in tmp_array])
    fab_number = f'{pagec0[217 - 128]:c}{pagec0[218 - 128]:c}'

    tmp_array = []
    for ii in range(6):
        offset = ii + 91  # 219-224, 6 bytes
        tmp_array.append(pagec0[offset])
    wafer_lot = "".join([f'{ii:c}' for ii in tmp_array])

    tmp_array = []
    for ii in range(6):
        offset = ii + 99  # 227-232, 6 bytes
        tmp_array.append(pagec0[offset])
    assembly_lot = "".join([f'{ii:c}' for ii in tmp_array])

    xy = f'{pagec0[233 - 128]:c}{pagec0[234 - 128]:c},{pagec0[235 - 128]:c}{pagec0[236 - 128]:c}'

    logger.info(f'VendorName: {vendor_name}')
    logger.info(f'VendorPN:   {vendor_pn}')
    logger.info(f'VendorRev:  {vendor_rev}')
    logger.info(f'VendorSN:   {vendor_sn}')
    logger.info(f'DateCode:   {date_code}')
    logger.info(f'CardPN:     {card_pn}')
    logger.info(f'CardSN:     {card_sn}')
    logger.info(f'FCT:        {fct_version}')
    logger.info(f'TestDate:   {test_date}')
    logger.info(f'BootLoader: {boot_loader}')
    logger.info(f'MCU FW:     {mcu_fw}')
    logger.info(f'CMIS FW:    {cmis_fw}')
    logger.info(f'DSP FW:     {dsp_fw}')
    logger.info(f'ChipSN:     {csn}')
    logger.info(f'FabNumber:  {fab_number}')
    logger.info(f'WaferLot:   {wafer_lot}')
    logger.info(f'AssyLot:    {assembly_lot}')
    logger.info(f'WaferXY:    {xy}')
    return 0


def module_sn_info(driver=None, logger=None):
    sn_list = driver.read(offset=0xa6, page=0x00, count=16)
    char_list = [chr(item) for item in sn_list]
    result = ''.join(char_list)
    logger.info('sn:' + result)
    return result


def module_info(driver=None, logger=None):
    if (None == driver):
        logger.info('ERROR: driver == None')
        return 1

    #  Read out useful info from page00 and pagec0.  Linux SMBus has a 
    #  32-byte limit, hence the ugliness
    page00_0 = driver.read(offset=0x80, page=0x00, count=32)  # 128-159
    page00_1 = driver.read(offset=0xa0, page=0x00, count=32)  # 160-191
    page00_2 = driver.read(offset=0xc0, page=0x00, count=32)  # 192-223
    page00_3 = driver.read(offset=0xe0, page=0x00, count=32)  # 224-255

    pagec0_0 = driver.read(offset=0x80, page=0xc0, count=32)
    pagec0_1 = driver.read(offset=0xa0, page=0xc0, count=32)
    pagec0_2 = driver.read(offset=0xc0, page=0xc0, count=32)
    pagec0_3 = driver.read(offset=0xe0, page=0xc0, count=32)

    #  And merge it into a single array -- I mean list.
    page00 = page00_0 + page00_1 + page00_2 + page00_3
    pagec0 = pagec0_0 + pagec0_1 + pagec0_2 + pagec0_3

    #  and decode the relevant contents
    decode_page00_pagec0(page00, pagec0, logger)
