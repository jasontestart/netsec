#!/usr/bin/python3
# Python3 wrapper for nmap 
# Written by Jason Testart
# March 2020
import subprocess
import shlex
import os
import uuid
import xmltodict

# Set the location of nmap here
NMAP_PATH='/usr/bin/nmap'

# Method: scan
# given options for nmap, call nmap and fetch XML
# Return a dict respresentation of the XML
def scan(options):
    my_dict = None
    dev_null = open(os.devnull, 'wb')
    tmpfile_name = f'/tmp/nmapsslpy_{uuid.uuid4().hex[0:6]}.xml'
    testssl_cmd = f"{NMAP_PATH} -oX {tmpfile_name} -Pn {options}"
    args = shlex.split(testssl_cmd)
    testssl_result = subprocess.run(args, stdout=dev_null, stderr=dev_null)
    if not testssl_result.returncode:
        with open(tmpfile_name, 'r') as tmpfile:
            data = tmpfile.read()
            my_dict = xmltodict.parse(data)
    if os.path.exists(tmpfile_name):
        os.remove(tmpfile_name)
    return my_dict

# Run nmap with the "ssh-auth-methods" NSE script.
# NOTE: The scan is intrusive!
def get_auth_methods(host,port):
    options = f"--script ssh-auth-methods -p {port} {host}"
    xmldict = scan(options)
    port_result = xmldict['nmaprun']['host']['ports']['port']
    if not 'script' in port_result.keys():
        return None
    script_result = xmldict['nmaprun']['host']['ports']['port']['script']['table']['elem']
    methods = []
    if isinstance(script_result, list):
        for method in script_result:
            methods.append(method)
    else:
        methods.append(script_result)
    return methods
