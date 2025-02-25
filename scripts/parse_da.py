#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 R0rt1z2 <https://github.com/R0rt1z2>

import argparse
import re
import struct
import sys
from datetime import datetime

import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()


class DAHeader:
    def __init__(self, data):
        self.da_id = data[0x20:0x60].rstrip(b'\0').decode('ascii')
        self.str_da_id = self._sanitize_da_id()
        (self.version,) = struct.unpack('<I', data[0x60:0x64])
        self.magic_number = data[0x64:0x68]
        (self.num_socs,) = struct.unpack('<I', data[0x68:0x6C])
        self.timestamp = self._extract_timestamp()

    def validate(self):
        if self.version != 4:
            raise ValueError('Unsupported version, expected 4.')
        if self.magic_number != b'\x99\x88\x66\x22':
            raise ValueError('Invalid magic number.')

    def _extract_timestamp(self):
        try:
            match = re.search(
                r'(\d{4}/\d{2}/\d{2}\.\d{2}:\d{2})', self.da_id
            )
            if match:
                dt = datetime.strptime(match.group(1), '%Y/%m/%d.%H:%M')
                return dt
            return None
        except (ValueError, IndexError):
            return None

    def _sanitize_da_id(self):
        try:
            sanitized = re.sub(r'_\d{4}/\d{2}/\d{2}\.\d{2}:\d{2}', '', self.da_id)
            sanitized = re.sub(r'\d{4}/\d{2}/\d{2}\.\d{2}:\d{2}', '', sanitized)
            sanitized = re.sub(r'/', '_', sanitized)
            sanitized = re.sub(r'\.', '_', sanitized)
            sanitized = re.sub(r'_+', '_', sanitized)
            return sanitized.strip('_')
        except Exception:
            return self.da_id

    def __str__(self):
        timestamp_str = (
            self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            if self.timestamp
            else 'Unknown'
        )
        return (
            'DA ID: %s\nVersion: %d\nMagic Number: %s\nNumber of SoCs: %d\nTimestamp: %s'
            % (
                self.str_da_id,
                self.version,
                self.magic_number.hex(),
                self.num_socs,
                timestamp_str,
            )
        )


class DAEntry:
    def __init__(self, data):
        fields = struct.unpack('<2sHIIIIIIIQIIIIIIIIIIIII128s', data)
        if fields[0] != b'\xda\xda':
            raise ValueError('Invalid DA Entry magic.')

        self.chip_id = fields[1]
        self.chip_version = fields[2]
        self.firmware_version = fields[3]
        self.extra_version = fields[4]

    def to_dict(self):
        return {
            'Chip ID': 'MT%X' % self.chip_id,
            'Chip Version': '0x%X' % self.chip_version,
            'Firmware Version': '0x%X' % self.firmware_version,
            'Extra Version': '0x%X' % self.extra_version,
        }

    def pretty_print(self):
        console.print('[bold cyan]Chip ID:[/] MT%X' % self.chip_id)
        console.print('[bold magenta]Chip Version:[/] 0x%X' % self.chip_version)
        console.print(
            '[bold yellow]Firmware Version:[/] 0x%X' % self.firmware_version
        )
        console.print(
            '[bold green]Extra Version:[/] 0x%X\n' % self.extra_version
        )

def display_soc_table(chip_data):
    print("\n")
    table = Table(title='Supported SoCs', show_lines=True, header_style='bold magenta')

    table.add_column('Chip ID', justify='center', style='cyan', no_wrap=True)
    table.add_column('Chip Version', justify='center', style='green')
    table.add_column('Firmware Version', justify='center', style='yellow')
    table.add_column('Extra Version', justify='center', style='red')

    for chip in chip_data:
        table.add_row(
            chip['Chip ID'],
            chip['Chip Version'],
            chip['Firmware Version'],
            chip['Extra Version']
        )
    console.print(table)

def main():
    parser = argparse.ArgumentParser(
        description='Parse MediaTek DA binary file.'
    )
    parser.add_argument('da_file', help='Input DA binary file')
    parser.add_argument('--extract', help='Extract DA body to specified file')
    parser.add_argument(
        '--export-csv', help='Export parsed chip info to CSV file'
    )
    args = parser.parse_args()

    try:
        with open(args.da_file, 'rb') as f:
            header_data = f.read(0x6C)
            header = DAHeader(header_data)
            header.validate()

            console.print(
                '\n[bold underline]Download Agent Information:[/bold underline]\n'
            )
            console.print(str(header), style='bold')

            chip_data = []

            for i in range(header.num_socs):
                entry_data = f.read(0xDC)
                if len(entry_data) != 0xDC:
                    console.print(
                        '[red]Warning:[/] Unexpected end of file, skipping remaining chips.'
                    )
                    continue
                try:
                    entry = DAEntry(entry_data)
                    chip_info = entry.to_dict()
                    chip_data.append(chip_info)
                except ValueError as ve:
                    console.print(
                        '[red]Warning:[/] %s for chip %d, skipping.' % (ve, i)
                    )

            if chip_data:
                display_soc_table(chip_data)

            if args.extract:
                da_binary = f.read()
                if da_binary:
                    with open(args.extract, 'wb') as da_file:
                        da_file.write(da_binary)
                    console.print(
                        '\n[green]Successfully extracted DA binary data to %s[/green]'
                        % args.extract
                    )
                else:
                    console.print(
                        '[yellow]Warning:[/] No DA binary data extracted.'
                    )

            if args.export_csv and chip_data:
                df = pd.DataFrame(chip_data)
                df.to_csv(args.export_csv, index=False)
                console.print(
                    '\n[green]Successfully exported chip data to %s[/green]'
                    % args.export_csv
                )
            elif args.export_csv:
                console.print('[yellow]No valid chip data found to export.[/]')

    except FileNotFoundError:
        sys.exit('Error: File "%s" not found.' % args.da_file)
    except ValueError as ve:
        sys.exit('Parsing error: %s' % ve)
    except Exception as e:
        sys.exit('Unexpected error: %s' % e)

if __name__ == '__main__':
    main()
