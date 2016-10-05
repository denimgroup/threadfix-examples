#!/usr/bin/python

import json
from optparse import OptionParser
import StringIO

CONST_PRESENT = 'Present'

def make_json_string_list(my_list):
	ret_val = '['
	first = True
	for my_item in my_list:
		if not first:
			ret_val = ret_val + ', '
		ret_val = ret_val + '"' + my_item + '"'
		first = False
	ret_val = ret_val + ']'
	return ret_val

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

class AttackSurfaceDiff:

	def __init__(self):
		self.added = []
		self.deleted = []

	def print_to_json(self):
		ret_val = None
		output = StringIO.StringIO()

		output.write('{')
		output.write('"added":')
		output.write(make_json_string_list(self.added))
		output.write(',')
		output.write('"deleted":')
		output.write(make_json_string_list(self.deleted))
		output.write('}')

		ret_val = output.getvalue()
		output.close

		return ret_val


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

def list_deleted(list1, list2):
	c = set(list1)
	d = set(list1).intersection(set(list2))
	return list(c - d)

def list_added(list1, list2):
	c = set(list2)
	d = set(list1).intersection(set(list2))
	return list(c - d)

# def _pretty_print_attack_surface_element(my_element):
#	ret_val = my_element.pathfragment
#	if my_element.children:
#		print 'Element has children: ' + str(my_element.children) + ' with type: ' + str(type(my_element.children)) + ' and keys: ' + str(my_element.children.keys())
#		ret_val = ret_val + ' {' + ', '.join(my_element.children.keys()) + '}'
#	return ret_val

# def _print_diff_status(orig_ptr, current_ptr, current_path_elements):
#	print 'STATUS: Original pathfragment: ' + _pretty_print_attack_surface_element(orig_ptr) + ', Current pathfragment: ' + _pretty_print_attack_surface_element(current_ptr) + ', path_elements: "' + '/'.join(current_path_elements) + '"'

def make_list_from_json(my_json, element_name):
	ret_val = []

	for surface_location in my_json:
		ret_val.append(surface_location['urlPath'])

	return ret_val

def calculate_attack_surface_diff(orig, current):
	ret_val = AttackSurfaceDiff()

	# orig_ptr = orig
	# current_ptr = current
	# current_path_elements = []

	orig_path_list = make_list_from_json(orig, 'urlPath')
	current_path_list = make_list_from_json(current, 'urlPath')

	# print '-----'
	# print 'orig_path_list: ' + ', '.join(orig_path_list)
	# print 'current_path_list: ' + ', '.join(current_path_list)
	
	ret_val.added = list_added(orig_path_list, current_path_list)
	ret_val.deleted = list_deleted(orig_path_list, current_path_list)

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
json_data = None
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
json_data_new = None
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


with open(surface_json_filename) as json_data:
	json_data_js = json.load(json_data)

with open(surface_json_filename_new) as json_data_new:
	json_data_new_js = json.load(json_data_new)

my_diff = calculate_attack_surface_diff(json_data_js, json_data_new_js)

print 'Added attack surface: ' + ', '.join(my_diff.added)
print 'Deleted attack surface: ' + ', '.join(my_diff.deleted)

diff_json = my_diff.print_to_json()
print 'Diff JSON is: ' + diff_json
