from ryu_models.instance import *
from ryu_models.instance import RYUInstance
from ryu_models.node import *
from ryu_models.table import *
from ryu_models.port import *
from ryu_models.flow import *
from ryu_models.exceptions import *
import json
import pprint

class RYUQoS():

    def __init__(self, instance):
        self.ryu_instance = instance
        self.ovsdb_address = "" 
       
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
                pprint("No QoS switches in OVSDB, be sure to set the address")

            pprint.pprint(response)
        except Exception as e:
            
            print("Could not fetch OVS nodes: ", e)

        return response 

        return
