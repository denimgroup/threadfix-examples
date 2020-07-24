#!/usr/bin/python3

import datetime
import json
import sys

if len(sys.argv) < 3:
    print('Usage: eslint_converter.py <source_file> <destination_file>')
    exit(2)

source_file = sys.argv[1]
destination_file = sys.argv[2]

print('Converting ESLint JSON file: ' + source_file + ' to .threadfix file: ' + destination_file)

eslint_data = None
with open(source_file) as f:
    eslint_data = json.load(f)

# print (eslint_data)

output = { }

# Get the basics out of the way
output['collectionType'] = 'SAST'
output['source'] = 'ESLint'


# ESLint doesn't provide any time-of-run data, so just use the current time
time_string = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

output['created'] = str(time_string)
output['exported'] = str(time_string)

findings = []

file_entry_count = 0
for file_entry in eslint_data:
    print('File entry ' + str(file_entry_count) + ': ' + str(file_entry))

    file_name = file_entry['filePath']
    parameter = 'JUNK'

    message_list = file_entry['messages']
    message_count = 0
    for message in message_list:
        print('File entry ' + str(file_entry_count) + ', Message ' + str(message_count) + ': ' + str(message))

        finding = { }
        finding['summary'] = message['ruleId']
        finding['nativeSeverity'] = message['severity']

        findings.append(finding)

        message_count = message_count + 1
    file_entry_count = file_entry_count + 1

output['findings'] = findings

with open(destination_file, "w") as write_file:
    json.dump(output, write_file)
    write_file.close()