#!/bin/bash

HEADER_LENGTH=$((0x39DC))

show_help() {
    cat <<EOF
USAGE: ${0##*/} [OPTION]... SOURCE_DA OUTPUT_BODY
Extract the body of SOURCE_DA by removing its header and save it as OUTPUT_BODY.

EXAMPLE:
  ${0##*/} source_da.bin output_body.bin

OPTIONS:
  -h, --help       Display this help message and exit
  -v, --version    Display version information and exit

DESCRIPTION:
  This script removes the first $HEADER_LENGTH bytes from SOURCE_DA and saves the remaining data (body) into OUTPUT_BODY.

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
elif [[ $# -ne 2 ]]; then
    echo "ERROR: Invalid number of arguments."
    echo "Try '${0##*/} --help' for more information."
    exit 1
fi

SOURCE_DA=$1
OUTPUT_BODY=$2

if [[ ! -f "$SOURCE_DA" ]]; then
    echo "ERROR: Source DA file '$SOURCE_DA' does not exist."
    exit 1
fi

tail -c +$((HEADER_LENGTH + 1)) "$SOURCE_DA" > "$OUTPUT_BODY"

echo "Header removed from '$SOURCE_DA'."
echo "Body saved to '$OUTPUT_BODY'."
