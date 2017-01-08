#!/usr/bin/python

from optparse import OptionParser
import sys
# sys.path.append('./threadfix-endpoint-cli-2.4-SNAPSHOT-jar-with-dependencies.jar')
from java.io import File
from com.denimgroup.threadfix.framework.engine.full import EndpointDatabase
from com.denimgroup.threadfix.framework.engine.full import EndpointDatabaseFactory

parser = OptionParser()
parser.add_option('--code_path', dest='code_path', help='Location of source code to model')
(options, args) = parser.parse_args()

print 'Using the attack surface calculation library via Jython'

code_path = options.code_path

print 'Will calculate attack surface for code located at: ' + code_path

the_file = File(code_path)

endpoint_database = EndpointDatabaseFactory.getDatabase(the_file)
endpoints = endpoint_database.generateEndpoints()

for endpoint in endpoints:
	print str(endpoint)
