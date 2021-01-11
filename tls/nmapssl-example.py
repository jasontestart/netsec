#!/usr/bin/python3
from nmapssl import tls_status

result = tls_status('129.97.208.23',443)
print(result)
