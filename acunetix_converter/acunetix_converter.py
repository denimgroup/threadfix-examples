#!/usr/bin/python3

import sys

if len(sys.argv) < 3:
    print('Usage: acunetix_converter.py <source_file> <destination_file>')
    exit(2)

source_file = sys.argv[1]
destination_file = sys.argv[2]

print('Converting Acunetix Pro XML file: ' + source_file + ' to Acunetix Standard XML file:' + destination_file)

