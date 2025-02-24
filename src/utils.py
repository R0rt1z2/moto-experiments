#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 R0rt1z2 <https://github.com/R0rt1z2>

import struct
import time
from typing import Union

import serial
import serial.tools.list_ports


def find_port(vendor_id, product_id, timeout=None) -> Union[str, None]:
    """
    Find a serial port by vendor ID and product ID.

    :param vendor_id: The vendor ID of the device.
    :param product_id: The product ID of the device.
    :param timeout: The time in seconds to keep searching. If None, search indefinitely.
    :return: The device name (e.g., '/dev/ttyUSB0') if found, otherwise None.
    """
    start = time.time()

    while timeout is None or time.time() - start < timeout:
        for port in serial.tools.list_ports.comports():
            if port.vid == vendor_id and port.pid == product_id:
                return port.device

    return None


def bit(n):
    """
    Return the nth bit of a byte.

    :param n: The bit number.
    :return: The bit value.
    """
    return 1 << n


def raise_(e):
    """
    Raise an exception.

    :param e: The exception to raise.
    """
    raise e


def to_bytes(value, size=1, endian='>'):
    """
    Convert an integer value to a byte representation.

    :param value: The integer value to convert.
    :param size: The size of the byte representation (1, 2, or 4 bytes).
    :param endian: The endianness of the byte representation ('>' for big-endian, '<' for little-endian).
    :return: The byte representation of the value.
    :raises RuntimeError: If an invalid size is specified.
    """
    return {
        1: lambda: struct.pack(endian + 'B', value),
        2: lambda: struct.pack(endian + 'H', value),
        4: lambda: struct.pack(endian + 'I', value),
    }.get(size, lambda: raise_(RuntimeError('invalid size')))()


def from_bytes(value, size=1, endian='>'):
    """
    Convert a byte representation to an integer value.

    :param value: The byte representation to convert.
    :param size: The size of the byte representation (1, 2, or 4 bytes).
    :param endian: The endianness of the byte representation ('>' for big-endian, '<' for little-endian).
    :return: The integer value represented by the bytes.
    :raises RuntimeError: If an invalid size is specified.
    """
    return {
        1: lambda: struct.unpack(endian + 'B', value)[0],
        2: lambda: struct.unpack(endian + 'H', value)[0],
        4: lambda: struct.unpack(endian + 'I', value)[0],
    }.get(size, lambda: raise_(RuntimeError('invalid size')))()
