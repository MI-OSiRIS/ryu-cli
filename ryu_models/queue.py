
from ryu_models.instance import *
from ryu_models.instance import RYUInstance
from ryu_models.QoS import *
from ryu_models.node import *
from ryu_models.table import *
from ryu_models.port import *
from ryu_models.flow import *
from ryu_models.exceptions import *
import json
import pprint
import cmd

class RYUQueue(object):
    
    def __init__(self, switch_id):
        
        self.switch_id = switch_id
        
        return

    def to_dict(self):

        q = {}
        q['port_name']  = self.port_name
        q['type']       = self.type
        q['max_rate']   = self.max_rate
        q['queues']     = self.queues
        q['switch_id']  = self.switch_id

        return q
    
    def user_build(self):
        
        print("Building new Queue")
        self.switch_id  = input("Switch ID: ")
        self.port_name  = input("Port Name: ")
        self.type       = input("Type <linux-htb or linux-other>: ")
        self.max_rate   = input("Max Rate <int>: ")
        self.queues     = []
        done = False

        if self.type != "linux-htb" and self.type != "linux-other":
            self.type = "linux-htb" 
        
        print('\n')

        while(done == False):

            cont = input("Add Queue?(y/n): ") 

            if cont == 'y':
                
                minmax = input("Min or Max?(min_rate/max_rate): ")

                if minmax != "min_rate" and minmax != "max_rate":
                    print("Incorrect input, must be exactly min_rate or max_rate.. restarting Queue form.")
                    continue

                value = input("Enter Value <int>: ")
                
                q = {}
                q[minmax] = value
                self.queues.append(q)
                
                print("Queue Added\n")

            elif cont == 'n':

                print("Done building queue")
                done = True
                break

        build_str = json.dumps(self.to_dict())

        return build_str



                

        
