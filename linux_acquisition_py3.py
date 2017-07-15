# 
#
# File: utilities.py
#
#
#
#


import datetime
import time
import string
import math
import redis
import base64
import json
from py_cf_py3.chain_flow import CF_Base_Interpreter

import os
import copy
import load_files_py3
import rabbit_cloud_status_publish_py3
from   io_control_py3 import io_controller_py3
from   io_control_py3 import construct_classes_py3
from   io_control_py3 import new_instrument_py3

#
#
# File: linux_acquisition.py
# Monitors status of raspberry pi
#
#

from data_acquisition_py3 import data_scheduling_py3
from data_acquisition_py3.data_scheduling_py3 import Data_Acquisition
from data_acquisition_py3.data_scheduling_py3 import add_chains
from data_acquisition_py3.data_scheduling_py3 import construct_class

import os
## os.system("sar -u 10 1 > sar_output.txt")
class PI_Status( object ):

   def __init__( self, redis_handle ):
       self.redis_handle = redis_handle

   def measure_temperature( self, tag, value, parameters ):
      temp = os.popen("vcgencmd measure_temp").readline()
      temp = temp.replace("temp=","").replace("'C\n","")
      temp = float(temp)
      temp = (9.0/5.0*temp)+32.

      return temp


   def measure_disk_space( self, tag, value, parameters  ):
       f = os.popen("df")
       data = f.read()
       f.close()
       lines = data.split("\n")
       
       return_value = []
       for i in range(0,len(lines)):
           if i == 0:
               continue
           fields = lines[i].split()
          
           if len(fields) > 3:
              percent = float( fields[2] )/float( fields[1] )
              temp_value = { "disk": fields[0], "used":percent }  
              return_value.append( temp_value )
       return return_value

   def measure_processor_ram( self ,tag, value, parameters ):
       f = os.popen("free -m")
       data = f.read()
       f.close()
       lines = data.split("\n")
       return_value = []
       fields = lines[1].split()
       percent = float(fields[2])/float(fields[1])
       temp_value = { "Component": fields[0], "used":percent }
       return_value.append(temp_value )
       fields = lines[3].split()
       percent = float(fields[2])/float(fields[1])
       temp_value = { "Component": fields[0], "used":percent }
       return_value.append(temp_value )
       return return_value

   def measure_processor_load( self ,tag, value, parameters  ):
       headers = [ "USER","PID","%CPU","%MEM","VSZ","RSS","TTY","STAT","START","TIME","COMMAND", "PARAMETER1", "PARAMETER2" ]
       f = os.popen("ps -aux | grep python")
       data = f.read()
       f.close()
       lines = data.split("\n")
       return_value = []
       for i in range(0,len(lines)):

           if i == 0:
               continue
           fields = lines[i].split()
           temp_value = {}
           if len(fields) <= len(headers):
               for i in range(0,len(fields)):
                   temp_value[headers[i]] = fields[i]
               return_value.append( temp_value )

       return return_value

   def log_redis_info( self, tag,value,parameters):
        return self.redis_handle.info()

def construct_linux_acquisition_class( redis_handle, gm, io_server,io_server_port ):
   pi_stat = PI_Status( redis_handle )
   gm.add_cb_handler("pi_temperature",       pi_stat.measure_temperature )  
   gm.add_cb_handler("linux_memory_load",    pi_stat.measure_processor_load )
   gm.add_cb_handler("linux_daily_disk",     pi_stat.measure_disk_space )
   gm.add_cb_handler("linux_daily_redis",    pi_stat.log_redis_info )
   gm.add_cb_handler("linux_daily_memory",   pi_stat.measure_processor_ram)

   instrument = new_instrument_py3.Modbus_Instrument()

   
   remote_classes = construct_classes_py3.Construct_Access_Classes(io_server,io_server_port)
   fifteen_store   =  []
   minute_store    =  []
   hour_store      =  list(gm.match_terminal_relationship(  "LINUX_HOUR_ACQUISTION"))[0]
   daily_store     =  list(gm.match_terminal_relationship("LINUX_DAILY_ACQUISTION" ))[0]
   fifteen_list   =  []
   minute_list     =  []     
   hour_list       =  list(gm.match_terminal_relationship( "LINUX_HOUR_ELEMENT" ))
   daily_list      =  list(gm.match_terminal_relationship( "LINUX_DAILY_ELEMENT" ))

   return  construct_class( redis_handle,
                     gm,instrument,
                     remote_classes,
                     fifteen_store,
                     minute_store,
                     hour_store,
                     daily_store,
                     fifteen_list,
                     minute_list,
                     hour_list,
                     daily_list,
                     status_queue_class ) 
    
if __name__ == "__main__":

   import time
   from redis_graph_py3.farm_template_py3 import Graph_Management 

   def list_filter( input_list):
      if len( input_list ) > 0:
          return input_list[0]
      else:
          return []

   gm =Graph_Management("PI_1","main_remote","LaCima_DataStore")
  
   data_store_nodes = gm.find_data_stores()
   io_server_nodes  = gm.find_io_servers()
  
   # find ip and port for redis data store
   data_server_ip   = data_store_nodes[0]["ip"]
   data_server_port = data_store_nodes[0]["port"]
   redis_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 12 )


   io_server_ip     = io_server_nodes[0]["ip"]
   io_server_port   = io_server_nodes[0]["port"]
   # find ip and port for ip server
   status_server =  gm.match_terminal_relationship("RABBITMQ_STATUS_QUEUE")[0]
   queue_name     = status_server[ "queue"]

   status_queue_class = rabbit_cloud_status_publish_py3.Status_Queue(redis_handle, queue_name ) 
   
   construct_linux_acquisition_class= construct_linux_acquisition_class( redis_handle, gm, io_server_ip, io_server_port )

   

   #
   # Adding chains
   #
   cf = CF_Base_Interpreter()
   cf.define_chain("test",True)
   cf.insert_link( "linkxx","Log",["test chain start"])
   cf.insert_link( "link_0", "SendEvent",  ["MINUTE_TICK",1] )
   cf.insert_link( "link_1", "WaitEvent",  ["TIME_TICK"] )
   cf.insert_link( "link_2", "SendEvent",    [ "HOUR_TICK",1 ] )
   cf.insert_link( "link_3", "WaitEventCount", ["TIME_TICK",2,0])
   cf.insert_link( "link_4", "SendEvent",    [ "DAY_TICK", 1] )


   add_chains(cf, construct_linux_acquisition_class)

   print( "starting chain flow" )

   cf.execute()

