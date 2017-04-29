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
import io_control.io_controller_class
import io_control.construct_classes
import io_control.new_instrument

#
#
# File: data_acquisition.py
# Monitors process control data on an minute, hourly, and day basis
#
#



class Data_Acquisition(object):

   def __init__(self):
       pass

   def process_minute_data( self,chainFlowHandle, chainOjb, parameters, event ):
       print "received minute_tick"
       self.common_process( self.minute_list, self.minute_store )
       return "CONTINUE"

   def process_hour_data( self,chainFlowHandle, chainOjb, parameters, event ):
       print "received hour tick"
       self.common_process( self.hour_list , self.hour_store)
  
       return "CONTINUE"

   def process_day_data( self,chainFlowHandle, chainOjb, parameters, event ):
       print "received day tick"
       self.common_process( self.day_list , self.day_store )
       return "CONTINUE"

   def common_process( self, data_list , store_element ):  
       #print "data_list",data_list
       #print "store_element",store_element
       data_dict = {}
       for i in data_list:
           temp_data =   self.slave_interface( i)
           data_dict[i["name"]] = temp_data
       data_json           = json.dumps(data_dict)
       redis_key           = store_element["measurement"]
       redis_array_length  = store_element["length"]
       print "data_json",data_json, redis_key,redis_array_length
       #self.redis_handle.lpush(redis_key,data_json)
       #self.redis_handle.ltrim(redis_key,0,redis_array_length)
       
       # send data to influxdb
       #self.status_queue_class.queue_message(store_element["routing_key"], data_dict )


   def slave_interface( self, element_descriptor ):
    
       action_function = self.load_slave_element( element_descriptor )
       if action_function != None:
            # find modbus address
            modbus_address = self.slave_dict[element_descriptor["modbus_remote"]]["modbus_address"]
            return_value = action_function( modbus_address, element_descriptor["parameters"]) 
       else:
            return_value = None
       return return_value
 
   def load_slave_element(self, list_item):
       return_value = None
       remote = list_item["modbus_remote"]
       if self.slave_dict.has_key(remote):
           slave_element = self.slave_dict[remote]
           slave_class   = slave_element["class"]
           m_tags = slave_class.m_tags
           if m_tags.has_key(list_item["m_tag"]):
              return_value = m_tags[list_item["m_tag"]]

       return return_value
     
   
   def verify_slave_tags( self):
      #print "day list keys",len(self.day_list)
      for i in self.day_list:
         self.verify_slave_element(i)
      #print "hour list keys",len(self.hour_list)
      for i in self.hour_list:
         self.verify_slave_element(i)
      #print "minute list keys",len(self.minute_list)
      for i in self.minute_list:
         self.verify_slave_element(i)

   def verify_slave_element(self, list_item):
       try:
           remote = list_item["modbus_remote"]
           #print "remote",remote
           slave_element = self.slave_dict[remote]
           slave_class   = slave_element["class"]
           m_tags        = slave_class.m_tags
           m_tag_function = m_tags[list_item["m_tag"]]
           #print "m_tags",m_tags
           #print "m_tag_function",m_tag_function
           return m_tag_function     
       except:
           print "list_item",list_item 
           
           raise


    
if __name__ == "__main__":

   import time
   import construct_graph 

   def list_filter( input_list):
      if len( input_list ) > 0:
          return input_list[0]
      else:
          return []

   graph_management = construct_graph.Graph_Management("PI_1","main_remote","LaCima_DataStore") 
   data_store_nodes = graph_management.find_data_stores()
   io_server_nodes  = graph_management.find_io_servers()
  
   # find ip and port for redis data store
   data_server_ip   = data_store_nodes[0]["ip"]
   data_server_port = data_store_nodes[0]["port"]
   redis_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 12 )


   io_server_ip     = io_server_nodes[0]["ip"]
   io_server_port   = io_server_nodes[0]["port"]
   # find ip and port for ip server

   instrument  =  io_control.new_instrument.Modbus_Instrument()

   instrument.set_ip(ip= io_server_ip, port = int(io_server_port))     
  
   remote_classes = io_control.construct_classes.Construct_Access_Classes(instrument)
   
   minute_store    =  graph_management.match_relationship( "MINUTE_ACQUISITION", json_flag = True )[0]
   hour_store      =  graph_management.match_relationship( "HOUR_ACQUISTION", json_flag = True )[0]
   daily_store     =  graph_management.match_relationship( "DAILY_ACQUISTION", json_flag = True )[0]
   
   minute_list     =  graph_management.match_relationship( "MINUTE_ELEMENT", json_flag = True )     
   hour_list       =  graph_management.match_relationship( "HOUR_ELEMENT", json_flag = True )
   day_list        =  graph_management.match_relationship( "DAILY_ELEMENT",   json_flag = True )

   status_stores = graph_management.match_relationship("CLOUD_STATUS_STORE",json_flag = True)
   queue_name    = status_stores[0]["queue_name"]

   status_queue_class = rabbit_cloud_status_publish.Status_Queue(redis_handle, queue_name )

   slave_nodes  = graph_management.match_relationship(  "REMOTE_UNIT", json_flag = True)
   slave_dict    = {}
   for i in slave_nodes:
     class_inst     = remote_classes.find_class( i["type"] )
     slave_dict[i["name"]] = { "modbus_address": i["modbus_address"], "type":i["type"], "class":class_inst }
 

   
  
   
   data_acquisition = Data_Acquisition(  )
   data_acquisition.redis_handle            = redis_handle
   data_acquisition.gm                      = graph_management
   data_acquisition.minute_list             = minute_list
   data_acquisition.hour_list               = hour_list
   data_acquisition.day_list                = day_list
   data_acquisition.minute_store            = minute_store
   data_acquisition.hour_store              = hour_store
   data_acquisition.daily_store             = daily_store
   data_acquisition.instrument              = instrument
   data_acquisition.remote_classes          = remote_classes
   data_acquisition.status_queue_class      = status_queue_class
   data_acquisition.slave_dict              = slave_dict


   #
   #
   #  Verifying graph vs slave nodes
   #
   #
   #
   #
   data_acquisition.verify_slave_tags()

   data_acquisition.process_hour_data( None, None,None,None )
   data_acquisition.process_minute_data( None, None,None,None )

   quit()

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



