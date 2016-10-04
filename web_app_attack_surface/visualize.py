#!/usr/bin/python

import json
from optparse import OptionParser
import StringIO

CONST_PRESENT = 'Present'

def create_attack_surface_from_json_string(json_string):
	surface_json = json.load(json_string)


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
				if surface_location['parameters']:
					new_attack_surface_element.setparameters(surface_location['parameters'])
				current_attack_surface_element.children[path_element] = new_attack_surface_element
				current_attack_surface_element = new_attack_surface_element
			else:
				print 'Have the element \'' + path_element + '\'. Moving forward.'
				current_attack_surface_element = current_attack_surface_element.children[path_element]
		item_count = item_count + 1

	return attack_surface


def _print_in_full_helper(self, output):
	output.write('{')
	param_str_fragment = None
	output.write('"name": "' + self.pathfragment)
	if self.getparameters():
		param_str_fragment = '[' + ", ".join(sorted(self.getparameters())) + ']'
		output.write(param_str_fragment)
	output.write('"')
	
	if bool(self._children):
		output.write(', "children": [')
		first = True;
		for child_name in sorted(self._children):
			if not first:
				output.write(', ')
			child_node = self._children[child_name]
			_print_in_full_helper(child_node, output)
			first = False
		output.write(']')

	else:
		output.write(', "size": 200')

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

	def print_to_json(self):
		output = StringIO.StringIO()
		_print_in_full_helper(self, output)

		# print output.getvalue()
		ret_val = output.getvalue()
		output.close()
		return ret_val


	
	

parser = OptionParser()
parser.add_option('--surfacejson', dest='surfacejson', help='JSON of attack surface')
parser.add_option('--surfacejsonout', dest='surfacejsonout', help='Output JSON for the attack surface visualization')
parser.add_option('--surfacejson_new', dest='surfacejson_new', help='JSON of attack surface')
parser.add_option('--surfacejsonout_new', dest='surfacejsonout_new', help='Output JSON for the attack surface visualization')

(options, args) = parser.parse_args()

surface_json_filename = options.surfacejson
surface_json_out_filename = options.surfacejsonout

surface_json_filename_new = options.surfacejson_new
surface_json_out_filename_new = options.surfacejsonout_new

print 'JSON file with attack surface is: ' + surface_json_filename

# Load up the attack surface JSON file
my_attack_surface = None
with open(surface_json_filename) as json_data:
	my_attack_surface = create_attack_surface_from_json_string(json_data)

tree_json = my_attack_surface.print_to_json()
print "Printing original JSON"
print tree_json

if surface_json_out_filename:
	surface_json_out = open(surface_json_out_filename, "w")
	surface_json_out.write(tree_json)
	surface_json_out.close()

my_attack_surface_new = None
if surface_json_filename_new:
	with open(surface_json_filename_new) as json_data_new:
		my_attack_surface_new = create_attack_surface_from_json_string(json_data_new)
	
	tree_json_new = my_attack_surface_new.print_to_json()
	print "Printing new JSON"
	print tree_json_new

	if surface_json_out_filename_new:
		surface_json_out_new = open(surface_json_out_filename_new, "w")
		surface_json_out_new.write(tree_json_new)
		surface_json_out_new.close()

