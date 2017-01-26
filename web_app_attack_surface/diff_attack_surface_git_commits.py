#!/usr/bin/python

from git import Git
from git import Repo
import json
from optparse import OptionParser
import os
import StringIO

execfile('attack_surface_lib.py')

parser = OptionParser()
parser.add_option('--repolocation', dest='repolocation', help='Path to Git repository location')
parser.add_option('--branch', dest='branch', help='Branch in the Git repository')
parser.add_option('--start_commit', dest='start_commit', help='Starting Git commit for diffing')
parser.add_option('--end_commit', dest='end_commit', help='Ending Git commit for diffing')
parser.add_option('--calc_modified', action='store_true', dest='calc_modified', default=False, help='Calculate a list of the URLs whose behavior may have been modified (in addition to added/deleted)')

(options, args) = parser.parse_args()

# Set up Git stuff
repo_path = options.repolocation
branch = options.branch
start_commit = options.start_commit
end_commit = options.end_commit

calc_modified = options.calc_modified

git_diff_attack_surface = compare_git_commits(repo_path, branch, start_commit, end_commit, calc_modified)
print 'Differences between git commit: ' + start_commit + ' and commit: ' + end_commit
print 'Added attack surface: ' + ', '.join(git_diff_attack_surface.added)
print 'Deleted attack surface: ' + ', '.join(git_diff_attack_surface.deleted)
if calc_modified:
	print 'Modified attack surface: ' + ', '.join(git_diff_attack_surface.modified)
print 'Added percent: ' + str(git_diff_attack_surface.added_percent())
print 'Deleted percent: ' + str(git_diff_attack_surface.deleted_percent())
if calc_modified:
	print 'Modified percent: ' + str(git_diff_attack_surface.modified_percent())

