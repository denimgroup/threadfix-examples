# Split WhiteHat Results and Load Into ThreadFix

This script allows you to pull data from a WhiteHat account where multiple applications are being scanned under a single WhiteHat Site.
The results are split into separate ThreadFix Applications based on the hostname associated with the vulnerability.
These results are then loaded into ThreadFix where each WhiteHat Site is turned into a ThreadFix Group, and each hostname's results are loaded into a different ThreadFix Application.
This is done by converting the WhiteHat results into (messy) SSVL.

This is a quick-and-dirty way to accomplish this split and isn't recommended for production use.
We're looking at better ways to accomplish this in a more sustainable manner.
BUT - for now this is an example of how this transformation can be accmomplished.
Quick and dirty.
