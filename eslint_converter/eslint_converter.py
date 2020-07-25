#!/usr/bin/python3

import datetime
import hashlib
import json
import sys

def convert_to_severity(severity):
    print("Checking severity value of: " + str(severity))
    ret_val = 'Unassigned'

    if severity == 2:
        ret_val = 'High'
    elif severity == 1:
        ret_val = 'Medium'
    elif severity == 0:
        ret_val = 'Info'

    return(ret_val)



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
    # Not sure why SAST findings require a parameter, so let's punt
    parameter = ''

    message_list = file_entry['messages']
    message_count = 0
    for message in message_list:
        print('File entry ' + str(file_entry_count) + ', Message ' + str(message_count) + ': ' + str(message))

        if file_entry['errorCount'] == 0 and file_entry['warningCount'] == 0:
            continue

        source_code = file_entry['source']
        source_code_array = source_code.split('\n')

        finding = { }
        if message['ruleId'] == None:
            finding['summary'] = 'Parse error'
        else:
            finding['summary'] = message['ruleId']
        finding['description'] = message['message']
        finding['nativeSeverity'] = message['severity']
        tf_severity = convert_to_severity(message['severity'])
        finding['severity'] = tf_severity

        static_details = { }

        static_details['file'] = file_name
        static_details['parameter'] = parameter

        data_flow = { }

        data_flow['file'] = file_name
        data_flow['lineNumber'] = message['line']
        data_flow['columnNumber'] = message['column']
        data_flow['text'] = source_code_array[message['line'] - 1]

        # ruleId can be null for parse errors
        full_identifier = file_name + ':' + str(message['ruleId']) + ':' + file_name + ':' + str(message['line']) + ':' + str(message['column'])
        finding['nativeId'] = hashlib.sha256(full_identifier.encode('utf-8')).hexdigest()

        static_details['dataFlow'] = [ data_flow ]
    
        finding['staticDetails'] = static_details

        findings.append(finding)

        message_count = message_count + 1
    file_entry_count = file_entry_count + 1

output['findings'] = findings

with open(destination_file, "w") as write_file:
    json.dump(output, write_file)
    write_file.close()