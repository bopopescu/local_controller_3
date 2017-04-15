# 
#
# File: eto.py
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


from   eto.eto import *
from   eto.cimis_request import *
import load_files




from cloud_event_queue import Cloud_Event_Queue
#from watch_dog         import Watch_Dog_Client

class Eto_Management(object):
   def __init__( self, redis_handle, eto_stores, rain_stores, status_queue,eto_measurement_handlers ):
       self.redis_handle            = redis_handle
       self.eto_stores              = eto_stores
       self.rain_stores             = rain_stores
       self.status_queue            = status_queue_name
       self.eto_measurement_handler = eto_measurement_handler

   def determine_to_measure(self, name_space ):
       if self.redis_handle.llen(name_space) == 0:
          return True
       data = self.redis_handle.lindex(i["namespace"], 0 )
       current_day      =  datetime.datetime.today().timetuple().tm_yday
       data_time_stamp  = data["time_stamp"]
       data_day         =datetime.fromtimestamp(data_time_stamp).timetuple().tm_yday
       if data_time_stamp != data_day:
           return True
       
       return False



   def calculate_daily_eto( self, *args ):
        for i in self.eto_stores:
           if self.determine_to_measure(i) == True:
              result = self.eto_measurement_handler.compute_eto(i["measurement_tag"])
              self.redis_handle.lpush(i["namespace"],json.dumps(result))
              self.redis_handle.lpush(i["namespace"],0,i["list_length"] )
        for i in self.eto_rain_stores:
           if self.determine_to_measure(i) == True:
              results = self.eto_measurement_handler.compute_eto(i["measurement_tag"])
              self.redis_handle.lpush(i["namespace"],json.dumps(result))
              self.redis_handle.lpush(i["namespace"],0,i["list_length"] )

   def integrate_eto_value( self, *args):
      eto_estimate = 0
      influxdb_item = {}
      # assemble eto data
      # assemble rain_data
      # publish eto_estimate
      # publish rain_estimate
      # send status information
      self.update_bins( eto_estimate)
      
#self.status_queue.queue_message("eto_measurement", properties )

   self.update_sprinkler_bins( self, eto_update ):
       pass 


   def update_sprinklers_time_bins_new( self, eto_data ): 
        value = self.redis.hget("CONTROL_VARIABLES","ETO_RESOURCE_UPDATED")
        if value == "TRUE":
           return
        print "made it here"
        self.cloud_queue.store_event_queue( "store_eto", eto_data,status = "GREEN") 
        keys = self.redis.hkeys( "ETO_RESOURCE" )
        for j in keys:
	     try:
               temp = self.redis.hget( "ETO_RESOURCE", j )
               temp = float(temp)             
             except: 
	       temp = 0
             temp = temp + eto_data
             if temp > .3 :
               temp = .3
             self.redis.hset( "ETO_RESOURCE",j, temp )
 
        #self.redis.hset("CONTROL_VARIABLES","ETO_RESOURCE_UPDATED","TRUE") 
 

class ETO_Calculators( object ):
 
   def __init__( self ):
     #register_handlers
     pass

   def compute_eto( self, tag):
     pass

   def check_computation_tags( self, tag_list ):
      pass  
       

     
if __name__ == "__main__":

   import time
   import construct_graph 
   import io_control.construct_classes
   import io_control.new_instrument

   graph_management = construct_graph.Graph_Management("PI_1","main_remote","LaCima_DataStore")
   #
   # Now Find Data Stores
   #
   #
   #
   data_store_nodes = graph_management.find_data_stores()
   
   data_values = data_store_nodes.values()
   # At present we limit the data stores to only one value
   # find ip and port for redis data store
   data_server_ip = data_values[0]["ip"]
   data_server_port = data_values[0]["port"]
   # Getting redis handle to data server
   redis_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 12 )
  
   # we need the ETO
   eto_stores  = graph_management.match_relationship( "ETO_ENTRY", json_flag = True )
   rain_stores = graph_management.match_relationship( "RAIN_ENTRY", json_flag = True )
   print len(eto_stores), len( rain_stores)
   tag_set = set()
   for i in eto_stores:   
       namespace                 = graph_management.convert_namespace( i["namespace"] )
       i["namespace"]        = namespace
       tag_set.add(i["measurement_tag"])

  
  
   for i in rain_stores:   
       namespace                 = graph_management.convert_namespace( i["namespace"] )
       i["namespace"]        = namespace
       tag_set.add(i["measurement_tag"])
   
   status_store = graph_management.match_relationship("STATUS_STORE")[0]
   queue_name    = status_store["queue_name"]
   status_queue = rabbit_cloud_status_publish.Status_Queue(redis_handle, queue_name )


  


   quit()
   '''
           namespace = self.graph_management.convert_namespace( properties["namespace"] )
           properties["namespace"] = namespace

           redis_handle.lpush( namespace, json.dumps(properties) )
           redis_handle.ltrim( namespace, 0, self.moisture_length )
           print redis_handle.llen(namespace)
           print redis_handle.lindex(namespace,0)
           self.status_queue.queue_message("moisture_measurement", properties )
   '''
   eto_calc  =  ETO_Calculators()
   eto = Eto_Management( redis_handle       = redis_handle  ,
                         status_store      = status_store, 
                         eto_step_up_data  = eto_step_up_data, 
                         humidity_eto      = humidity_eto,
                         eto_data_store    = eto_data_store )




   cf.define_chain("get_current_eto",True)
   cf.insert_link( "link_1", "WaitEvent",    [ "HOUR_TICK" ] )
   cf.insert_link( "link_3", "Code",         [ etm.verify_eto_resource_updated ] )
   cf.insert_link( "link_4", "Code",         [ etm.verify_empty_queue ] )
   cf.insert_link( "link_5", "One_Step",     [ etm.calculate_daily_eto ] )
   cf.insert_link( "link_6", "Reset", [] )

   # eto roll over is 6 PM
   eto_rollover = 12 +6
   cf.define_chain("intergrate_eto_data",True )
   cf.insert_link("link_1","WaitEvent", ["HOUR_TICK"] )
   cf.insert_link("link_2","Code",      [ eto.integrate_data, eto_roll_over ] )
   cf.insert_link "link_1","WaitTod",   ["*",eto_roll_over,"*","*" ])
   cf.insert_link("link_2","One_Step",  [ eto.update_bins ] )
        
 


 


