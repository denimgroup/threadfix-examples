#!/usr/bin/python

import json
from optparse import OptionParser
import StringIO

CONST_PRESENT = 'Present'

def _print_in_full_helper(self, output):
	output.write('{')
	if self.is_endpoint:
		output.write('"name": "' + self.pathfragment + '", "children": [')
		first = True
		for param in self._parameters:
			if not first:
				# Append ", "
				output.write(', ')
			output.write('{"name": "' + param + '", "size": 100}')
			first = False
		output.write(']')

	else:
		output.write('"name": "' + self.pathfragment + '", ')
		if bool(self._children):
			# There are children
			output.write('"children": [')
			first = True;
			for child_name in self._children:
				if not first:
					output.write(', ')
				child_node = self._children[child_name]
				_print_in_full_helper(child_node, output)
				first = False
			output.write(']')

		else:
			# No children. Make an endpoint
			output.write('"size": 200')

	output.write('}')

class AttackSurfaceElement:

	def __init__(self, pathfragment):
		self.pathfragment = pathfragment
		self.is_endpoint = False
		self._parameters = []
		self._children = { }

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

	def print_in_full(self):
		output = StringIO.StringIO()
		_print_in_full_helper(self, output)

		print output.getvalue()
		output.close()



	
	

parser = OptionParser()
parser.add_option('--surfacejson', dest='surfacejson', help='JSON of attack surface')

(options, args) = parser.parse_args()

surface_json_filename = options.surfacejson

print 'JSON file with attack surface is: ' + surface_json_filename

# Load up the attack surface JSON file
surface_json = None
with open(surface_json_filename) as json_data:
	surface_json = json.load(json_data)


attack_surface = AttackSurfaceElement('/')
item_count = 0
for surface_location in surface_json:
	print '[' + str(item_count) + ']: URL: ' + surface_location['urlPath'] + ', Parameters: ' + ', '.join(surface_location['parameters'])

	full_path = surface_location['urlPath']
	path_elements = full_path.split('/')

	current_attack_surface_element = attack_surface
	for path_element in path_elements:
		print 'Got path_element: \'' + path_element + '\' from full_path: \'' + full_path + '\''
		if path_element not in current_attack_surface_element.children:
			print 'Don\'t have \'' + path_element + '\' yet. Add this path element.'
			new_attack_surface_element = AttackSurfaceElement(path_element)
			current_attack_surface_element.children[path_element] = new_attack_surface_element
			current_attack_surface_element = new_attack_surface_element
		else:
			print 'Have the element \'' + path_element + '\'. Moving forward.'
			current_attack_surface_element = current_attack_surface_element.children[path_element]

	# parameters = { }
	# for param in surface_location['parameters']:
	#	parameters[param] = CONST_PRESENT
	# attack_surface[surface_location['urlPath']] = parameters
	# item_count += 1

attack_surface.print_in_full()
