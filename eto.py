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
'''
class Eto_Management(object):
   def __init__( self, redis_handle, status_queue_class, eto_sources, eto_data_stores,rain_sources,rain_data_stores,eto_calc ):
        self.redis_handle                  = redis_handle
        self.status_queue_class            = status_queue_class
        self.eto_sources                   = eto_sources
        self.eto_data_stores               = eto_data_stores
        self.rain_sources                  = rain_sources
        self.rain_data_stores              = rain_data_stores
        self.eto_calc                      = eto_calc

#eto.make_measurement
#eto.verify_empty_queue
#eto.update_eto_bins 


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
       
'''
     
if __name__ == "__main__":

   import time
   import construct_graph 
   import io_control.construct_classes
   import io_control.new_instrument

   gm = construct_graph.Graph_Management("PI_1","main_remote","LaCima_DataStore")
   #
   # Now Find Data Stores
   #
   #
   #
   data_store_nodes = gm.find_data_stores()
   # find ip and port for redis data store
   data_server_ip   = data_store_nodes[0]["ip"]
   data_server_port = data_store_nodes[0]["port"]
   # find ip and port for ip server
   
   redis_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 12 )

   #
   #
   # find eto sources
   #
   #
   eto_sources = gm.match_relationship("ETO_ENTRY")
   #
   # find eto data stores
   eto_data_stores = gm.match_relationship("ETO_STORE")
   #
   #  Make sure that there is a data store for every eto_source
   #
   #
   eto_source_temp_list  = gm.form_key_list( "measurement", eto_sources )
   eto_store_temp_list   = gm.form_key_list( "name", eto_data_stores )
   assert len(set(eto_source_temp_list)^set(eto_store_temp_list)) == 0, "graphical data base error"
     
   #
   # find rain sources
   # 
   rain_sources = gm.match_relationship("RAIN_ENTRY")
   #
   # find rain stores
   #
   rain_data_stores = gm.match_relationship( "RAIN_STORE" )

   rain_source_temp_list  = gm.form_key_list( "measurement", rain_sources )
   rain_store_temp_list   = gm.form_key_list( "name", rain_data_stores )
   #print set(rain_source_temp_list)^set(rain_store_temp_list)
   assert len(set(rain_source_temp_list)^set(rain_store_temp_list)) == 0, "graphical data base error"

   #
   #
   #
   status_stores = gm.match_relationship("CLOUD_STATUS_STORE")


   queue_name    = status_stores[0]["queue_name"]

   status_queue_class = rabbit_cloud_status_publish.Status_Queue(redis_handle, queue_name )
  
  
   eto_calc  =  ETO_Calculators()
   eto = Eto_Management( redis_handle            = redis_handle,
                         status_queue_class      = status_queue_class,
                         eto_sources             = eto_sources, 
                         eto_data_stores         = eto_data_stores,
                         rain_sources            = rain_sources,
                         rain_data_stores        = rain_data_stores,
                         eto_calc                = eto_calc          )


  




   cf.define_chain("eto_time_window",True)
   cf.insert_link( "link_1","WaitTod",["*",8,"*","*" ])    
   cf.insert_link( "link_2","Enable_Chain",["update_eto"])
   cf.insert_link( "link_3","WaitTod",["*",23,"*","*" ]) 
   cf.insert_link( "link_4", "Disable_Chain",["update_eto"])
   cf.insert_link( "link_5", "Reset", [] )


   cf.define_chain("eto_time_window",True)
   cf.insert_link( "link_1", "One_Step",     [ eto.make_measurement ]
   cf.insert_link( "link_2", "WaitEvent",    [ "HOUR_TICK" ] )
   cf.insert_link( "link_3", "Reset",[])


   cf.define_chain("update_eto_bins",True)
   cf.insert_link( "link_1","WaitEvent", [ "UPDATE_ETO_BINS"] )
   cf.insert_link( "link_2","Code",      [ eto.verify_empty_queue] )
   cf.insert_link( "link_3","One_Step",  [ eto.update_eto_bins ] )
   cf.insert_link( "link_4", "Terminate", [] )
  

        
 


 


