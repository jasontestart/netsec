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
NMAP_PATH='/usr/local/bin/nmap'

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

# Return a list of TLS protocols support by host at port
def get_protocols(host,port):
    options = f'--script ssl-enum-ciphers -p {port} {host}'
    xmldict = scan(options)
    port_result = xmldict['nmaprun']['host']['ports']['port']
    if not 'script' in port_result.keys():
        return None
    proto_result = xmldict['nmaprun']['host']['ports']['port']['script']['table']
    protos = []
    if isinstance(proto_result, list):
        for proto in proto_result:
            protos.append(proto['@key'])
    else:
        protos.append(proto_result['@key'])
    return protos

# Return Fail if there's no support for TLSv1.2 or greater
# Return Warn if there's support for TLSv < 1.2 and >= 1.2
# Return Pass if there's support for only TLSv1.2 or greater
def tls_status(host,port):
    protos = get_protocols(host,port)
    if not protos:
        return 'Unknown'
    result = 'Fail'
    for p in ['TLSv1.2', 'TLSv1.3']:
        if p in protos:
            result = 'Warn'
            protos.remove(p)
    if not protos and result == 'Warn':
        return 'Pass'
    else:
        return result


# Return a dictionary containing org name and common name of the
# issuer of the certificate at the provded host and port.
def get_cert_issuer(host,port):
    options = f'-sV --script ssl-cert -p {port} {host}'
    xmldict = scan(options)
    result = xmldict['nmaprun']['host']['ports']['port']
    if not 'script' in result.keys():
        return None
    result = xmldict['nmaprun']['host']['ports']['port']['script']
    issuer = { 'organizationName' : 'Unknown', 'commonName' : 'Unknown' }
    if isinstance(result,list):
        for level1 in result:
            if level1['@id'] == 'ssl-cert':
                level2 = level1['table']
    else:
        level2 = result['table']
    for entry in level2:
        if entry['@key'] == 'issuer':
            if isinstance(entry['elem'],list):
                for v in entry['elem']:
                    if v['@key'] in issuer.keys():
                        issuer[v['@key']] = v['#text']
            else:
                issuer[entry['elem']['@key']] = entry['elem']['#text']
    return issuer
