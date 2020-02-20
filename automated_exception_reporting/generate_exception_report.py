#!/usr/bin/python3

import csv
import sys
from ThreadFixPythonApi import threadfixpro

def make_tags_list(tf_con, tags):
	ret_val = []

	my_tags = tags.split(',')
	for tag_name in my_tags:
		tag_id = tf_con.TagsAPI.get_tag_by_name(tag_name)
		if tag_id.success:
			ret_val.append(tag_id.data[0]['id'])

	return(ret_val)

def make_severities_list(severities):
	ret_val = []

	severity_list = severities.split(',')
	for severity in severity_list:
		if(severity == 'Critical'):
			ret_val.append(5)
		elif(severity == 'High'):
			ret_val.append(4)
		elif(severity == 'Medium'):
			ret_val.append(3)
		elif(severity == 'Low'):
			ret_val.append(2)
		elif(severity == 'Info'):
			ret_val.append(1)
		else:
			print('Got unknown severity: '  +  severity)

	return(ret_val)

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

if len(sys.argv) < 7:
  print('Usage: generate_exception_report.py <tf_server> <api_key> <outfile> <tags> <severities> <aging>')
  exit(2)

tf_server = sys.argv[1]
api_key = sys.argv[2]
outfile = sys.argv[3]
tags = sys.argv[4]
severities = sys.argv[5]
aging = sys.argv[6]

print('Using tf_server: ' + tf_server)
print('Using api_key: ' + api_key)
print('Using outfile: ' + outfile)
print('Using tags: ' + tags)
print('Using severities: ' + severities)
print('Using aging: ' + aging)

# Get our connection to the ThreadFix server
tfp = threadfixpro.ThreadFixProAPI(tf_server, api_key, verify_ssl=False)
# Get our output CSV file and write the header
csvoutfile = open(outfile, 'w')
csvout = csv.writer(csvoutfile)
header_list = ['Vulnerability ID', 'Application', 'Vulnerability Type', 'Severity', 'Location']
csvout.writerow(header_list)


# Look up the tags from the command line
tags_list = make_tags_list(tfp, tags)
severities_list = make_severities_list(severities)

page = 0
num_vulns_in_batch = -1

while num_vulns_in_batch != 0:
	vulnerabilities = tfp.VulnerabilitiesAPI.vulnerability_search(generic_severities=severities_list, tags=tags_list, days_old=aging, number_vulnerabilities=100, page=page, show_open=True, show_not_false_positive=True)
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
