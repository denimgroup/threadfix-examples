#!/usr/local/bin/python3

import datetime
import defusedxml
from defusedxml import ElementTree as ET
import hashlib
import json
import sys

# Fields we need to bring over
#
# Vuln ID
# CWE ID
# Vuln Title
# Severity
# Description
# Recommendation
# Steps To Reproduce
# Vuln url

# Convert CVSS float scores to string severity representation
def convert_to_severity(severity_string):
    print("Checking severity string of: " + severity_string)
    ret_val = 'Unassigned'
    if severity_string == 'Critical':
        ret_val = 'Critical'
    elif severity_string == 'High':
        ret_val = 'High'
    elif severity_string == 'Medium':
        ret_val = 'Medium'
    elif severity_string == 'Low':
        ret_val = 'Low'
    elif severity_string == 'Minimal':
        ret_val = 'Info'
    return(ret_val)


if len(sys.argv) < 3:
    print("usage: synopsys3d_to_threadfix.py <input_file> <output_file>")
    exit(1)

infile = sys.argv[1]
outfile = sys.argv[2]

print ("Input file will be: " + infile)
print ("Output file will be: " + outfile)

tree = ET.parse(infile)
root = tree.getroot()

print ("Root: " + root.tag)

output = { }

# Get the basics out of the way
output['collectionType'] = 'DAST'
output['source'] = 'Synopsys3D'

# Pull in the created time and do the date string conversion stuff
elems = root.findall("summary/test_end_time")
print ("Found element: " + str(elems))
created_string = elems[0].text.strip()
print("Created string: " + created_string)

# TOFIX - Parse the provided date and output it in the require format
# created_date = datetime.datetime.strptime(created_string, '%m.%d.%Y %H:%M:%S')
# yyyy-MM-dd'T'HH:mm:ss'Z' 
# created_date_string = datetime.datetime.strftime(created_date, '%Y-%m-%dT%H:%M:%SZ')
output['created'] = str(created_string)
output['exported'] = str(created_string)

# Build the findings list
elems = root.findall("webapp_vulnerabilities/vulnerability")
# vulnerability_list = vulas_data['vulasReport']['vulnerabilities']
finding_list = [ ]
for vulnerability_elem in elems:
    print ('Processing finding: ' + str(len(finding_list)))

    finding_dict = { }


    # Sort out the severity
    # cvss_string = vulnerability_dict['bug']['cvssScore']
    # try:
    #     cvss_score = float(cvss_string)
    # except ValueError:
    #     cvss_score = 0.0
    #
    # severity_string = convert_cvss_to_severity(cvss_score)
    native_severity = vulnerability_elem.findall("severity")[0].text.strip()
    print ("Native severity: " + native_severity)
    
    # TOFIX - Be able to convert Synopsys severity to our severities
    severity_string = convert_to_severity(native_severity)
    print ("Severity string: " + severity_string)

    finding_dict['severity'] = severity_string
    finding_dict['nativeSeverity'] = native_severity

    # Craft a description
    # summary = vulnerability_dict['bug']['id'] + ' in ' + vulnerability_dict['filename']
    summary = vulnerability_elem.findall("vulnerability_title")[0].text.strip()
    print ("Summary: " + summary)
    finding_dict['summary'] = summary
    description = vulnerability_elem.findall("vulnerability_descriptions/vulnerability_description")[0].text.strip()
    # print ("Description: " + description)
    finding_dict['description'] = description

    # Sort out the native ID as a has of the CVE and filename
    native_id = vulnerability_elem.findall("vulnerability_id")[0].text.strip()
    print ("Vulnerability ID/Native ID: " + native_id)
    finding_dict['nativeId'] = native_id

    # Bundle up the finding details
    finding_details_dict = { }
    # finding_details_dict['library'] = vulnerability_dict['filename']
    # finding_details_dict['description'] = summary
    # finding_details_dict['issueType'] = 'VULNERABILITY'
    # finding_details_dict['reference'] = vulnerability_dict['bug']['id']
    # finding_dict['dependencyDetails'] = finding_details_dict

    finding_list.append(finding_dict)

output['findings'] = finding_list

with open(outfile, "w") as write_file:
    json.dump(output, write_file)
    write_file.close()
