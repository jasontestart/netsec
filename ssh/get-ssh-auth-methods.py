#!/usr/bin/python3
# Written by Jason Testart
# March 2020
#
# Given an IP address or CIDR netblock,
# this script will search Shodan for 
# Internet-exposed SSH servers,
# then use nmap to scan those servers
# to determine what SSH authentication
# methods are supported.
#
# ************** WARNING ****************
#
# The network scanning performed by this
# script is considered intrusive and should
# only be performed with express permission
# of the network/host owner.
#
# ***************************************
#

import nmapssh
import shodan
import my_shodan_api_key
import sys

# Given an IP address or netblock in CIDR notation,
# search Shodan for SSH servers and return a list
# of (hostname, ip address, tcp port) tuples
def build_host_list(cidr):
    hosts = []
    api = shodan.Shodan(my_shodan_api_key.KEY)
    query_str = f"ssh net:{cidr}"
    for entry in api.search_cursor(query_str):
        if 'ssh' in entry.keys():
            ip = entry['ip_str']
            port = entry['port']
            if entry['hostnames']:
                hostname = entry['hostnames'].pop()
            else:
                hostname = 'unknown'
            hosts.append((hostname,ip,port))
    return hosts


if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <IP address or CIDR range>")
    sys.exit(1)


print('hostname\tip\tport\tstatus\tauthentication methods')

total = 0
passed = 0
failed = 0
server_list = build_host_list(sys.argv[1])

for (hostname,ip,port) in server_list:
    supported_methods = None
    total += 1
    # First, get the list of supported methods
    try:
        supported_methods = nmapssh.get_auth_methods(ip,port)
    except:
        pass
    if supported_methods:
        method_str = ''
        status = 'WARN'
        if len(supported_methods) == 1:
            if 'publickey' in supported_methods:
                status = 'OK'
                passed += 1
            elif 'password' in supported_methods:
                status = 'FAIL'
                failed += 1
            method_str = supported_methods.pop()
        else:
            for method in supported_methods:
                method_str += f'{method} '
        print(f'{hostname}\t{ip}\t{port}\t{status}\t{method_str}')
    else:
        print(f'{hostname}\t{ip}\t{port}\tunknown\tunknown')

print(f'publickey only:\t{passed}')
print(f'password only:\t{failed}')
print(f'Total:\t{total}')
