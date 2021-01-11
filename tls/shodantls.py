#!/usr/bin/python3
import shodan
import my_shodan_api_key

# Return Fail if there's no support for TLSv1.2 or greater
# Return Warn if there's support for TLSv < 1.2 and >= 1.2
# Return Pass if there's support for only TLSv1.2 or greater
def tls_status(protos):
    proto_list = protos.copy()
    if proto_list == None:
        return 'Unknown'
    # If a modern protocol is not supported, then we're done!
    if '-TLSv1.2' in proto_list and '-TLSv1.3' in proto_list:
        return 'Fail'
    for p in ['TLSv1.2', 'TLSv1.3', '-TLSv1.2', '-TLSv1.3']:
        if p in proto_list:
            proto_list.remove(p)
    # Either 'Pass' or 'Warn', no other protocols supported to 'Pass'.
    for p in proto_list:
        if p[0] != '-':
            return 'Warn'
    return 'Pass'

def get_info(host,port):
    api = shodan.Shodan(my_shodan_api_key.KEY)
    # Wrap the request in a try/ except block to catch errors
    try:
        result = api.host(host)
        status = 'Unknown'
        issuer = 'Unknown'
        ip = result['ip_str']
        hostnames = ''
        for data in result['data']:
            if data['port'] == port:
                if 'ssl' in data:
                    protos = data['ssl']['versions']
                    status = tls_status(protos)
                    if 'cn' in data['ssl']['cert']['issuer']:
                        issuer = data['ssl']['cert']['issuer']['cn']
                    elif 'CN' in data['ssl']['cert']['issuer']:
                        issuer = data['ssl']['cert']['issuer']['CN']
                    for host in data['hostnames']:
                        hostnames += f'{host} '
        if hostnames == '':
            for host in result['hostnames']:
                hostnames += f'{host} '
        return { 'ip' : ip, 'hostnames' : hostnames[:-1], 'status': status, 'issuer': issuer}
    except shodan.APIError as e:
            print('Error: {}'.format(e))

