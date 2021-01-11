 # SSH authentication methods

The network at work has thousands of hosts and hundreds of SSH servers
exposed to the Internet. The network is a wild west of researchers,
so in a drive to rid ourselves of password-only authentication
everywhere, I wrote some scripts that will grab a list of 
Internet-facing SSH servers from Shodan, and then determine
the supported authentication methods for each server by
using nmap.

**NOTE: These nmap scans are considered intrusive, so
permission from the network owner should be obtained 
before performing such scans.**
