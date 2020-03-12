#!/usr/bin/python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from optparse import OptionParser
from threadfix_api import threadfix

import json
from riskiq.api import Client, FilterField, FilterValue, FilterOperation
from riskiq.render import renderer

parser = OptionParser()

# Command-line options for the network scan

# Command-line options for creating applicaitons in ThreadFix (optional)
parser.add_option('-c', '--create', action='store_true', dest='create', help='Auto-create applications in a ThreadFix server')
parser.add_option('-t', '--team', dest='team', help='ThreadFix team to which apps will be added.')
parser.add_option('-s', '--server', dest='server', help='ThreadFix server', default='http://localhost:8080/threadfix/')
parser.add_option('-k', '--apikey', dest='apikey', help='API key for ThreadFix server')

(options, args) = parser.parse_args()

# If we're going to push this data to ThreadFix, make sure we have the info
# we need - specifically the ThreadFix team that will house the applications

tf = None
tf_team = None

if options.create:
	tf = threadfix.ThreadFixAPI(options.server, options.apikey, verify_ssl=False)
	tf_team = tf.get_team_by_name(options.team)
	if tf_team.success:
		print ('Team {0} already exists. Will add applications to that team'.format(options.team))
	else:
		print ('Team {0} does not exist. Creating'.format(options.team))
		tf_team = tf.create_team(options.team)
		if tf_team.success:
			print ('Team {0} was created with id: {1}'.format(options.team, tf_team.data['id']))
		else:
			print ('Problem creating team: {0}'.format(tf_team.message))
			exit(1)
	print ('Going to create applications in ThreadFix server {0} under team {1}'.format(options.server, options.team))

# Query RiskIQ to request a list of the web sites they've discovered

print ('Querying RiskIQ to request list of discovered websites')

client = Client.from_config()
queryString = ''
filter = {'field':FilterField.AssetType, 'value':FilterValue.WebSite, 'type':FilterOperation.Equals}

results = client.post_inventory_search(queryString, filter)
inventory_assets = results['inventoryAsset']

for asset in inventory_assets:
	website = asset['webSite']
	print('Website identified: {0}'.format(website['initialUrl']))

	# Create the application in ThreadFix, if needed
	if options.create:
		application_name = website['initialUrl']
		# Use the application name also for the ThreadFix application URL because that is what RiskIQ gives us
		tf_application = tf.create_application(tf_team.data['id'], application_name, application_name)
		if tf_application.success:
			print ('Created application {0} under team {1}'.format(application_name, options.team))
		else:
			print ('Had problems creating application: {0}'.format(tf_application.message))
