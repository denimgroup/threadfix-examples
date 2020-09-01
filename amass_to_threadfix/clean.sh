#!/bin/bash

echo "Deleting results found so far"
rm amass_results.txt
echo "" > all_identified_hosts.txt

echo "Deleting Amass database"
rm db/amass.json
rm db/amass.log
rm db/indexes.bolt



