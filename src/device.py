#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 R0rt1z2 <https://github.com/R0rt1z2>
import logging
import time
from typing import Tuple, Union

import serial
from src.commands import Command
from src.utils import find_port, from_bytes, to_bytes


class Device:
    def __init__(self, port: str = None, baud: int = 115200, timeout: int = 5):
        self.dev: Union[serial.Serial, None] = None
        self.port = port
        self.baud = baud
        self.timeout = timeout

        if port:
            self.dev = serial.Serial(port, baud, timeout=timeout)

    @staticmethod
    def check(test: bytes, expected: bytes) -> bool:
        """
        Check if a test is successful.

        :param test: The test data.
        :param expected: The expected data.
        :return: True if the test is successful, otherwise False.
        """
        if test != expected:
            raise RuntimeError(f'Expected {expected}, got {test}')
        return True

    def find_device(
        self, vendor_id: int = 0x0E8D, product_id: int = 0x2000
    ) -> None:
        """
        Find the device by vendor ID and product ID.

        :param vendor_id: The vendor ID of the device.
        :param product_id: The product ID of the device.
        """
        if self.dev:
            logging.info('Device already found!')
            return

        self.port = find_port(vendor_id, product_id)
        logging.info('Found device = %s', self.port)

        if not self.port:
            raise RuntimeError('Device not found')

        self.dev = serial.Serial(self.port, self.baud, timeout=self.timeout)

    def echo(self, words, size=1) -> bool:
        """
        Send data to the device and check if the echo
        matches the sent data.

        :param words: The data to send.
        :param size: The number of bytes to read.
        :return: The data read.
        """
        self.dev.write(words)
        self.dev.read(size)
        # return self.check(self.dev.read(size), words)

    def wr(self, data: bytes, size: int = 1) -> bytes:
        """
        Write data to the device and read a response.

        :param data: The data to write.
        :param size: The number of bytes to read.
        """
        self.dev.write(data)
        return self.dev.read(size)

    def handshake(self) -> None:
        """
        Handshake with the device.
        """
        while True:
            self.dev.write(b'\xa0')
            response = self.dev.read(1)
            if response == b'\x5f':
                break
            self.dev.reset_input_buffer()

        self.check(self.wr(b'\x0a'), b'\xf5')
        self.check(self.wr(b'\x50'), b'\xaf')
        self.check(self.wr(b'\x05'), b'\xfa')

        logging.info('Handshake completed!')

    def get_hw_sw_ver(self) -> Tuple[int, int, int]:
        """
        Get the hardware and software version of the device.

        :return: The hardware and software version.
        """
        self.echo(to_bytes(Command.GET_HW_SW_VER.value, 1))

        hw_sub_code = self.dev.read(2)
        hw_ver = self.dev.read(2)
        sw_ver = self.dev.read(2)
        status = self.dev.read(2)

        if from_bytes(status, 2) != 0:
            raise RuntimeError('status is 0x%04X' % from_bytes(status, 2))

        return (
            from_bytes(hw_sub_code, 2),
            from_bytes(hw_ver, 2),
            from_bytes(sw_ver, 2),
        )

    def get_hw_code(self) -> int:
        """
        Get the hardware code of the device.

        :return: The hardware code.
        """
        self.echo(to_bytes(Command.GET_HW_CODE.value, 1))

        hw_code = self.dev.read(2)
        status = self.dev.read(2)

        if from_bytes(status, 2) != 0:
            raise RuntimeError('status is 0x%04X' % from_bytes(status, 2))

        return from_bytes(hw_code, 2)

    def get_me_id(self):
        """
        Get the ME ID of the device.

        :return: The ME ID.
        """
        self.echo(to_bytes(Command.GET_ME_ID.value, 1))

        length = from_bytes(self.dev.read(4), 4)
        if length == 0:
            raise RuntimeError('ME ID length is 0')
        me_id = self.dev.read(length)

        status = self.dev.read(2)
        if from_bytes(status, 2) != 0:
            raise RuntimeError('status is 0x%04X' % from_bytes(status, 2))

        return me_id

    def get_soc_id(self):
        """
        Get the SOC ID of the device.

        :return: The SOC ID.
        """
        self.echo(to_bytes(Command.GET_SOC_ID.value, 1))

        length = from_bytes(self.dev.read(4), 4)
        if length == 0:
            raise RuntimeError('SOC ID length is 0')
        soc_id = self.dev.read(length)

        status = self.dev.read(2)
        if from_bytes(status, 2) != 0:
            raise RuntimeError('status is 0x%04X' % from_bytes(status, 2))

        return soc_id

    def power_init(self, reg, val) -> None:
        """
        Initialize the power register.

        :param reg: The power register.
        :param val: The value to write.
        """
        logging.info(f'Init PMIC: 0x{reg:04X} (0x{val:04X})')
        self.echo(to_bytes(Command.PWR_INIT.value, 1))

        self.echo(to_bytes(reg, 4))
        self.echo(to_bytes(val, 4))

        status = self.dev.read(2)
        if from_bytes(status, 2) != 0:
            raise RuntimeError('status is 0x%04X' % from_bytes(status, 2))

    def power_deinit(self) -> None:
        """
        Deinitialize PMIC.
        """
        logging.info('Deinit PMIC')
        self.echo(to_bytes(Command.PWR_DEINIT.value, 1))

        status = self.dev.read(2)
        if from_bytes(status, 2) != 0:
            raise RuntimeError('status is 0x%04X' % from_bytes(status, 2))

    def get_preloader_version(self) -> int:
        self.dev.write(to_bytes(Command.GET_PL_VER.value, 1))

        pl_ver = self.dev.read(2)
        if pl_ver == 0xFE:
            logging.warning('Cannot get the Preloader version')

        return from_bytes(pl_ver, 1)

    def send_da(self, address, da_len, sig_len, da) -> int:
        """
        Uploads the Download Agent to the device.

        :param address: The address to upload the Download Agent to.
        :param da_len: The length of the Download Agent.
        :param sig_len: The length of the signature.
        :param da: The Download Agent to upload.

        :return: The checksum of the Download Agent.
        """
        logging.info(
            'Send DA to 0x%08X '
            '(%d bytes, %d bytes signature)' % (address, da_len, sig_len)
        )
        self.echo(to_bytes(Command.SEND_DA.value, 1))

        self.echo(to_bytes(address, 4), 4)
        self.echo(to_bytes(da_len, 4), 4)
        self.echo(to_bytes(sig_len, 4), 4)

        status = self.dev.read(2)

        if from_bytes(status, 2) != 0:
            raise RuntimeError('status is 0x%04X' % from_bytes(status, 2))

        self.dev.write(da)

        checksum = from_bytes(self.dev.read(2), 2)
        status = from_bytes(self.dev.read(2), 2)

        if status != 0:
            raise RuntimeError('status is 0x%04X' % status)

        return checksum

    def jump_da(self, address: int):
        """
        Jump to the Download Agent.

        :param address: The address of the Download Agent.
        """
        logging.info('Jump to DA at 0x%08X', address)
        self.echo(to_bytes(Command.JUMP_DA.value, 1))

        self.echo(to_bytes(address, 4))

        status = self.dev.read(2)

    def identify(self) -> None:
        """
        Identify the device.
        """
        hw_code = self.get_hw_code()
        hw_sub_code, hw_ver, sw_ver = self.get_hw_sw_ver()
        me_id = self.get_me_id()
        soc_id = self.get_soc_id()
        logging.info(f'HW Code: 0x{hw_code:04X}')
        logging.info(f'HW Sub-Code: 0x{hw_sub_code:04X}')
        logging.info(f'HW Version: 0x{hw_ver:04X}')
        logging.info(f'SW Version: 0x{sw_ver:04X}')
        logging.info(f'ME ID: {me_id.hex().upper()}')
        logging.info(f'SOC ID: {soc_id.hex().upper()}')
