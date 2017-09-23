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

##cf.insert_link( "link_17",  "One_Step",         [ self.log_clean_filter ] )


from data_acquisition_py3 import data_scheduling_py3
from data_acquisition_py3.data_scheduling_py3 import Data_Acquisition
from data_acquisition_py3.data_scheduling_py3 import add_chains
from data_acquisition_py3.data_scheduling_py3 import construct_class

import os
class Irrigation_Monitoring( object ):

   def __init__( self, redis_handle, redis_old_handle ):
       self.redis_handle     = redis_handle
       self.redis_old_handle = redis_old_handle


   def measure_flow( self, tag, flow_value, parameters ):
       print("parameters",parameters)
       conversion_rate = parameters[1]
       queue           = parameters[2]
       corrected_flow_rate = flow_value*conversion_rate
       self.redis_old_handle.hset("CONTROL_VARIABLES","global_flow_sensor",flow_value )         
       self.redis_old_handle.hset("CONTROL_VARIABLES","global_flow_sensor_corrected",corrected_flow_rate )
       self.redis_old_handle.hset("FLOW_METERS","main_flow_meter",corrected_flow_rate)
       self.redis_old_handle.lpush("QUEUES:SPRINKLER:FLOW:"+queue,flow_value )
       self.redis_old_handle.ltrim("QUEUES:SPRINKLER:FLOW:"+queue,0,800)
 
       print("corrected_flow_rate",corrected_flow_rate)
       return corrected_flow_rate
 
   def well_controller_output( self, tag, value, parameters  ):
       return 0.0

   def well_controller_input( self ,tag, value, parameters ):
       return 0.0

   def filter_pressure( self ,tag, value, parameters  ):
       return 0.0

   def well_pressure( self, tag,value,parameters):
        return 0.0

   def transfer_irrigation_current( self, tag, current ,parameters):

       print( "valve current",current)
       key = "coil_current"
       self.redis_old_handle.lpush( "QUEUES:SPRINKLER:CURRENT:"+key,current )
       self.redis_old_handle.ltrim( "QUEUES:SPRINKLER:CURRENT:"+key,0,800)
       self.redis_old_handle.hset( "CONTROL_VARIABLES",key, current )
       return current

   def transfer_controller_current( self, tag, current , parameters):

       print( "controller_current ", current)
       key = "plc_current"
       self.redis_old_handle.lpush( "QUEUES:SPRINKLER:CURRENT:"+key,current )
       self.redis_old_handle.ltrim( "QUEUES:SPRINKLER:CURRENT:"+key,0,800)
       self.redis_old_handle.hset( "CONTROL_VARIABLES",key, current )
       return current
  



def construct_irrigation_monitoring_class( redis_handle,redis_old_handle, gm, io_server,io_server_port ):
  
   irrigation_monitoring = Irrigation_Monitoring( redis_handle,redis_old_handle )
   gm.add_cb_handler("measure_flow",    irrigation_monitoring.measure_flow )
   gm.add_cb_handler("well_controller_output",     irrigation_monitoring.well_controller_output )
   gm.add_cb_handler("well_controller_input",    irrigation_monitoring.well_controller_input )
   gm.add_cb_handler("filter_pressure",   irrigation_monitoring.filter_pressure)
   gm.add_cb_handler("well_pressure",   irrigation_monitoring.well_pressure)
   gm.add_cb_handler("transfer_irrigation_current",   irrigation_monitoring.transfer_irrigation_current)
   gm.add_cb_handler("transfer_controller_current",   irrigation_monitoring.transfer_controller_current)
  
   instrument = new_instrument_py3.Modbus_Instrument()

   
   remote_classes = construct_classes_py3.Construct_Access_Classes(io_server,io_server_port)
   fifteen_store   =  []
   minute_store    =  list(gm.match_terminal_relationship(  "MINUTE_ACQUISITION"))[0]   
   hour_store      =  []
   daily_store     =  []
   fifteen_list   =  []
   minute_list     =  list(gm.match_terminal_relationship( "MINUTE_ELEMENT" ))
   hour_list       =  []
   daily_list      =  []

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
   from irrigation_control_py3.misc_support_py3 import IO_Control

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
   redis_old_handle  = redis.StrictRedis( host = '192.168.1.84', port=6379, db = 0 )



   io_server_ip     = io_server_nodes[0]["ip"]
   io_server_port   = io_server_nodes[0]["port"]
   # find ip and port for ip server
   status_server =  gm.match_terminal_relationship("RABBITMQ_STATUS_QUEUE")[0]
   queue_name     = status_server[ "queue"]


   remote_classes = construct_classes_py3.Construct_Access_Classes(io_server_ip,io_server_port)
   io_control  = IO_Control(gm,remote_classes, redis_old_handle,redis_handle)



   status_queue_class = rabbit_cloud_status_publish_py3.Status_Queue(redis_handle, queue_name ) 
   
   construct_linux_acquisition_class= construct_irrigation_monitoring_class( redis_handle,redis_old_handle, gm, io_server_ip, io_server_port )

   

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

'''
   properties = {}
   properties["units"] = "mAmps"
   properties["modbus_remote"] = "satellite_1"
   properties["m_tag"]          = "measure_analog"
   properties["parameters"]     = [ "DF1",1.0]
   #properties["exec_tag"  ]     = ["transfer_controller_current"]
   
   cf.add_info_node( "MINUTE_ELEMENT","CONTROLLER_CURRENT",properties=properties, json_flag=True)


   properties = {}
   properties["units"] = "mAmps"
   properties["modbus_remote"] = "satellite_1"
   properties["m_tag"]          = "measure_analog"
   properties["parameters"]     = ["DF2",1.0]
   #properties["exec_tag"]       = ["transfer_irrigation_current"]
   cf.add_info_node( "MINUTE_ELEMENT","IRRIGATION_VALVE_CURRENT",properties=properties, json_flag=True)

  
   properties = {}
   properties["units"]         = "GPM"
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]   = []
   properties["m_tag"]        = "no_controller"
   properties["parameters"]   = [.0224145939]
   properties["exec_tag"]     = ["measure_flow"]
   cf.add_info_node( "MINUTE_ELEMENT","MAIN_FLOW_METER",properties=properties, json_flag=True)

   
   properties = {}
   properties["units"]         = "AMPS"
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]   = []
   properties["m_tag"]        = "no_controller"
   properties["parameters"]   = [.0224145939]
   properties["exec_tag"]     = ["well_controller_output"]
  
   cf.add_info_node( "MINUTE_ELEMENT","WELL_CONTROLLER_OUTPUT",properties=properties, json_flag = True )

   properties = {}
   properties["units"]         = "AMPS"
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]   = []
   properties["m_tag"]        = "no_controller"
   properties["parameters"]   = [.0224145939]
   properties["exec_tag"]     = ["well_controller_input"]
   cf.add_info_node( "MINUTE_ELEMENT","WELL_CONTROLLER_INPUT", properties=properties, json_flag = True)

   properties = {}
   properties["units"]         = "AMPS"
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]   = []
   properties["m_tag"]        = "no_controller"
   properties["parameters"]   = [.0224145939]
   properties["exec_tag"]     = ["filter_pressure"]
   cf.add_info_node( "MINUTE_ELEMENT","FILTER_PRESSURE", properties=properties, json_flag = True )

   properties = {}
   properties["units"]         = "AMPS"
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]   = []
   properties["m_tag"]        = "no_controller"
   properties["parameters"]   = [.0224145939]
   properties["exec_tag"]     = ["well_pressure"]
   cf.add_info_node( "MINUTE_ELEMENT", "WELL_PRESSURE", properties=properties, json_flag = True )
'''
