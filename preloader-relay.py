#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 R0rt1z2 <https://github.com/R0rt1z2>

import argparse
import logging

from src.device import Device


def main():
    parser = argparse.ArgumentParser(
        prog='preloader-relay',
        description="""
Replay Preloader traffic to run Download Agents that can execute arbitrary code.
The authors of this tool are not responsible for any misuse of this tool. Use this 
tool at your own risk and only on devices you have permission to test on.""",
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        '-i',
        dest='mode_identify',
        action='store_true',
        help='Read and print hardware information from the device',
    )
    mode.add_argument(
        '-d',
        dest='mode_download_agent',
        action='store_true',
        help='Upload and execute a download agent',
    )
    parser.add_argument(
        '--payload',
        dest='payload',
        type=str,
        default='bin/payload.bin',
        help='Path to the DA/payload to upload',
    )
    parser.add_argument(
        '-v',
        dest='verbose',
        action='store_true',
        help='Enable verbose output',
    )

    parser.add_argument(
        '-p',
        dest='port',
        type=str,
        help='The serial port to use',
    )
    parser.add_argument(
        '-s',
        dest='skip_handshake',
        action='store_true',
        help='Skip the handshake with the device',
    )

    args = parser.parse_args()

    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    device = Device(args.port)

    logging.info('Waiting for device...')

    device.find_device()

    if not args.skip_handshake:
        device.handshake()

    device.identify()

    if not args.mode_identify:
        da = open(args.payload, 'rb').read()
        logging.info(
            'Load payload from %s = 0x%08X bytes', args.payload, len(da)
        )
        device.send_da(0x200000, len(da), 0x00000100, da)
        device.jump_da(0x200000)


if __name__ == '__main__':
    main()
