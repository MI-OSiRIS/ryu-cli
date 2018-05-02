
from ryu_models.instance import *
from ryu_models.instance import RYUInstance
from ryu_models.node import *
from ryu_models.table import *
from ryu_models.port import *
from ryu_models.flow import *
from ryu_models.exceptions import *
from ryu_models.queue import *
import json
import pprint
from cmd import *

class RYUMeter():

    def __init__(self, switch_id):
        
        self.switch_id = switch_id
        self.bands = []
        self.self_dict = {}
        
        return

    def user_build(self):
        
        print(" - Build Meter - ")
        self.meter_id       = input("Meter id<int>: ")
        
        cont = False

        while cont == False:
        
            new_b = input("\nAdd a band?(y/n): ")

            if new_b == 'y':

                band = {}
       
                band['action']      = input(" - Action <DROP or DSCP_REMARK>: ")
                band['flag']        = input(" - Flag <KBPS or PKTPS or BURST or STATS>: ")
                band['burst_size']  = input(" - Burst Size <int>: ")
                band['rate']        = input(" - Rate <int>: ")
                band['prec_level']  = input(" - Prec Level <int>: ") 

                if self.validate_band(band):
                    self.bands.append(band)

            elif new_b == 'n':
                cont = True
        

        self.self_dict = self.to_dict()
        build_str = json.dumps(self.self_dict)

        return build_str

    def validate_band(self, b):

        if b['action'] != "DROP" and b['action'] != "DSCP_REMARK":
            print("Action field must be either DROP or DSCP_REMARK")
            return False

        if b['flag'] != "KBPS" and b['flag'] != 'PKTPS' and b['flag'] != "BURST" and b['flag'] != "STATS":
            print("Flag must be one of KBPS, PKTPS, BURST, or STATS")
            return False
        if isinstance(b['burst_size'], int) and isinstance(b['rate'], int) and isinstance(b['prec_level'], int):
            print("Burst Size, Rate, and Prec Level must be integers.")
            return False

        return True

    def to_dict(self):
        m = {}

        m['meter_id'] = self.meter_id
        m['bands'] = self.bands

        return m

