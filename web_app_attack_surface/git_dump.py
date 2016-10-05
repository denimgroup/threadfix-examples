#!/usr/bin/python

from git import Git
from git import Repo
from optparse import OptionParser
import os

parser = OptionParser()
parser.add_option('--repolocation', dest='repolocation', help='Path to Git repository location')
parser.add_option('--branch', dest='branch', help='Branch in the Git repository')
parser.add_option('--project', dest='project', help='Name of the project')

(options, args) = parser.parse_args()

repo_path = options.repolocation
project = options.project

branch = 'master'
if options.branch:
	branch = options.branch

print 'Repo path: ' + repo_path + ' and branch: ' + branch

repo = Repo(repo_path)
git = Git(repo_path)
head = repo.heads[0]

commits = list(repo.iter_commits(branch))
commits.reverse()
for commit in commits:
	print 'Commit: ' + commit.hexsha + ' with date: ' + str(commit.committed_date)
	git.checkout(commit.hexsha)
	cmd_str = 'java -jar bin/threadfix-endpoint-cli-2.4-SNAPSHOT-jar-with-dependencies.jar ' + repo_path + ' -json > work/' + project + '_attacksurface_' + str(commit.committed_date) + '.json'
	print 'About to generate attack surface with command: ' + cmd_str
	os.system(cmd_str)
