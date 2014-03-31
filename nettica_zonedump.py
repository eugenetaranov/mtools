#!/usr/bin/env python

"""
Usage: zonedump.py <domain>
Dumps SOA, NS, A, MX, TXT records for the specified zone into file in nsupdate format
"""
netticauser = ''
netticapasswd = ''
netticaurl = 'https://www.nettica.com/DNS/DnsApi.asmx?WSDL'
server = '127.0.0.1'
zonestorage = ''


import base64
import sys
from suds.client import Client
from os import remove


def main(zone, netticauser, netticapasswd, netticaurl):
    """ Main function """
    netticapasswd = base64.b64encode(netticapasswd)
    nettica = Client(netticaurl)
    res = nettica.service.ListDomain(netticauser, netticapasswd, zone)
    if res[0]['Status'] != 200:
        print res[0]['Description']
        sys.exit(1)
    try:
        with open('%s/%s.txt' % (zonestorage, zone), 'w+') as f:
            f.write('server %s\n' % server)
            f.write('zone %s\n' % zone)
            for rec in res[2][0]:
                if rec['HostName'] == None:
                    if rec['Priority'] == 0:
                        f.write('update add %s %s %s %s\n' % (rec['DomainName'], rec['TTL'], rec['RecordType'], rec['Data']))
                    else:
                        f.write('update add %s %s %s %s %s\n' % (rec['DomainName'], rec['TTL'], rec['RecordType'], rec['Priority'], rec['Data']))
                else:
                    f.write('update add %s.%s %s %s %s\n' % (rec['HostName'], rec['DomainName'], rec['TTL'], rec['RecordType'], rec['Data']))
            f.write('send\n')
    except IndexError:
        remove('%s/%s.txt' % (zonestorage, zone))
        print 'No records found'
        sys.exit(1)
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: %s <domain name>" % __file__
        sys.exit(1)
    else:
        zone = sys.argv[1]
        main(zone, netticauser, netticapasswd, netticaurl)
