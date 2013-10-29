#!/usr/bin/env python

import subprocess
from os import remove, mkdir
from argparse import ArgumentParser
from tempfile import NamedTemporaryFile

DEFDOMAIN = 'domain.com'
NETWORKS = {
'int01': {'gw': '0.0.0.0', 'ns': '8.8.8.8', 'netmask': '255.255.255.0' },
'int02': {'gw': '10.8.0.1', 'ns': '8.8.8.8', 'netmask': '255.255.255.0' },
'dmz01': {'gw': '10.8.0.1', 'ns': '8.8.8.8', 'netmask': '255.255.255.0' },
'dmz02': {'gw': '10.8.0.1', 'ns': '8.8.8.8', 'netmask': '255.255.255.0' },
'cmn': {'gw': '10.8.4.1', 'ns': '8.8.8.8', 'netmask': '255.255.252.0' },
}
STORAGEPATH = '/vms'
DEBUG = True

def parseargs():
    p = ArgumentParser()
    p.add_argument('-n', '--name', required = True)
    p.add_argument('-r', '--ram', type = int, default = 1024)
    p.add_argument('-c', '--cpus', type = int, default = 1)
    p.add_argument('--ip', required = True)
    p.add_argument('--network', required = True, choices = NETWORKS.keys() )
    p.add_argument('--domain', default = DEFDOMAIN)
    p.add_argument('--size', type = int, default = 10)
    p.add_argument('--puppetmaster')
    p.add_argument('--kstemplate', required = True)
    p.add_argument('--url', required = True)
    return vars(p.parse_args())

def ksparser(line):
    """ Replace variables in kickstart """
    line = line.replace('%IPADDR%', params['ip'])
    line = line.replace('%HOSTNAME%', params['name'])
    line = line.replace('%DOMAIN%', params['domain'])
    line = line.replace('%URL%', params['url'])
    line = line.replace('%GATEWAY%', NETWORKS[params['network']]['gw'])
    line = line.replace('%NAMESERVER%', NETWORKS[params['network']]['ns'])
    line = line.replace('%NETMASK%', NETWORKS[params['network']]['netmask'])
    return line

def ksgenerator():
    """ Create temporary KS file """
    with open(params['kstemplate'], 'r') as kst:
        with NamedTemporaryFile(delete = False) as ks:
            for line in kst.readlines():
                ks.write(ksparser(line))
            return ks.name

def allocatedisk():
    """ Allocate vm disk """
    try:
        mkdir('%(path)s/%(name)s' % {'path': STORAGEPATH, 'name': params['name']})
    except OSError:
        pass
    print STORAGEPATH, params['name']
    diskpath = '%(path)s/%(name)s/%(name)s.img' % {'path': STORAGEPATH, 'name': params['name']}
    args = 'fallocate -l %(size)s %(diskpath)s' % {'size': params['size']*1024, 'diskpath': diskpath}
    try:
        subprocess.call(args, shell = True)
    except:
        pass
    return diskpath

def doinstall(ksfile, diskpath):
    """ Run vm-install """
    args = 'virt-install --force --connect qemu:///system --cpu host -n %s -r %s --vcpus=%s --disk path=%s,bus=virtio,sparse=false -w network=%s --nographics --location=%s --noautoconsole --initrd-inject=%s --extra-args="ks=file:%s console=ttyS0,115200"' % (params['name'], params['ram'], params['cpus'], diskpath, params['network'], params['url'], ksfile, ksfile.split('/')[-1])
    if DEBUG: print 'Calling %s' % args
    try:
        subprocess.call(args, shell = True)
    except:
        pass

def main():
    if DEBUG: print "Args: %s" % params
    ksfile = ksgenerator()
    if DEBUG: print "Kickstart file: %s" % ksfile
    diskpath = allocatedisk()
    if DEBUG: print 'Created disk on %s' % diskpath
    doinstall(ksfile, diskpath)
    if not DEBUG: remove(ksfile)

if __name__ == '__main__':
    params = parseargs()
    main()
