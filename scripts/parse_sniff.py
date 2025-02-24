#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 R0rt1z2 <https://github.com/R0rt1z2>

import binascii
import sys

import pandas as pd

if len(sys.argv) < 2:
    print('Usage: python parser.py <csv_file>')
    sys.exit(1)

csv_file = sys.argv[1]

start_pattern = 'FF FF FF EA 90 0E 00 FA'
end_pattern = '6A BF C9 A8 D7 B0 33 E7'

min_length_pattern = """
6A BF C9 A8 D7 B0 33 E7 5F ED 48 45 B2 79 86 33
17 2A DE CA 0C 56 E8 C0 BD F9 3C 09 58 7D A0 72
""".strip().replace(' ', '')
min_data_length = len(min_length_pattern)

try:
    df = pd.read_csv(
        csv_file,
        sep=',',
        skipinitialspace=True,
        engine='python',
        on_bad_lines='skip',
    )

    df.columns = [col.strip() for col in df.columns]

    data_column = next((col for col in df.columns if 'Data' in col), None)
    record_column = next((col for col in df.columns if 'Record' in col), None)

    if data_column is None or record_column is None:
        exit('Error: Data or Record column not found in CSV file.')

    cdc_out_data = df[
        df[record_column]
        .astype(str)
        .str.contains('CDC OUT Data', case=False, na=False)
    ]

    if cdc_out_data.empty:
        exit('Error: CDC OUT Data not found in CSV file.')

    start_index = cdc_out_data[
        cdc_out_data[data_column]
        .astype(str)
        .str.contains(start_pattern, case=False, na=False)
    ].index
    end_index = cdc_out_data[
        cdc_out_data[data_column]
        .astype(str)
        .str.contains(end_pattern, case=False, na=False)
    ].index

    if start_index.empty or end_index.empty:
        exit('Error: Start or End pattern not found in CDC OUT Data.')

    start_idx = start_index[0]
    end_idx = end_index[0]

    if start_idx > end_idx:
        exit('Error: Start pattern found after End pattern in CDC OUT Data.')

    extracted_data = cdc_out_data.loc[start_idx:end_idx, data_column]

    filtered_data = extracted_data[
        extracted_data.astype(str).str.replace(' ', '').str.len()
        > min_data_length
    ]

    if filtered_data.empty:
        exit('No data extracted from CDC OUT Data.')

    hex_data = ' '.join(
        str(item) for item in filtered_data.fillna('').tolist()
    ).replace(' ', '')

    try:
        binary_data = binascii.unhexlify(hex_data)
    except binascii.Error as e:
        exit('Error converting hex data to binary data: %s' % e)

    with open('DA.bin', 'wb') as bin_file:
        bin_file.write(binary_data)

    print('Successfully extracted DA.bin file from CSV file.')

except Exception as e:
    print('Error: %s' % e)
