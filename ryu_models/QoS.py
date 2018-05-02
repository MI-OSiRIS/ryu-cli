from ryu_models.instance import *
from ryu_models.instance import RYUInstance
from ryu_models.node import *
from ryu_models.table import *
from ryu_models.port import *
from ryu_models.flow import *
from ryu_models.exceptions import *
from ryu_models.queue import *
from ryu_models.meter import *
from ryu_models.rule import *
import json
import pprint

class RYUQoS():

    def __init__(self, instance):
        
        self.ryu_instance = instance
        self.ovsdb_address = "" 
        self.queues = {}
        self.meters = {}
        self.rules  = {}

        return  
    
    # Make a PUT request to ensure the switch is pointed to our ovsdb instance
    # Ex)  curl -X PUT -d '"tcp:127.0.0.1:6632"' http://localhost:8080/v1.0/conf/switches/0000000000000001/ovsdb_addr
    def set_ovsdb_address(self, switch_key, addr):

        endpoint = "/v1.0/conf/switches/" + switch_key + "/ovsdb_addr"
        
        try:

            res_set = self.ryu_instance.put(endpoint, "tcp:" + addr) 
            res_test = self.ryu_instance.get(endpoint)

            pprint.pprint("OVSDB Address for switch " + switch_key + " set to - " + res_test)

            self.ovsdb_address = res_test
        
        except Exception as e:

            print("Could not set ovsdb address to tcp:" + self.ovsdb_address, e)

        return

    def get_ovsdb_address(self, switch_key):
        endpoint = "/v1.0/conf/switches/" + switch_key + "/ovsdb_addr"
        try:

            response = self.ryu_instance.get(endpoint)
            print("ovsdb response:")
            pprint.pprint(response)
            
            return response

        except:

            print("Could not get ovsdb address from switchL: ", e)

        return

    def get_qos_nodes(self):

        endpoint = "/v1.0/conf/switches"
 
        try:

            response = self.ryu_instance.get(endpoint)
            print("OVS reply: ")
            
            if len(response) == 0:
                pprint.pprint("No QoS switches in OVSDB, be sure to set the address")

            pprint.pprint(response)
        except Exception as e:
            
            print("Could not fetch OVS nodes: ", e)

        return response 

    def qos_queue_stats(self, *argv):
        
        params = argv[0]
         
        # if no args given do queue all
        if len(params) == 1 and params[0]=='':
            try:
                endpoint = "/qos/queue/status/all"
                response = self.ryu_instance.get(endpoint)
                pprint.pprint(response)
            except Exception as e:
                print("Unable to fetch Queues: ", e)
                return
        elif len(params) > 1:

            print("Too many arguments given. Max node argument is 1")

        else:
            switch_id = params[0]
            try:
                endpoint = "/qos/queue/status/" + switch_id
                response = self.ryu_instance.get(endpoint)
                print("Queues for switch " + switch_id)
                pprint.pprint(response)

            except Exception as e:
                print("Unable to fetch qos queue's for switch")

        return

    def add_queue(self, switch_id):
        
        if switch_id == '':
            print("No switch_id given. Cannot create queue")
            return

        queue = RYUQueue(switch_id)
        queue_str = queue.user_build()
        
        endpoint = "/qos/queue/" + switch_id

        try:
            
            response = self.ryu_instance.post(endpoint, queue_str)
            print("OVS Response: ")
            pprint.pprint(response)
            print("Status - ", response[0]['command_result']['result'])
            
            # add to self's list of queue, self updates bc it will overwrite the dict entry
            self.queues[response[0]['switch_id']] = queue

        except Exception as e:
            
            print("Unable to add queue to switch: ", e)

        return

    def add_meter(self, switch_id):

        if switch_id == '':
            print("No switch_id given.")
            return

        meter = RYUMeter(switch_id)
        meter_str = meter.user_build()
        
        endpoint = "/qos/meter/" + switch_id

        try:

            response = self.ryu_instance.post(endpoint, meter_str)
            print("OVS Response: ")
            pprint.pprint(response)
            print("Status - ", response[0]['command_result'][0]['result'])

        except Exception as e:

            print("Unable to add meter entry: ", e)

        return

    def add_rule(self, switch_id):

        if switch_id == '':
            print("No switch_id given.")
            return

        rule = RYURule(switch_id)
        rule_str = rule.user_build()

        endpoint = "/qos/rules/"  + switch_id

        try:

            response = self.ryu_instance.post(endpoint, rule_str)
            print("OVS Response: ")
            pprint.pprint(response)

        except Exception as e:

            print("Unable to set rule: ", e)

        return
        
