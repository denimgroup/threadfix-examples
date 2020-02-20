#!/usr/bin/python3

import csv
import sys
from ThreadFixPythonApi import threadfixpro

def create_vuln_location(vulnerability):
	ret_val = 'Unknown'

	file_path = vulnerability['calculatedFilePath']
	path = vulnerability['path']
	parameter = vulnerability['parameter']

	ret_val = 'File Path: ' + str(file_path) + ' Path: ' + str(path) + ' Parameter: ' + str(parameter)

	return(ret_val)

def create_vuln_record(vulnerability):
	ret_val = None

	vuln_id = vulnerability['id']
	application = vulnerability['app']['name']
	generic_vulnerability = vulnerability['genericVulnerability']
	vuln_type = None
	if(generic_vulnerability != None):
		vuln_type = generic_vulnerability['name']
	else:
		vuln_type = 'Unspecified'
	severity = vulnerability['genericSeverity']['name']
	vuln_location = create_vuln_location(vulnerability)

	ret_val = [vuln_id, application, vuln_type, severity, vuln_location]

	return ret_val

if len(sys.argv) < 4:
  print('Usage: generate_exception_report.py <tf_server> <api_key> <outfile>')
  exit(2)

tf_server = sys.argv[1]
api_key = sys.argv[2]
outfile = sys.argv[3]

print('Using tf_server: ' + tf_server)
print('Using api_key: ' + api_key)
print('Using outfile: ' + outfile)

# Get our connection to the ThreadFix server
tfp = threadfixpro.ThreadFixProAPI(tf_server, api_key, verify_ssl=False)
# Get our output CSV file and write the header
csvoutfile = open(outfile, 'w')
csvout = csv.writer(csvoutfile)
header_list = ['Vulnerability ID', 'Application', 'Vulnerability Type', 'Severity', 'Location']
csvout.writerow(header_list)


# Optionally - Parse from command-line args
# In this ThreadFix installation, PCI has tag ID 1, exposure:public has tag ID 6, and env:production has tag ID 7
# The tags API will allow us to look up tag IDs by name
tags = [1, 6, 7]
# Generic severity 5 maps to Critical and 4 maps to High
generic_severities = [5, 4]
days_old = 30

page = 0
num_vulns_in_batch = -1

while num_vulns_in_batch != 0:
	vulnerabilities = tfp.VulnerabilitiesAPI.vulnerability_search(generic_severities=generic_severities, tags=tags, days_old=days_old, number_vulnerabilities=100, page=page, show_open=True, show_not_false_positive=True)
	if vulnerabilities.success:
		num_vulns_in_batch = len(vulnerabilities.data)
		print ('Found ' + str(num_vulns_in_batch) + ' vulnerabilities')
		for vulnerability in vulnerabilities.data:
			print(str(vulnerability))
			output_line_list = create_vuln_record(vulnerability)
			csvout.writerow(output_line_list)
	else:
		print("ERROR: {}".format(vulnerabilities.message))
	page = page + 1

csvoutfile.close()
