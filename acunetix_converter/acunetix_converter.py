#!/usr/bin/python3

import sys

if len(sys.argv) < 3:
    print('Usage: acunetix_converter.py <source_file> <destination_file>')
    exit(2)

source_file = sys.argv[1]
destination_file = sys.argv[2]

print('Converting Acunetix Pro XML file: ' + source_file + ' to Acunetix Standard XML file:' + destination_file)

infile = open(source_file, 'r')
outfile = open(destination_file, 'w')

start_url = None
start_time = None

REFERER = 'Referer: '
SCAN_GROUP = '<ScanGroup ExportedOn="'

for line in infile:
    # print('DEBUG:' + line.rstrip())
    index = line.find(REFERER)
    if start_url is None:
        if index != -1:
            start_url = line[index + len(REFERER): len(line) - 1]
            print('Found StartURL of: ' + start_url)
    
    index = line.find(SCAN_GROUP)
    if start_time is None:
        if index != -1:
            start_time = line[index + len(SCAN_GROUP): len(line) - 3]
            print('Found StartTime of: ' + start_time)


infile.close()

if start_url == None:
    start_url = 'http://localhost/'
    print('WARN: Unable to find valid StartURL. Defaulting to: ' + start_url)

if start_time == None:
    start_time = '01/01/2020, 12:12:12'
    print('WARN: Unable to find valid StartTime. Defaulting to: ' + start_time)

print('Using StartURL: ' + start_url)
print('Using StartTime: ' + start_time)


SCAN = '<Scan>'

infile = open(source_file, 'r')
for line in infile:
    outfile.write(line)

    index = line.find(SCAN)
    if index != -1:
        outfile.write('<Name><![CDATA[Scan Thread 1 ( ' + start_url + ' )]]></Name>\n')
        outfile.write('<ShortName><![CDATA[Scan Thread 1]]></ShortName>\n')
        outfile.write('<StartURL><![CDATA[' + start_url + ']]></StartURL>\n')
        outfile.write('<StartTime><![CDATA[' + start_time + ']]></StartTime>\n')

infile.close()
outfile.close()