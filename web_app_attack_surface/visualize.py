#!/usr/bin/python

import json
from optparse import OptionParser

CONST_PRESENT = 'Present'


class AttackSurfaceElement:

	def __init__(self, pathfragment):
		self.pathfragment = pathfragment
		self.is_endpoint = False
		self._parameters = []
		self._children = []

	def getparameters(self):
		return self._parameters

	def setparameters(self, value):
		self._parameters = value
		self.is_endpoint = True

	def delparameters(self):
		del self._parameters
		self.is_endpoint = False

	parameters = property(getparameters, setparameters, delparameters, "I'm the list of parameters that can be passed to this AttackSurfaceElement.")

	def add_child(self, child):
		# TODO - Do we need to check the type of convert from strings if needed?
		self._children.append(child)

	def getchildren(self):
		return self._children

	children = property(getchildren, None, None, "I'm the list of children of this AttackSurfaceElement")

	def __str__(self):
		retVal = self.pathfragment
		if self.is_endpoint:
			retVal += '[' + ', '.join(self.parameters) + ']'
		return retVal
	
	

parser = OptionParser()
parser.add_option('--surfacejson', dest='surfacejson', help='JSON of attack surface')

(options, args) = parser.parse_args()

surface_json_filename = options.surfacejson

print 'JSON file with attack surface is: ' + surface_json_filename

surface_json = None
with open(surface_json_filename) as json_data:
	surface_json = json.load(json_data)

# print(surface_json)

my_element = AttackSurfaceElement('/url')
print my_element
my_element.parameters = ['one', 'two']
print my_element

attack_surface = { }
item_count = 0
for surface_location in surface_json:
	print '[' + str(item_count) + ']: URL: ' + surface_location['urlPath'] + ', Parameters: ' + ', '.join(surface_location['parameters'])
	parameters = { }
	for param in surface_location['parameters']:
		parameters[param] = CONST_PRESENT
	attack_surface[surface_location['urlPath']] = parameters
	item_count += 1
