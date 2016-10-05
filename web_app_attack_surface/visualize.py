#!/usr/bin/python

from git import Git
from git import Repo
import json
from optparse import OptionParser
import os
import StringIO

CONST_PRESENT = 'Present'

def list_deleted(list1, list2):
	c = set(list1)
	d = set(list1).intersection(set(list2))
	return list(c - d)

def list_added(list1, list2):
	c = set(list2)
	d = set(list1).intersection(set(list2))
	return list(c - d)


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
			# print 'Got path_element: \'' + path_element + '\' from full_path: \'' + full_path + '\''
			if path_element not in current_attack_surface_element.children:
				# print 'Don\'t have \'' + path_element + '\' yet. Add this path element.'
				new_attack_surface_element = AttackSurfaceElement(path_element)
				if surface_location['parameters']:
					new_attack_surface_element.setparameters(surface_location['parameters'])
				current_attack_surface_element.children[path_element] = new_attack_surface_element
				current_attack_surface_element = new_attack_surface_element
			else:
				# print 'Have the element \'' + path_element + '\'. Moving forward.'
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

def make_list_from_json(my_json, element_name):
	ret_val = []

	for surface_location in my_json:
		ret_val.append(surface_location['urlPath'])

	return ret_val

class AttackSurfaceDiff:

	def __init__(self, orig, current):

		orig_path_list = make_list_from_json(orig, 'urlPath')
		current_path_list = make_list_from_json(current, 'urlPath')

		self.added = sorted(list_added(orig_path_list, current_path_list))
		self.deleted = sorted(list_deleted(orig_path_list, current_path_list))
		self.orig_path_count = len(orig_path_list)
		self.current_path_count = len(current_path_list)

	def print_to_json(self):
		ret_val = None
		output = StringIO.StringIO()

		output.write('{')
		output.write('"orig_path_count": ' + str(self.orig_path_count))
		output.write(',')
		output.write('"current_path_count": ' + str(self.current_path_count))
		output.write(',')
		output.write('"added":')
		output.write(make_json_string_list(self.added))
		output.write(',')
		output.write('"deleted":')
		output.write(make_json_string_list(self.deleted))
		output.write('}')

		ret_val = output.getvalue()
		output.close

		return ret_val


	def added_percent(self):
		ret_val = len(self.added) / float(self.orig_path_count)
		return ret_val

	def deleted_percent(self):
		ret_val = len(self.deleted) / float(self.orig_path_count)
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
parser.add_option('--diff_out', dest='diff_out', help='Output JSON for the attack surface diff')
parser.add_option('--repolocation', dest='repolocation', help='Path to Git repository location')
parser.add_option('--branch', dest='branch', help='Branch in the Git repository')
parser.add_option('--project', dest='project', help='Name of the project')
parser.add_option('--start_commit', dest='start_commit', help='Starting Git commit for diffing')
parser.add_option('--end_commit', dest='end_commit', help='Ending Git commit for diffing')

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
# print "Printing original JSON"
# print tree_json

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
	# print "Printing new JSON"
	# print tree_json_new

	if surface_json_out_filename_new:
		surface_json_out_new = open(surface_json_out_filename_new, "w")
		surface_json_out_new.write(tree_json_new)
		surface_json_out_new.close()


with open(surface_json_filename) as json_data:
	json_data_js = json.load(json_data)

with open(surface_json_filename_new) as json_data_new:
	json_data_new_js = json.load(json_data_new)

my_diff = AttackSurfaceDiff(json_data_js, json_data_new_js)

print 'Added attack surface: ' + ', '.join(my_diff.added)
print 'Deleted attack surface: ' + ', '.join(my_diff.deleted)

diff_json = my_diff.print_to_json()
print 'Diff JSON is: ' + diff_json
if options.diff_out:
	diff_out_file = open(options.diff_out, "w")
	diff_out_file.write(diff_json)
	diff_out_file.close()

print 'Added percent: ' + str(my_diff.added_percent())
print 'Deleted percent: ' + str(my_diff.deleted_percent())

def diff_attack_surface_files(start_file, end_file):
	with open(surface_json_filename) as json_data:
		json_data_js = json.load(json_data)

	with open(surface_json_filename_new) as json_data_new:
		json_data_new_js = json.load(json_data_new)

	ret_val = AttackSurfaceDiff(json_data_js, json_data_new_js)
	return ret_val


def make_attack_surface_filename(commit_name):
	ret_val = 'work/' + commit_name + '_attacksurface.json'
	return ret_val

def compare_git_commits(repo_path, branch, start_commit, end_commit):
	# print 'Repo path: ' + repo_path + ' and branch: ' + branch
	# print 'Starting commit: ' + start_commit + ', Ending commit: ' + end_commit

	repo = Repo(repo_path)
	git = Git(repo_path)
	head = repo.heads[0]

	cmd_str = 'java -jar bin/threadfix-endpoint-cli-2.4-SNAPSHOT-jar-with-dependencies.jar ' + repo_path + ' -json 2>/dev/null > ' + make_attack_surface_filename(start_commit)
	# print 'About to generate start attack surface with command: ' + cmd_str
	os.system(cmd_str)

	cmd_str = 'java -jar bin/threadfix-endpoint-cli-2.4-SNAPSHOT-jar-with-dependencies.jar ' + repo_path + ' -json 2>/dev/null > ' + make_attack_surface_filename(end_commit)
	# print 'About to generate end attack surface with command: ' + cmd_str
	os.system(cmd_str)

	ret_val = diff_attack_surface_files(make_attack_surface_filename(start_commit), make_attack_surface_filename(end_commit))
	return ret_val

# Set up Git stuff
repo_path = options.repolocation
branch = options.branch
start_commit = options.start_commit
end_commit = options.end_commit

git_diff_attack_surface = compare_git_commits(repo_path, branch, start_commit, end_commit)
print 'Differences between git commit: ' + start_commit + ' and commit: ' + end_commit
print 'Added attack surface: ' + ', '.join(git_diff_attack_surface.added)
print 'Deleted attack surface: ' + ', '.join(git_diff_attack_surface.deleted)
print 'Added percent: ' + str(git_diff_attack_surface.added_percent())
print 'Deleted percent: ' + str(git_diff_attack_surface.deleted_percent())

# This method is still pretty shaky
def generate_attack_surface_change_history(repo_path, branch, outfile_name):
	repo = Repo(repo_path)
	git = Git(repo_path)
	head = repo.heads[0]
	commits = list(repo.iter_commits(branch))
	commits.reverse()
	first = True
	previous_commit = None
	for commit in commits:
		if not first:
			attack_surface_diff = compare_git_commits(repo_path, branch, previous_commit.hexsha, commit.hexsha)
			current_path_count = attack_surface_diff.current_path_count
			added = len(attack_surface_diff.added)
			deleted = len(attack_surface_diff.deleted)
			print 'Start commit: ' + str(previous_commit.hexsha) + ', Current commit: ' + commit.hexsha + ', Count: ' + str(current_path_count) + ', Added: ' + str(added) + ', Deleted: ' + str(deleted)
		previous_commit = commit
		first = False

# generate_attack_surface_change_history(repo_path, branch, 'stuff')
