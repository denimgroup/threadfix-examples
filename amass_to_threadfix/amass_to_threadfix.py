#!/usr/bin/python3

import os
import sys
from ThreadFixProApi import threadfixpro

def create_apps(tf_connection, team_id, raw_line):
    print('Hosts to create apps for: ' + raw_line)
    individual_hosts = raw_line.split(' ')
    for host in individual_hosts:
        host = host.rstrip()
        print("Creating ThreadFix app for host: '" + host + "'")
        result = tf_connection.ApplicationsAPI.create_application(team_id, host, 'https://' + host + "/")
        if result.success:
            print("Successfully created application: ' "+ host + "'")
        else:
            print("Problems creating application: '" + host + "'. Result: " + str(result))


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

print('About to run amass_alert.sh script to find new hostnames')
os.system("./amass_alert.sh")

print('Opening all_identified_hosts.txt to check on latest entries')
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


