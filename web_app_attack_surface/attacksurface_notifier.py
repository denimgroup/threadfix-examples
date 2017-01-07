#!/usr/bin/python

from git import Git
from git import Repo
from hypchat import HypChat
from jira import JIRA
import json
from optparse import OptionParser
import os
import pprint
from slacker import Slacker
import StringIO
import time
from zapv2 import ZAPv2

execfile('attack_surface_lib.py')

def zap_scan_url(zap, api_key, full_url):
	print 'Going to ZAP scan URL: ' + full_url
	# Pull back the inital URL. This get is on the ZAP session's radar
	result = zap.core.access_url(apikey=api_key, url=full_url)
	time.sleep(2)

	# Spider that URL to collect the paramters. Otherwise ZAP doesn't seem to know about them
	result = zap.spider.scan(apikey=api_key, url=full_url, maxchildren=0, recurse=False, subtreeonly=True)
	print 'ZAP spider id: ' + result
	# Despite the spider waiting code below, for some reason ZAP isn't adding the URL with the parameters
	# to its list without this sleep() call. Probably something I'm doing wrong, but this hack works
	# for the moment
	time.sleep(5)
	while(int(zap.spider.status(result)) < 100):
		print 'Wainting for spider...'
		time.sleep(2)

	# Get the list of all URLs we've found and cycle through all of them. This will make
	# sure that we test the raw URL as well as the ZAP entries for that URL that have
	# parameters
	#
	# TODO - Probably need to move this process so it is only done once. Otherwise we re-scan earlier URLs
	# in situations where we have more than one new URL worty of attack surface
	all_urls = zap.core.urls
	for current_url in all_urls:
		print 'Starting specific scan for URL: ' + current_url
		result = zap.ascan.scan(apikey=api_key, url=current_url, recurse=False)
		print 'Result of starting scan: ' + result
	


parser = OptionParser()
parser.add_option('--repolocation', dest='repolocation', help='Path to Git repository location')
parser.add_option('--branch', dest='branch', help='Branch in the Git repository')

parser.add_option('--hipchat_token', dest='hipchat_token', help='HipChat API token')
parser.add_option('--hipchat_room', dest='hipchat_room', help='HipChat room name')

parser.add_option('--slack_token', dest='slack_token', help='Slack API token')
parser.add_option('--slack_room', dest='slack_room', help='Slack room name')

parser.add_option('--jira_username', dest='jira_username', help='JIRA username')
parser.add_option('--jira_password', dest='jira_password', help='JIRA password')
parser.add_option('--jira_url', dest='jira_url', help='JIRA server URL')
parser.add_option('--jira_project', dest='jira_project', help='JIRA project')

parser.add_option('--zap_server', dest='zap_server', help='ZAP server (do NOT include protocol - just server address)')
parser.add_option('--zap_token', dest='zap_token', help='ZAP API access token')
parser.add_option('--base_url', dest='base_url', help='Base URL for scanning')


(options, args) = parser.parse_args()

do_hipchat = False
do_slack = False
do_jira = False
do_zap = False

# Set up Git configuration
repo_path = options.repolocation
branch = options.branch
if branch == None:
	branch = 'master'

if repo_path == None:
	print 'Must enter a Git repository path. Exiting.'
	exit(-1)

# Set up HipChat stuff
hipchat_access_token = options.hipchat_token
hipchat_room_name = options.hipchat_room
hc = None
hc_room = None

if hipchat_access_token != None:
	do_hipchat = True
	print 'Will be sending messages to HipChat room: ' + hipchat_room_name
	hc = HypChat(hipchat_access_token)
	hc_room = hc.get_room(hipchat_room_name)

# Set up Slack stuff
slack_access_token = options.slack_token
slack_room_name = options.slack_room
slack = None

if slack_access_token != None:
	do_slack = True
	print 'Will be sending message to Slack channel: ' + slack_room_name
	slack = Slacker(slack_access_token)

# Set up JIRA stuff
jira_url = options.jira_url
jira_project = None
jira_connection = None

if jira_url != None:
	do_jira = True
	jira_project = options.jira_project
	print 'Will be creating issues for JIRA project: ' + jira_project
	jira_username = options.jira_username
	jira_password = options.jira_password

	jira_options = {'server': jira_url}
	jira_connection = JIRA(options=jira_options, basic_auth=(jira_username, jira_password))

# Set up Git stuff

repo = Repo(repo_path)
git = Git(repo_path)
head = repo.heads[0]
commits = list(repo.iter_commits(branch))

starting_commit_hash = commits[0].hexsha

# Set up ZAP stuff
zap_server = options.zap_server

zap = None
zap_token = None
base_url = None
result = None

if zap_server != None:
	do_zap = True
	zap_token = options.zap_token
	base_url = options.base_url
	print 'Will be running ZAP scans via ZAP server at: ' + zap_server
	print 'Base URL for new attack surface will be: ' + base_url
	zap = ZAPv2(proxies={'http': 'http://' + zap_server, 'https': 'https://' + zap_server})
	result = zap.core.new_session(apikey=zap_token)

# Say howdy

hello_message = 'ThreadFix Attack Surface bot is now active and we are keeping an eye on branch ' + branch + ' starting with commit ' + starting_commit_hash
if do_hipchat:
	hc_room.message(hello_message)

if do_slack:
	slack.chat.post_message(slack_room_name, hello_message)

while 1:
	# Check current commit
	git.checkout(branch)
	repo.remotes.origin.pull()
	commits = list(repo.iter_commits(branch))
	latest_commit_hash = commits[0].hexsha
	if latest_commit_hash != starting_commit_hash:
		# Have a new commit. Let's see if there are changes
		print 'Have a new commit: ' + latest_commit_hash
		print 'Checking attack surface for changes'
		attack_surface_diff = compare_git_commits(repo_path, branch, starting_commit_hash, latest_commit_hash)
		if len(attack_surface_diff.added) > 0 or len(attack_surface_diff.deleted) > 0:
			# Attack surface has changed!
			zap_report = None

			# Only need to test NEW attack surface with ZAP
			if do_zap and attack_surface_diff.added > 0:
				# Scan each of the new URLs
				for new_page in attack_surface_diff.added:
					full_url = base_url + new_page
					zap_scan_url(zap, zap_token, full_url)

				# Wait for all scans to finish because all the scans were queued up
				# asynchronously earlier
				scans = zap.ascan.scans
				for scan_info in scans:
					scan_id = scan_info['id']
					while(int(zap.ascan.status(scan_id)) < 100):
						time.sleep(2)
				results = zap.core.alerts()
				results_we_care_about = list()
				for result in results:
					# For our purposes here, we only care about High results
					if result['risk'] == 'High':
						results_we_care_about.append(result)

				if len(results_we_care_about) > 0:
					# zap_report = pprint.pformat(results_we_care_about)
					zap_report = ''
					for result in results_we_care_about:
						zap_report += result['alert'] + ' was found in new URL: ' + result['url'] + ' and parameter: ' + result['param'] + '\nFor further background on this type of vulnerability, see: ' + result['reference'] + '\n'
					print 'ZAP report:'
					print zap_report


			# Only need to report NEW attack surface to JIRA
			if do_jira and attack_surface_diff.added > 0:
				issue_summary = 'Manual pen test new attack surface'
				issue_detail = 'Perform a manual penetration test for new attack surface:\n'
				issue_detail += 'Added attack surface: ' + ', '.join(attack_surface_diff.added)

				new_issue = jira_connection.create_issue(project=jira_project, summary=issue_summary, description=issue_detail, issuetype={'name': 'Bug'})

			# Report any attack surface changes to the chat rooms. Include ZAP results if available

			chat_message = 'The ThreadFix Attack Surface chat bot has identified that commit: ' + latest_commit_hash + '\n'
			chat_message += 'Added attack surface: ' + ', '.join(attack_surface_diff.added) + '\n'
			chat_message += 'Deleted attack surface: ' + ', '.join(attack_surface_diff.deleted) + '\n'

			if zap_report != None:
				chat_message += '\nResults of ZAP Scan:\n'
				chat_message += zap_report + '\n'

			print chat_message

			if do_hipchat:
				hc_room.message(chat_message)

			if do_slack:
				slack.chat.post_message(slack_room_name, chat_message)
			
			print 'Updating latest commit to: ' + latest_commit_hash
			starting_commit_hash = latest_commit_hash
		else:
			print 'No attack surface change'
	else:
		print 'Latest commit is still: ' + starting_commit_hash
	time.sleep(10)
