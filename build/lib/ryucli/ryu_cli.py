#!/usr/bin/env python

'''
Usage:
ryu-cli [<url> <user> <password>]
'''

from ryu_models.instance import RYUInstance
from ryu_models.QoS import RYUQoS 
from ryu_models.node import RYUNode, RYUTable
from ryu_models.flow import RYUFlow


from docopt import docopt
import re
import cmd
import json
import shlex
import pprint
import socket
import requests
from ryucli.util import Util, col

class ConfigurationError(Exception):
    def __init__(self, num, key, dir_list):
        self.num = num
        self.key = key
        self.dir = "/" + "/".join(dir_list)

    def __str__(self):
        return "No such path through config at pos: %d %s in %s" %\
            (self.num, self.key, self.dir)

class RYUCmd(cmd.Cmd):
    def __init__(self, url, user, pw):
        self.prompt = col.PROMPT + "ryu-cli> " + col.ENDC
        self.config = {}
        self.cwc = self.config
        self.cwd_list = []
        self.ryu = RYUInstance(url, (user, pw)) 
        self.util = Util()
        self.node = None
        self.table = None
        self.url = url
        self.pp = pprint.PrettyPrinter(indent=1, width=80, depth=None, stream=None)
        cmd.Cmd.__init__(self)

    def emptyline(self):
        pass

    def do_get_flows(self, key):
        ''' Gets the flows for a given dpid. Usage: get_flows <dpid>'''
        try:        
            flows = self.ryu.get("/stats/flow/" + key)
            self.pp.pprint(flows)
        except:
            print("Error grabbing flow entries. Please ensure the dpid is correct")
        return

    def do_qos_set_ovsdb(self, params):
        params = params.split(" ")
        switch_key = params[0]
        addr = "10.0.3.42:6650"
        
        qos = RYUQoS(self.ryu)
        res = qos.set_ovsdb_address(switch_key, addr)
        
        return

    def do_get_qos_nodes(self, params):
        qos = RYUQoS(self.ryu)
        res = qos.get_qos_nodes()
        return

    def do_qos_stats(self, key):
        try:
            endpoint = "/v1.0/conf/switches/" + key + "/ovsdb_addr"
            print("attempting to get " + endpoint)
            qos_stats = self.ryu.get(endpoint)
            self.pp.pprint(qos_stats)
        except:
            print("Could not grab qos stats")
        return

    def do_cd(self, path):
        '''Change the current level of view of the config to be at <key>
        cd <key>'''
        if path=="" or path[0]=="/":
            new_wd_list = path[1:].split("/")
        else:
            new_wd_list = self.cwd_list + path.split("/")
        try:
            print("new_wd_list: ", new_wd_list)
            cwc, new_wd_list = self._conf_for_list(new_wd_list)
        except ConfigurationError as e:
            print (col.FAIL + str(e) + col.ENDC)
            return
        self.cwd_list = new_wd_list
        self.cwc = cwc

    def complete_cd(self, text, l, b, e):
        return [ x[b-3:] for x,y in self.cwc.iteritems() if x.startswith(l[3:])]

    def do_ls(self, key):
        '''Show the top level of the current working config, or top level of config under [key]
        ls [key]'''
        conf = self.cwc
        if key:
            try:
                conf = conf[key]
            except KeyError:
                print ("No such key %s" % key)
                return

        try:
            for k,v in conf.iteritems():
                if isinstance(v, RYUNode):
                    try:
                        hostname = socket.gethostbyaddr(v.ip_address)[0]
                    except:
                        hostname = v.ip_address
                    print (col.DIR + k + col.ENDC + ": (\"%s\", \"%s\", \"%s\")" % \
                        (v.description, v.hardware, v.manufacturer))
                elif isinstance(v, dict) or isinstance(v, list):
                    print (col.DIR + k + col.ENDC)
                else:
                    print ("%s: %s" % (k, v))
        except:
            print ("%s" % conf)

    def complete_ls(self, text, l, b, e):
        return [ x[b-3:] for x,y in self.cwc.iteritems() if x.startswith(l[3:]) ]

    def do_lsd(self, key):
        '''Show all config from current level down... or all config under [key]
        lsd [key]'''
        conf = self.cwc
        if key:
            try:
                conf = conf[key]
            except KeyError:
                print ("No such key %s" % key)
        self.pp.pprint(conf)

    def complete_lsd(self, text, l, b, e):
        return [ x for x,y in self.cwc.iteritems()
                 if isinstance(y, dict) and x.startswith(text) ]

    def do_pwd(self, key):
        '''Show current path in config separated by slashes
        pwd'''
        print ("/" + "/".join(self.cwd_list))

    def do_get_nodes(self, args):
        '''Get all or a specific node from Ryu OFCTL
        get_nodes [node]'''
        try:
            self.ryu.update()
            nodes = self.ryu.get_nodes()
            self.config = nodes
            self._set_cwc()
        except Exception as e:
            print ("Error: %s" % e)
            import traceback
            traceback.print_exc()
    def do_get_unis_nodes(self, args):
        from unis.runtime import Runtime

        try:
            rt = Runtime()
            print(rt.nodes)
        except Exception as e:
            print ("Error: %s" % e)
            import traceback
            traceback.print_exc()

    def do_del_flow(self, fid):
        try:
            if not self.cwd_list[-3] == "tables":
                raise
        except:
            print (col.FAIL + "Not in a valid table leaf!" + col.ENDC)
            return

        if not fid:
            print (col.FAIL + "Must specify flow id or '*'" + col.ENDC)
            return

        table = self.cwd_list[-2]
        if fid == "*":
            yn = self.util.query_yes_no("Delete ALL flows in table %s" % (table))
            if yn:
                try:
                    self.tables[int(table)].delete_flows()
                    self.tables[int(table)].update()
                except Exception as e:
                    print ("Error deleting flows from table: %s" % e)
                    return
            else:
                return
        else:
            yn = self.util.query_yes_no("Delete flow %s in table %s" % (fid, table))
            if yn:
                try:
                    flow = self.tables[int(table)].get_flows_by_id(fid)
                    flow.delete()
                    self.tables[int(table)].update()
                except Exception as e:
                    print ("Error deleting flow: %s" % e)
                    return
            else:
                return

    def complete_del_flow(self, text, l, b, e):
        return [ x[b-9:] for x,y in self.cwc.iteritems() if x.startswith(l[9:]) ]
            
    def do_add_flow(self, args):
        '''Add a flow, will prompt for user input'''
        if not self.node:
            print (col.FAIL + "No node selected!" + col.ENDC)
            return

        file_path = self.util.get_string("Input file: ", None)
        if not file_path:
            print ("You must include a json file containing the flow(s)")
            return
        
        try:
            with open(file_path, 'r') as in_file:
                raw_json = in_file.read()
                
            flow_requests = json.loads(raw_json)
        except IOError as e:
            print ("Could not open file %s" % file_path)
            return
        except ValueError as e:
            print ("Invalid json formatting in request")
            return

        if isinstance(flow_requests, list):
            for request in flow_requests:
                try:
                    flow = request["flow"]
                    flow_id  = flow["id"]
                    table_id = flow["table_id"]
                    self.tables[table_id].put_flow_from_data_json(json.dumps({"flow": flow}), flow_id)
                except ValueError as e:
                    print ("Flow request did not contain flow or table id")
                    return
                except Exception as e:
                    print ("Error pushing flow: %s" % e)
        else:
            request = flow_requests
            try:
                flow = request["flow"]
                flow_id  = flow["id"]
                table_id = flow["table_id"]
                self.tables[table_id].put_flow_from_data_json(json.dumps({"flow": flow}), flow_id)
            except ValueError as e:
                print ("Flow request did not contain flow or table id")
                return
            except Exception as e:
                print ("Error pushing flow: %s" % e)

        self.do_update(None)
        self.do_get_nodes(None)

    def do_update(self, args):
        # TODO: track current object to perform selective update
        pass
        
    def do_EOF(self, line):
        return True

    def _set_cwc(self):
        '''Set the current working configuration to what it should be
        based on the cwd_list. If the path doesn't exist, set cwc to
        the top level and clear the cwd_list.
        '''
        try:
            self.cwc, self.cwd_list = self._conf_for_list()
            print ("OK")
            #self.pp.pprint(self.cwc)
        except ConfigurationError:
            self.cwc = self.config
            self.cwd_list = []

    def _conf_for_list(self, cwd_list=None):
        '''Takes in a list representing a path through the config
        returns a tuple containing the current working config, and the
        "collapsed" final path (meaning it has no .. entries.
        '''
        if not cwd_list:
            cwd_list = self.cwd_list
        cwc_stack = []
        cwc = self._ryu_to_dict(self.config, None)
        num = 0
        for kdir in cwd_list:
            if kdir == "":
                continue
            num += 1
            if kdir == ".." and cwc_stack:
                cwc = cwc_stack.pop()[0]
                continue
            elif kdir == "..":
                continue
            try:
                ocwc = cwc
                cwc = self._ryu_to_dict(cwc[kdir], kdir)
                cwc_stack.append((ocwc, kdir))
            except KeyError:
                import traceback
                traceback.print_exc()
                raise ConfigurationError(num, kdir, cwd_list)
        return (cwc, [ x[1] for x in cwc_stack ])

    def _ryu_to_dict(self, cfg, k):
        print(cfg, k)
        
        if k and hasattr(cfg, "to_dict"):
            if isinstance(cfg, RYUNode):
                self.node = cfg
                self.ports = cfg.get_ports()
                self.tables = cfg.get_tables()
            print(cfg)
            cfg = cfg.to_dict()

        if isinstance(cfg, list):
            new = {}
            for d in cfg:
                if "id" in d:
                    new[str(d['id'])] = d
                else:
                    for k, v in d.items():
                        new[str(k)] = v
            cfg = new
        return cfg

def main(args=None):
    args = docopt(__doc__, version='ryu-cli 0.1')
    url = args.get("<url>")
    if not url:
        url = "http://localhost:8080"

    user = args.get("<user>")
    if not user:
        user = "admin"

    pw = args.get("<password>")
    if not pw:
        pw = "admin"

    info =\
"""Server: %s
User  : %s
Passwd: %s\n""" % (url, user, "*****" if pw != "admin" else pw)
    print (info)
    
    ryuc = RYUCmd(url, user, pw)
    ryuc.cmdloop()

if __name__ == '__main__':
    main()
