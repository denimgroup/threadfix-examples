#!/usr/bin/python3

import os
import sys
from ThreadFixProApi import threadfixpro

def create_apps(tf_connection, team_id, raw_line):
    raw_line = raw_line.strip()
    print('Hosts to create apps for: ' + raw_line)
    individual_hosts = raw_line.split(' ')
    for host in individual_hosts:
        host = host.strip()
        if host != '':
            print("Creating ThreadFix app for host: '" + host + "'")
            result = tf_connection.ApplicationsAPI.create_application(team_id, host, 'https://' + host + "/")
            if result.success:
                print("Successfully created application: ' "+ host + "'")
            else:
                print("Problems creating application: '" + host + "'. Result: " + str(result))
        else:
            print('Blank hostname - will not create an application')


if len(sys.argv) < 4:
    print('Usage: amass_to_threadfix.py <tf_server> <api_key> <team>')
    exit(2)

tf_server = sys.argv[1]
api_key = sys.argv[2]
team = sys.argv[3]

create_all = False
if len(sys.argv) >= 5:
    if sys.argv[4] == '-all':
        create_all = True

print('Using tf_server: ' + tf_server)
print('Using api_key: ' + api_key)
print('Using team: ' + team)

# Get our connection to the ThreadFix server
tfp = threadfixpro.ThreadFixProAPI(tf_server, api_key, verify_ssl=False)

team_id = -1
team_json = tfp.TeamsAPI.get_team_by_name(team)
if team_json.success:
    team_id = team_json.data['id']
    print('Team: ' + team + ' has ID: ' + str(team_id))
else:
    print('Unable to find team: ' + team)
    exit(3)

# Check to see if this is the first time amass_alert.sh has been run.
# If it is, we'll need to grab -all- the outputs from this run and create
# apps for them. Otherwise the amass track results will get us what we need
# This may not be needed for newer versions of amass

is_first_run = True
if os.path.exists('db/indexes.bolt'):
    print('db/indexes.bolt exists - not first run')
    is_first_run = False
else:
    print('db/indexes.bolt does not exist - first run')


print('About to run amass_alert.sh script to find new hostnames')
os.system("./amass_alert.sh")

if is_first_run:
    print('First run. Opening amass_results.txt to get all entries')
    hosts_file = open('amass_results.txt', 'r')
    all_hosts_array = hosts_file.readlines()
    for host_line in all_hosts_array:
        host_line = host_line.strip()
        print("Host line: '" + host_line + "'")
        host_array = host_line.split()
        print('host_array: ' + str(host_array))
        # For some reason all the Amass data sources don't seem to have embedded whitespace
        # except for [Brute Forcing] results. And that sure does mess up what I expect
        # from my call to .split() So let's handle that...
        if host_array[0] == '[Brute':
            host_to_create = host_array[2]
        else:
            host_to_create = host_array[1]
        print("Host to create: '" + host_to_create + "'")
        create_apps(tfp, team_id, host_to_create)
else:
    print('Not a first run. Opening all_identified_hosts.txt to check on latest entries')
    hosts_file = open('all_identified_hosts.txt', 'r')
    all_hosts_array = hosts_file.readlines()
    if(create_all):
        print('Creating new ThreadFix applications for -all- identified hosts')
        for host_line in all_hosts_array:
            create_apps(tfp, team_id, host_line)
    else:
        print('Creating ThreadFix applicatiions for the most recently identified apps')
        if len(all_hosts_array) >= 1:
            create_apps(tfp, team_id, all_hosts_array[len(all_hosts_array) - 1])
        else:
            print('Hosts file had no records')


