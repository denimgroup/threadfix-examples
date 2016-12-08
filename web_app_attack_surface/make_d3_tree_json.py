#!/usr/bin/python

# import attack_surface_lib

from git import Git
from git import Repo
import json
from optparse import OptionParser
import os
import StringIO

execfile('attack_surface_lib.py')

parser = OptionParser()
parser.add_option('--sourcedir', dest='sourcedir', help='Directory containing the source code')
parser.add_option('--outfile', dest='outfile', help='Output filename for D3 JSON tree data')

(options, args) = parser.parse_args()

source_dir = options.sourcedir
outfile = options.outfile

print 'Source dir to command line: ' + source_dir
print 'Ouptut fie to command line: ' + outfile

attack_surface_json = generate_attack_surface_enumeration_json_from_source_dir(source_dir)
my_attack_surface = create_attack_surface_from_json_string(attack_surface_json)
d3_tree_json = my_attack_surface.print_to_json()

d3_json_file = open(outfile, 'w')
d3_json_file.write(d3_tree_json)
d3_json_file.close()

