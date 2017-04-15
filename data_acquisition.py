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
import urllib2
import math
import redis
import base64
import json
import py_cf
import os
import copy
import load_files
import rabbit_cloud_status_publish



#
#
# File: data_acquisition.py
# Monitors process control data on an minute, hourly, and day basis
#
#



class Data_Acquisition(object):

   def __init__(self,  redis_handle, minute_value_nodes, hour_value_nodes, day_value_nodes, minute_actions, hour_actions, day_actions ):
       self.redis_handle                  = redis_handle
       self.minute_value_nodes            = minute_value_nodes  # keys <value_key> <list_key>,<list_length>
       self.hour_value_nodes              = hour_value_nodes
       self.day_value_nodes               = day_value_nodes
       self.minute_actions                = minute_actions # keys <get_data> a function <name> redis store
       self.hour_actions                  = hour_actions
       self.day_actions                   = day_actions


   def process_minute_data( self,chainFlowHandle, chainOjb, parameters, event ):
       print "received minute_tick"
       self.common_process( self.minute_value_nodes, self.minute_actions )
       return "CONTINUE"

   def process_hour_data( self,chainFlowHandle, chainOjb, parameters, event ):
       print "received hour tick"
       self.common_process( self.hour_value_nodes, self.hour_actions )
  
       return "CONTINUE"

   def process_day_data( self,chainFlowHandle, chainOjb, parameters, event ):
       print "received day tick"
       self.common_process( self.hour_value_nodes, self.hour_actions )
       return "CONTINUE"

   def common_process( self, value_nodes, action_list ,event ):  
       if event == "INIT":
            return
       if len( action_list ) == 0:
           return 
       data_dict = {}
       for i in action_list:
            temp_data =   i["get_data"]()
            self.redis_handle.set( i["name"],temp_data )
            data_dict[i["name"]] = temp_data
       
       data_json = json.dumps(data_dict)
       self.redis_handle.set( value_nodes["value_key"])
       self.redis_handle.lpush( value_nodes["list_key"], data_json )
       self.redis_handle.ltrim( value_nodes["list_key"], 0, value_nodes["list_length"] )
       # send data to influxdb

class Node_Assembler(object):

   def __init__( self , graph_management ):
       self.gm = graph_management

   def find_value_nodes( self, value_label, list_label ):
      dict = {}
      # return dict["value"],dict["list"],dict["list_length"]
      return dict

   def find_data_elements(self, data_element_tag ):
       dict = {}
       # return dict["name"], dict["properties"]


class Slave_Action_Assembler( object ):
   def __init__(self, graph_management )
       self.gm = graph_management
       self.io_server_nodes  = graph_management.find_io_servers()
       io_server_ip =   io_values[0]["ip"]
       io_server_port = io_values[0]["port"]
       # find ip and port for ip server
       instrument  =  io_control.new_instrument.Modbus_Instrument()
       instrument.set_ip(ip= io_server_ip, port = int(io_server_port))     
       remote_classes = io_control.construct_classes.Construct_Access_Classes(instrument)


   def assemble_actions( self, data_elements ):
       action_list = []
       for i in data_element:
           action_list.append( self.generate_a_actions( i )
       return action_list
               
   def generate_an_action( action_element )
    






    
if __name__ == "__main__":

   import time
   import construct_graph 

   graph_management = construct_graph.Graph_Management("PI_1","main_remote","LaCima_DataStore") 
   data_store_nodes = graph_management.find_data_stores()  
   data_values = data_store_nodes.values()
   # find ip and port for redis data store
   data_server_ip = data_values[0]["ip"]
   data_server_port = data_values[0]["port"]
   

    
   minute_list     =  graph_management.match_relationship( "MINUTE_LIST", json_flag = True )[0]
   hour_list       =  graph_management.match_relationship( "HOUR_LIST", json_flag = True )[0]
   day_list        =  graph_management.match_relationship( "DAILY_LIST",   json_flag = True )[0]

   '''
   Need to assemble acquisiton lists
   '''
   minute_acquisition = []
   hour_acquisition = []
   day_acquisition = []
   
   redis_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 12 )

   data_acquisition = Data_Acquisition( redis_handle, graph_management, minute_list, hour_list, day_list, minute_acquisition, hour_acquisition, day_acquisition )
 
   #
   # Adding chains
   #
   cf = py_cf.CF_Interpreter()


   #cf.define_chain("test",True)
   #cf.insert_link( "linkxx","Log",["test chain start"])
   #cf.insert_link( "link_0", "SendEvent",  ["MINUTE_TICK",1] )
   #cf.insert_link( "link_1", "WaitEvent",  ["TIME_TICK"] )
   #cf.insert_link( "link_2", "SendEvent",    [ "HOUR_TICK",1 ] )
   #cf.insert_link( "link_3", "WaitEvent", ["TIME_TICK"])
   #cf.insert_link( "link_4", "SendEvent",    [ "DAY_TICK", 1] )


   cf.define_chain("minute_list",True)
   cf.insert_link( "link_1","WaitEvent",["MINUTE_TICK" ])
   cf.insert_link( "link_2","One_Step",[data_acquisition.process_minute_data])
   cf.insert_link( "link_3","Reset",[])  


   cf.define_chain("hour_list",True)
   cf.insert_link( "link_1","WaitEvent",["HOUR_TICK" ])
   cf.insert_link( "link_2","One_Step",[data_acquisition.process_hour_data])
   cf.insert_link( "link_3","Reset",[])  

   cf.define_chain("day_list",True)
   cf.insert_link( "link_1","WaitEvent",["DAY_TICK" ])
   cf.insert_link( "link_2","One_Step",[data_acquisition.process_day_data])
   cf.insert_link( "link_3","Reset",[])  
   print "starting chain flow"
   cf_environ = py_cf.Execute_Cf_Environment( cf )
   cf_environ.execute()



