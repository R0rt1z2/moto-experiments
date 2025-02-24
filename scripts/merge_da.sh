#!/bin/bash

HEADER_LENGTH=$((0x39DC))

show_help() {
    cat <<EOF
USAGE: ${0##*/} [OPTION]... SOURCE_DA BODY_DA OUTPUT_DA
Extract header from SOURCE_DA and merge it with BODY_DA to create OUTPUT_DA.

EXAMPLE:
  ${0##*/} source_da.bin body_da.bin output_da.bin

OPTIONS:
  -h, --help       Display this help message and exit
  -v, --version    Display version information and exit

DESCRIPTION:
  This script extracts the first $HEADER_LENGTH bytes from SOURCE_DA as the header
  and concatenates it with the BODY_DA to produce OUTPUT_DA.

EOF
}

show_version() {
    echo "${0##*/} version 1.0.0"
}

if [[ $# -eq 0 || "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
    exit 0
elif [[ "$1" == "--version" || "$1" == "-v" ]]; then
    show_version
    exit 0
elif [[ $# -ne 3 ]]; then
    echo "ERROR: Invalid number of arguments."
    echo "Try '${0##*/} --help' for more information."
    exit 1
fi

SOURCE_DA=$1
BODY_DA=$2
OUTPUT_DA=$3

if [[ ! -f "$SOURCE_DA" ]]; then
    echo "ERROR: Source DA file '$SOURCE_DA' does not exist."
    exit 1
fi

if [[ ! -f "$BODY_DA" ]]; then
    echo "ERROR: Body DA file '$BODY_DA' does not exist."
    exit 1
fi

head -c $HEADER_LENGTH "$SOURCE_DA" > header.bin
cat header.bin "$BODY_DA" > "$OUTPUT_DA"

rm header.bin

echo "Header extracted from '$SOURCE_DA' and merged with body from '$BODY_DA'."
echo "Output saved to '$OUTPUT_DA'."
