# Convert Acunetix Pro XML Exports for Upload to ThreadFix

This repository contains a simple Python utility to convert XML files exported from Acunetix Pro into the format needed to simulate Acunetix Standard uploads to ThreadFix. Please check back - native support for Acunetix Pro is in the works - this utility is merely a stopgap.

![Acunetix Pro Screen Shot](https://github.com/denimgroup/threadfix-examples/blob/master/acunetix_converter/screen_shot.png)

The reason this utility is needed is that ThreadFix checks inbound file uploads to determine the scanner type. Acunetix Standard XML files start with the tag sequence ScanGroup / Scan / Name / ShortName / StartURL / StartTime (and then have a bunch of additional info about the crawl, site structure. Acunetix Pro XML download files have a similar structure, but omit the Name / ShortName / StartURL / StartTime tags (as well as others) and jump right into ReportItems / ReportItem tags with the actual vulnerabilities. Also, Acunetix Standard outputs severities in lower case ("High" "Medium" etc) whereas Acunetix Pro capitalizes the severities ("High" "Medium" etc).
