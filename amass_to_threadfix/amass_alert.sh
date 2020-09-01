#!/bin/bash

# This is adapted from a script included with Amass Tutorial https://github.com/OWASP/Amass/blob/master/doc/tutorial.md

echo "About to run amass enum"
amass enum -src -active -df ./domains_to_monitor.txt -config ./regular_scan.ini -o ./amass_results.txt -dir ./db/ -brute -norecursive

echo "About to run amass track"
RESULT=$(amass track -df ./domains_to_monitor.txt -config ./regular_scan.ini -last 2 -dir ./db/ | grep Found | awk '{print $2}')
echo "Result of amass track is $RESULT"

echo "Calculating final result"
FINAL_RESULT=$(while read -r d; do if grep --quiet "$d" ./all_identified_hosts.txt; then continue; else echo "$d"; fi; done <<< $RESULT)

# if [[ -z "$FINAL_RESULT" ]];
if [[ -z "$FINAL_RESULT" ]]
then
    echo "No new subdomains were found"
else
    echo "New subdomains found. Writing to file."
    echo "$FINAL_RESULT" >> ./all_identified_hosts.txt
    echo "New subdomains are:"
    cat all_identified_hosts.txt
fi
