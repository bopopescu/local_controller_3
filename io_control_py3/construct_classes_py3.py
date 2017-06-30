# File: construct_classes.py
#
#
#
#
#

from  .psoc_4m_devices_py3 import PSOC_4M_MOISTURE_UNIT
from  .click_controller_class_py3 import Click_Controller_Base_Class_44
from  .click_controller_class_py3 import Click_Controller_Base_Class_22
from  .io_controller_py3 import IO_Controller
from  .new_instrument_py3 import Modbus_Instrument


class Construct_Access_Classes(object):

   def __init__( self , ip, port):
       # find ip and port for ip server
       instrument  =  Modbus_Instrument()
       instrument.set_ip(ip, int(port) )     

       self.access_classes = {}
       self.type_classes   = {}
       self.type_classes["PSOC_4_Moisture"] = PSOC_4M_MOISTURE_UNIT( instrument )
       self.type_classes["click_44"]        = Click_Controller_Base_Class_44( instrument )
       self.type_classes["click_22"]        = Click_Controller_Base_Class_22( instrument )
       self.type_classes["io_controller"]   = IO_Controller( instrument )
   
   def find_class( self, type ):
       return self.type_classes[type]  

             
if __name__ == "__main__":
   
   access_class = Construct_Access_Classes( "192.168.1.84" , 3400 ) ### dummy values
   print (access_class.find_class("PSOC_4_Moisture"))
