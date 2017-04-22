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
   def __init__( self, redis_handle, status_queue_class, eto_sources, eto_data_stores,rain_sources,rain_data_stores,eto_integrated, rain_integrated,eto_calc ):
        self.redis_handle                  = redis_handle
        self.status_queue_class            = status_queue_class
        self.eto_sources                   = eto_sources
        self.eto_data_stores               = eto_data_stores
        self.rain_sources                  = rain_sources
        self.rain_data_stores              = rain_data_stores
        self.eto_calc                      = eto_calc
        self.redis_old                     = redis.StrictRedis( host = '192.168.1.82', port=6379, db = 0 )


   def generate_new_sources( self, chainFlowHandle, chainObj, parameters, event ):
       
       if event == "INIT":
         return "CONTINUE"
       for i in self.eto_sources:
           data_store = i["measurement"]
           self.redis_handle.lpush(data_store, "EMPTY")

       for i in self.rain_sources:
           data_store = i["measurement"]
           self.redis_handle.lpush(data_store, "EMPTY")
       return "DISABLE"  

   def make_measurement( self, chainFlowHandle, chainOjb, parameters, event ):

       if event == "INIT":
         return "CONTINUE"


       return_value = "CONTINE"
       count = 0
       for i in self.eto_sources:
           data_store = i["measurement"]
           data_value = redis_handle.lindex( data_store,0)
           if type(data_value) == type(str()):
               flag, data = self.eto_calc( i )
               if flag == True:
                   count = count + 1
                   redis_handle.lset( data_store, 0, json.dumps(data_value ))
               else:
                   pass
           else:
               count = count + 1
       for i in self.rain_sources :
           data_store = i["measurement"]
           data_value = redis_handle.lindex( data_store,0)
           if data_value == "EMPTY":
               flag, data = self.rain_calc( i )
               if flag == True:
                   redis_handle.lset( data_store, 0, json.dumps(data_value ))
               else:
                   pass
           else:
               pass
       
       
       print "count",count
       if count >= 2:
           eto_data = self.integrate_data()
           self.update_eto_bins(eto_data)
           self.update_eto_old_bins(eto_data)
           return_value = "TERMINATE"
       return return_value             

   def update_eto_bins( self, eto_data ):
       pass

   def update_sprinklers_time_bins_old( self, eto_data ): 
        keys = self.redis.hkeys( "ETO_RESOURCE" )
        for j in keys:
	     try:
               temp = self.redis.hget( "ETO_RESOURCE", j )
               temp = float(temp)             
             except: 
	       temp = 0
             temp = temp + eto_data
             self.redis.hset( "ETO_RESOURCE",j, temp )

   def update_eto_bins(self, chainFlowHandle, chainOjb, parameters, event ):
       if event == "INIT":
         return "CONTINUE"


       return_value = "CONTINE"
       return return_value
      
   #
   #
   #  
   #
   def print_result_1( self, chainFlowHandle, chainOjb, parameters, event ):
       if event == "INIT":
         return "CONTINUE"


       return_value = "CONTINE"
       count = 0
       for i in self.eto_sources:
           data_store = i["measurement"]
           data_value = redis_handle.lindex( data_store,0)
           print i["name"],data_store,data_value
           redis_handle.lpop(data_store)
           print redis_handle.llen(data_store)
           redis_handle.delete(data_store)
 
       for i in self.rain_sources :
           data_store = i["measurement"]
           data_value = redis_handle.lindex( data_store,0)
           print i["name"],data_store,data_value
           redis_handle.lpop(data_store)
           print redis_handle.llen(data_store)
           redis_handle.delete(data_store)


class ETO_Calculators( object ):
 
   def __init__( self ):
     #register_handlers
     pass

   def eto_calc( eto_store ):
      pass

   def rain_calc( eto_store ):
      pass
       

     
if __name__ == "__main__":

   import time
   import construct_graph 
   import io_control.construct_classes
   import io_control.new_instrument
   import py_cf

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
   temp = gm.match_relationship("ETO_SITES")
   eto_integrated = temp[0]["measurement"]
   temp = gm.match_relationship("RAIN_SOURCES")
   rain_integrated =  temp[0]["measurement"]

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
                         eto_calc                = eto_calc,          
                         eto_integrated          = eto_integrated, 
                         rain_integrated         = rain_integrated   )

  

   #
   # Adding chains
   #
   cf = py_cf.CF_Interpreter()

   cf.define_chain("test_generator",True)
   cf.insert_link( "link_1","SendEvent", ["DAY_TICK",0] )
   cf.insert_link( "link_2","WaitEvent", ["TIME_TICK"] )
   cf.insert_link( "link_3","One_Step",[eto.print_result_1] )


   cf.define_chain("eto_time_window",True)
   cf.insert_link( "link_1","WaitEvent", ["DAY_TICK"] )
   cf.insert_link( "link_2","One_Step", [ eto.generate_new_sources ])
   cf.insert_link( "link_1","WaitTod",["*",8,"*","*" ])    
   cf.insert_link( "link_2","Enable_Chain",["eto_time_window"])
   cf.insert_link( "link_3","WaitTod",["*",23,"*","*" ]) 
   cf.insert_link( "link_4", "Disable_Chain",["eto_time_window"])
   cf.insert_link( "link_5", "Reset", [] )


   cf.define_chain("eto_time_window",False)
   cf.insert_link( "link_1", "Code",         [ eto.make_measurement ] )
   cf.insert_link( "link_2", "WaitEvent",    [ "HOUR_TICK" ] )
   cf.insert_link( "link_3", "Reset",[])

   #
   # Executing chains
   #
   cf_environ = py_cf.Execute_Cf_Environment( cf )
   cf_environ.execute()

   
 
