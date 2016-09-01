#!/usr/bin/python

import json
from threadfix_api import threadfix
from optparse import OptionParser
import urllib
import urllib2
from urlparse import urlparse
from xml.sax.saxutils import escape

########## Helper functions

SEVERITY_MAP = { '5' : 'Critical', '4' : 'High', '3' : 'Medium', '2' : 'Medium', '1' : 'Low', '0' : 'Info' }
TYPE_MAP = {	
		'Abuse of Functionality' : '999',
		'Application Code Execution' : '999',
		'Autocomplete Attribute' : '525',
		'Brute Force' : '307',
		'Clickjacking' : '999',
		'Content Spoofing' : '290',
		'Cross Site Request Forgery' : '352',
		'Cross Site Scripting' : '79',
		'Directory Indexing' : '999',
		'Fingerprinting' : '205',
		'Improper Input Handling' : '20',
		'Information Leakage' : '200',
		'Insufficient Anti-automation' : '799',
		'Insufficient Authorization' : '285',
		'Insufficient Password Policy Implementation' : '263',
		'Insufficient Password Recovery' : '640',
		'Insufficient Session Expiration' : '613',
		'Insufficient Transport Layer Protection' : '311',
		'Non-HttpOnly Session Cookie' : '565',
		'Predictable Resource Location' : '425',
		'Server Misconfiguration' : '16',
		'SQL Injection' : '89',
		'Unsecured Session Cookie' : '565',
		'URL Redirector Abuse' : '601'
		}
MISSING_TYPES = { }

def map_severity(severity):
	ret_val = 'Unknown'

	if severity in SEVERITY_MAP:
		ret_val = SEVERITY_MAP[severity]
	
	return(ret_val)

def map_class(the_class):
	ret_val = 'Unknown'

	if the_class in TYPE_MAP:
		ret_val = TYPE_MAP[the_class]
	else:
		print '*** Missing type ' + the_class
		MISSING_TYPES[the_class] = "PLACEHOLDER"
	
	return(ret_val)

def make_ssvl(vuln_list, dump_all=True):

	ssvl = ''

	ssvl += '<?xml version="1.0"?>\n'
	ssvl +='\t<Vulnerabilities SpecVersion="0.2"\n'
	ssvl += '\t\tApplicationTag="PRODUCTION_20110115"\n'
	ssvl += '\t\tExportTimestamp="2/13/2011 1:45:30 AM -06:00"\n'
	ssvl += '\t\txmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
	ssvl += '\t\txsi:noNamespaceSchemaLocation="ssvl.xsd">\n'
	for vuln in vuln_list:
		if dump_all or vuln['status'] == 'open':
			# print 'Writing vuln because dump_all = ' + str(dump_all) + ' and vuln_status = ' + vuln['status']
			ssvl += '\t\t\t<Vulnerability CWE="' + map_class(vuln['class']) + '" Severity="' + map_severity(vuln['severity']) + '">\n'
			ssvl += '\t\t\t\t<ShortDescription>\n'
			ssvl += '\t\t\t\t\t' + escape(vuln['description']) + '\n'
			ssvl += '\t\t\t\t</ShortDescription>\n'
			ssvl += '\t\t\t\t<LongDescription>\n'
			ssvl += '\t\t\t\t\t' + escape(vuln['solution']) + '\n'
			ssvl += '\t\t\t\t</LongDescription>\n'
			ssvl += '\t\t\t\t<Finding NativeID="' + vuln['id'] + '" Source="WhiteHat Sentinel">\n'
			ssvl += '\t\t\t\t\t<SurfaceLocation url="' + vuln['url'] + '" />\n'
			ssvl += '\t\t\t\t</Finding>\n'
			ssvl += '\t\t\t</Vulnerability>\n'
		# else:
			# print 'Skipping vuln because dump_all = ' + str(dump_all) + ' and vuln_status = ' + vuln['status']
	ssvl += '</Vulnerabilities>'

	return(ssvl)

########## Main body

parser = OptionParser()
parser.add_option('--whkey', dest='whkey', help='WhiteHat API key')
parser.add_option('--tfkey', dest='tfkey', help='ThreadFix API key')
parser.add_option('--tfserver', dest='tfserver', help='ThreadFix server URL')

(options, args) = parser.parse_args()

wh_key = options.whkey
wh_base_url = 'https://sentinel.whitehatsec.com/api/vuln/'

tf_key = options.tfkey
tf_url = options.tfserver

print 'WhiteHat API key: ' + wh_key
print 'ThreadFix API key: ' + tf_key
print 'ThreadFix Server URL: ' + tf_url

values = {'key' : wh_key,
		'format' : 'application/json' }
url_values = urllib.urlencode(values)

wh_url = wh_base_url + '?' + url_values

# print 'URL: ' + wh_url

try:
	data = urllib2.urlopen(wh_url)
	raw_json = data.read()
	# print 'Data returned:'
	# print raw_json

	parsed_json = json.loads(raw_json)

	print 'Parsed data:'
	vuln_list = parsed_json['collection']

	hosts = { }
	sites = { }
	vulns = { }

	for vuln in vuln_list:
		sites[vuln['site_name']] = 'VALUE'
		o = urlparse('http://' + vuln['url'])

		clean_hostname = o.netloc.strip()
		hosts[clean_hostname] = 'VALUE'

		detail_values = {'key' : wh_key,
				'format' : 'application/json',
				'display_description' : '1',
				'display_solution' : 1 }
		url_detail_values = urllib.urlencode(detail_values)

		wh_detail_url = wh_base_url + vuln['id'] + '?' + url_detail_values

		# print wh_detail_url

		detail_data = urllib2.urlopen(wh_detail_url)
		raw_detail_json = detail_data.read()

		print raw_detail_json
		parsed_detail_json = json.loads(raw_detail_json)


		vuln_dict = { }
		vuln_dict['id'] = vuln['id']
		vuln_dict['url'] = vuln['url']
		vuln_dict['class'] = vuln['class']
		vuln_dict['severity'] = vuln['severity']
		vuln_dict['status'] = vuln['status']
		vuln_dict['description'] = parsed_detail_json['description']['description']
		vuln_dict['solution'] = parsed_detail_json['solution']['solution']

		# print "descritpion is: " + vuln_dict['description']
		# print "solution is: " + vuln_dict['solution']


		sites_dict = {}
		if vuln['site_name'] in vulns:
			sites_dict = vulns[vuln['site_name']]
			print 'Retrieved sites_dict for: ' + vuln['site_name']
		else:
			sites_dict = { }
			print 'Created new sites_dict for: ' + vuln['site_name']


		vuln_list = []
		if clean_hostname in sites_dict:
			print 'Retrieved vuln_list for: ' + clean_hostname
			vuln_list = sites_dict[clean_hostname]
		else:
			vuln_list = [ ]
			print 'Created new vuln_list for: ' + clean_hostname
		vuln_list.append(vuln_dict)

		sites_dict[clean_hostname] = vuln_list
		vulns[vuln['site_name']] = sites_dict

	# print 'Sites:'
	# for site in sites:
	#	print site

	# print 'Unique hosts:'
	# for host in hosts:
	#	print host

	tf = threadfix.ThreadFixAPI(tf_url, tf_key, verify_ssl=False)
	tf_team = None;
	tf_application = None;

	#print 'Vulnerabilities:'
	for site in vulns:
		print 'Dumping vulns for Site: ' + site
		site_dict = vulns[site]

		tf_team = tf.create_team(site)

		for host in site_dict:
			print '    Dumping vulns for Host: ' + host
			# print 'Vulnerabilites for host: ' + host
			vuln_list = site_dict[host]
			# for vuln in vuln_list:
				# print 'ID: ' + vuln['id'] + ', URL: ' + vuln['url'] + ', Class: ' + vuln['class'] + ', Severity: ' + vuln['severity']
			# print 'Vulnerabilities for host in SSVL format:'
			ssvl = make_ssvl(vuln_list)
			# print ssvl

			tf_application = tf.create_application(tf_team.data['id'], host)

			filename = 'output/' + host.strip() + '.ssvl'
			print '    Creating file: ' + filename

			text_file = open(filename, 'w')
			text_file.write(ssvl)
			text_file.close()

			tf.upload_scan(tf_application.data['id'], filename)

			ssvl = make_ssvl(vuln_list, False)

			text_file = open(filename, 'w')
			text_file.write(ssvl)
			text_file.close()

			tf.upload_scan(tf_application.data['id'], filename)

except RuntimeError as e:
	print e.reason

