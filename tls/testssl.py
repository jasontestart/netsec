#!/usr/bin/python3
# Python3 wrapper for testssl.sh
# Written by Jason Testart
# March 2020

import subprocess
import shlex
import os
import json


# Method: testssl
# given a hostname or IP address, call testssl.sh and fetch json
# Return a JSON object
def testssl(host,port):
    dev_null = open(os.devnull, 'wb')
    tmpfile_name = f'/tmp/testssl_{os.getpid()}.json'
    if os.path.exists(tmpfile_name):
        os.remove(tmpfile_name)
    testssl_cmd = f"testssl.sh --quiet -S -p --openssl=/usr/bin/openssl -oj {tmpfile_name} {host}:{port}"
    args = shlex.split(testssl_cmd)
    testssl_result = subprocess.run(args, stdout=dev_null, stderr=dev_null)
    if not testssl_result.returncode:
        with open(tmpfile_name, 'r') as tmpfile:
            data = json.load(tmpfile)
            tmpfile.close()
        os.remove(tmpfile_name)
        return data

# Method: get_protocol_status
# given JSON returned from running testssl(), return a judgement
# (as a string) on the state of the TLS protocol support
# Fail means browsers won't talk to you as of April 2020.
# Warn means you support SSL/TLS protocols that you shouldn't
# OK means your TLS protocol support is good for 2020
def get_protocol_status(json_data):
    ids_i_care_about = [ 'SSLv2', 'SSLv3', 'TLS1', 'TLS1_1', 'TLS1_2', 'TLS1_3' ]
    modern = False
    old_protos = False
    status = 'Unknown'
    for entry in json_data:
        if entry['id'] in ids_i_care_about:
            this_id = entry['id']
            this_severity = entry['severity']
            this_finding = entry['finding']
            if (this_id != 'TLS1_2' and this_id != 'TLS1_3') and this_severity != 'OK':
                old_protos = True
            elif this_severity == 'OK':
                modern = True
    if old_protos and not modern:
        status = 'Fail'
    elif old_protos and modern:
        status = 'Warn'
    elif not old_protos and modern:
        status = 'Ok'
    return status

# Method: get_issuer
# given JSON returned from running testssl(),
# return the certificate issuer as a string
def get_issuer(json_data):
    ids_i_care_about = [ 'cert_caIssuers' ]
    for entry in json_data:
        if entry['id'] in ids_i_care_about:
            return entry['finding']
