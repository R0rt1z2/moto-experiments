#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 R0rt1z2 <https://github.com/R0rt1z2>

from enum import Enum


class Command(Enum):
    """
    Commands used by the Preloader / BootROM protocol. Each command
    corresponds to a specific operation that can be performed on the
    device. Some devices may not support all commands.
    """

    GET_HW_SW_VER = 0xFC
    GET_HW_CODE = 0xFD
    GET_PL_VER = 0xFE
    GET_BR_VER = 0xFF

    LEGACY_WRITE = 0xA1
    LEGACY_READ = 0xA2

    I2C_INIT = 0xB0
    I2C_DEINIT = 0xB1
    I2C_WRITE8 = 0xB2
    I2C_READ8 = 0xB3
    I2C_SET_SPEED = 0xB4

    PWR_INIT = 0xC4
    PWR_DEINIT = 0xC5
    PWR_READ16 = 0xC6
    PWR_WRITE16 = 0xC7

    READ16 = 0xD0
    READ32 = 0xD1
    WRITE16 = 0xD2
    WRITE16_NO_ECHO = 0xD3
    WRITE32 = 0xD4
    JUMP_DA = 0xD5
    JUMP_BL = 0xD6
    SEND_DA = 0xD7
    GET_TARGET_CONFIG = 0xD8
    UART1_LOG_EN = 0xDB

    SEND_CERT = 0xE0
    GET_ME_ID = 0xE1
    SEND_AUTH = 0xE2
    SLA_CHALLENGE = 0xE3
    GET_SOC_ID = 0xE7

    ZEROIZATION = 0xF0
    GET_PL_CAP = 0xF1
