#!/usr/bin/python
#

import pprint
import time
from zapv2 import ZAPv2

target = 'http://localhost'
# This has been changed, so please no one get too excited about sensitive data in git repositories...
apikey = 'nssfdfbktnk0ap1kbgudfq51vf'
baseUrl = 'http://localhost/bodgeit/'
targetPage = 'search.jsp'
# targetPage = 'basket.jsp'
fullUrl = baseUrl + targetPage

zap = ZAPv2()
zap = ZAPv2(proxies={'http': 'http://127.0.0.1:8088', 'https': 'http://127.0.0.1:8088'})

# Get a new session so we start with a clean slate
result = zap.core.new_session(apikey=apikey)
time.sleep(2)

# Pull back the initial URL. This gets it on the ZAP session's radar
print 'Accessing page: ' + fullUrl
result = zap.core.access_url(apikey=apikey, url=fullUrl)
time.sleep(2)

# Spider that URL to collect the parameters. Otherwise ZAP doesn't seem to know about them
result = zap.spider.scan(apikey=apikey, url=fullUrl, maxchildren=0, recurse=False, subtreeonly=True)
print 'Spider: ' + result + ' initiated'
time.sleep(2)
print 'Waiting for spidering to complete'
while (int(zap.spider.status(result)) < 100):
	print 'Waiting...'
	time.sleep(2)


# Get the list of all URLs we've found and cycle through all of them. This will make
# sure that we test the raw URL as well as the ZAP entries for that URL that have
# parameters
allUrls = zap.core.urls
# print 'Result: ' + str(result)
for currentUrl in allUrls:
	print 'Running active scan of URL: ' + currentUrl
	result = zap.ascan.scan(apikey=apikey, url=currentUrl, recurse=False)
	print 'Result: ' + str(result)

# Wait for all scans to finish because the calls to ascan.scan() are asynchronous
scans = zap.ascan.scans
for scan_info in scans:
	scan_id = scan_info['id']
	print 'Waiting for scan: ' + scan_id + ' to complete'
	while(int(zap.ascan.status(scan_id)) < 100):
		print 'Waiting...'
		time.sleep(2)
	print 'Scan: ' + scan_id + ' has completed'

results = zap.core.alerts()
results_we_care_about = list()
for result in results:
	# For our purposes here, we only care about High results
	if result['risk'] == 'High':
		results_we_care_about.append(result)
output = 'No important results found'
if len(results_we_care_about) > 0:
	output = pprint.pformat(results_we_care_about)
print output
