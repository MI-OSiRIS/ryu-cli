#!/usr/bin/env python

'''
Usage:
push_flows [<flow_file> <url> <user> <password>]
'''

from ryu_models.instance import RYUInstance
from ryu_models.node import RYUNode
from docopt import docopt
import json

if __name__ == '__main__':
    args = docopt(__doc__, version='ryu-client 0.1')
    url = args.get("<url>")
    if not url:
        url = "http://localhost:8080"
        
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
    
    assert ffile is not None, "Must specify input file"

    try:
        f = open(ffile, 'r')
        fstr = f.read()
        flows = json.loads(fstr)
    except Exception, e:
        print "Error: %s" % e
        exit(1)

    ryu = RYUInstance(url, (user, pw))
    nodes = ryu.get_nodes()
    for flow in flows:
        sw = flow['switch']
        tid = flow['flow']['table_id']
        tables = nodes[sw].get_tables()
        tables[tid].put_flow_from_data_json(json.dumps({"flow": flow['flow']}), flow['id'])
    f.close()
    
