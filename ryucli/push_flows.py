#!/usr/bin/env python

'''
Usage:
push_flows [<flow_file> <url> <user> <password>]
'''

from odl.instance import ODLInstance
from odl.topology import ODLTopology
from odl.node import ODLNode
from docopt import docopt
import json

if __name__ == '__main__':
    args = docopt(__doc__, version='odl-client 0.1')
    url = args.get("<url>")
    if not url:
        url = "http://localhost:8181"
        
    user = args.get("<user>")
    if not user:
        user = "admin"

    pw = args.get("<password>")
    if not pw:
        pw = "admin"

    ffile = args.get("<flow_file>")
        
    info =\
"""File  : %s
Server: %s
User  : %s
Passwd: %s\n""" % (ffile, url, user, "*****" if pw != "admin" else pw)
    print info
    
    try:
        f = open(ffile, 'r')
        fstr = f.read()
        flows = json.loads(fstr)
    except Exception, e:
        print "Error: %s" % e
        
    odl = ODLInstance(url, (user, pw))
    nodes = odl.get_nodes()
    for flow in flows:
        sw = flow['switch']
        tid = flow['flow']['table_id']
        tables = nodes[sw].get_tables()
        tables[tid].put_flow_from_data_json(json.dumps({"flow": flow['flow']}), flow['id'])
    f.close()
    
