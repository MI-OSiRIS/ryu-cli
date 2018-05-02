from ryu_models.instance import *
from ryu_models.instance import RYUInstance
from ryu_models.node import *
from ryu_models.table import *
from ryu_models.port import *
from ryu_models.flow import *
from ryu_models.exceptions import *
from ryu_models.queue import *
from ryu_models.meter import *
import json
import pprint

class RYURule():

    def __init__(self, switch_id):
        
        self.switch_id = switch_id
        self.self_dict = {}
        self.match_fields = {}
        self.action_fields = {}
        self.match_names = ["in_port", "dl_src", "dl_dst", "dl_type", "nw_src", "nw_dst", "ipv6_src", "ipv6_dst", "nw_proto", "tp_src", "tp_dst", "ip_dscp"]
        return 

    def user_build(self):

        print("\n - Build Rule - \n")
        
        print("Available match fields -\n" +  
                " - in_port : <int>\n" +
                " - dl_src  : <xx:xx:xx:xx:xx:xx>\n" +
                " - dl_dst  : <xx:xx:xx:xx:xx:xx>\n" +
                " - dl_type : <ARP or IPv4 or IPv6>\n" +
                " - nw_src  : <A.B.C.D/M>\n" +
                " - nw_dst  : <A.B.C.D/M>\n" +
                " - ipv6_src: <xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx/m>\n" +
                " - ipv6_dst: <xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx/m>\n" +
                " - nw_proto: <TCP or UDP or ICMP or ICMPv6>\n" +
                " - tp_src  : <int>\n" +
                " - tp_dst  : <int>\n" +
                " - ip_dscp  : <int>\n")

        self.priority = input("Priority  <int '0 to 65533'>: ")
        
        cont = True
        while cont == True:

            new_state = input("\nAdd a match field?(y/n): ")

            if new_state == 'y':
                
                f_name      = input(" - Field Name: ")
                f_value     = input(" - Field Value: ")

                if f_name not in self.match_names:
                    print("Not a valid match field.. skipping.")
                    continue

                self.match_fields[f_name] = f_value

            elif new_state == 'n':

                cont = False
                break
              
        cont = True
        

        new_state = input("\nAdd an action field?(y/n): ")

        if new_state == 'y':

            # Begin lazy switch statement
            sub_state = input("\nAdd Meter id?(y/n): ")
            if sub_state == 'y':
                self.action_fields['meter_id'] = input("Meter id<int>: ")

            sub_state = input("\nAdd DSCP Mark?(y/n): ")
            if sub_state == 'y':
                self.action_fields['mark'] = input("Mark <int>: ")

            sub_state = input("\nAdd Queue?(y/n): ")
            if sub_state == 'y':
                self.action_fields['queue'] = input("Queue id<int>: ")
        
        elif new_state != 'n':
            print("Unrecognized input. Please us y or n. Skipping action fields.")

        self.self_dict = self.to_dict()
        build_str = json.dumps(self.self_dict)

        return build_str


    def to_dict(self):

        r = {}
        r['priority']   = self.priority
        r['actions']    = self.action_fields
        r['match']      = self.match_fields

        return r


