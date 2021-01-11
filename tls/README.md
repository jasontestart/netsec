# TLS/SSL assessments

These tools were written as different ways to assess the TLS protocol
support for services on the network. I have three ways here:

 1. Using [Shodan](https://shodan.io) (only works for Internet-exposed hosts)
 2. Using [nmap](https://nmap.org)
 3. Using the [testssl.sh](https://testssl.sh) script

I needed to prioritize remediation efforts on a network with several hundred
web servers with very distributed management. Shodan is great for Internet-
facing hosts, and I prefer nmap for local scanning.
