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




#from cloud_event_queue import Cloud_Event_Queue
#from watch_dog         import Watch_Dog_Client

class Eto_Management():
   def __init__( self, redis_handle, status_store_key , eto_setup_data_key, humidity_eto_key, eto_data_store_key ):
       self.redis_handle        = redis_handle
       self.status_store_key        = status_store_key
       self.eto_setup_data_key      = eto_setup_data_key
       self.status_store_key        = status_store_key
       #self.eto = ETO(alt,access_codes)


   def calculate_daily_eto( self, *args ):
        results = self.eto.integrate_eto_data( )
        print "results",results
        self.redis.hset("CONTROL_VARIABLES","ETO",results[0]["eto"] )
        self.redis.hset("CONTROL_VARIABLES","RAIN",results[0]["rain"])
        self.redis.hset("CONTROL_VARIABLES","ETO_DATA",results[1])
        self.redis.hset("CONTROL_VARIABLES","RAIN_DATA",results[2])        
         
       
        self.update_sprinklers_time_bins_new( results[0]["eto"] )
        self.redis.hset("CONTROL_VARIABLES","ETO_RESOURCE_UPDATED","TRUE") 
   def verify_eto_resource_updated( self, *args ):
       if self.redis.hget("CONTROL_VARIABLES","ETO_RESOURCE_UPDATED") == "TRUE" :
          returnValue = "RESET"  
       else:
          returnValue = "DISABLE"
       print "verify eto resuorce",returnValue

       return returnValue

   def verify_empty_queue( self, *args ):
       if self.redis.llen( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE" ) != 0 :
          
          returnValue = "RESET"  
       elif self.redis.llen("QUEUES:SPRINKLER:IRRIGATION_QUEUE") != 0 :
          returnValue = "RESET"
       else:
          returnValue = "DISABLE"
       print "verify empty queue",returnValue
       return returnValue



   def calculate_daily_eto( self, *args ):
        results = self.eto.integrate_eto_data( )
        print "results",results
        self.redis.hset("CONTROL_VARIABLES","ETO",results[0]["eto"] )
        self.redis.hset("CONTROL_VARIABLES","RAIN",results[0]["rain"])
        self.redis.hset("CONTROL_VARIABLES","ETO_DATA",results[1])
        self.redis.hset("CONTROL_VARIABLES","RAIN_DATA",results[2])        
         
       
        self.update_sprinklers_time_bins_new( results[0]["eto"] )
        self.redis.hset("CONTROL_VARIABLES","ETO_RESOURCE_UPDATED","TRUE") 
  
   def clear_flag( self,chainFlowHandle, chainObj, parameters, event ):
        self.redis.hset("CONTROL_VARIABLES","ETO_RESOURCE_UPDATED","FALSE")



  
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
 

          
   def delete_email_files( self,chainFlowHandle, chainOjb, parameters, event ):  
       print( str(datetime.datetime.now())+"\n")
       print("deleteing emails \n")
       imap_username = 'lacima.ranch@gmail.com'
       imap_password = 'Gr1234gfd'
       delete_cimis_email( imap_username, imap_password )
  

       
'''    
       
   def verify_eto_resource_updated( self, *args ):
       if self.redis.hget("CONTROL_VARIABLES","ETO_RESOURCE_UPDATED") == "TRUE" :
          returnValue = "RESET"  
       else:
          returnValue = "DISABLE"
       print "verify eto resuorce",returnValue

       return returnValue

   def verify_empty_queue( self, *args ):
       if self.redis.llen( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE" ) != 0 :
          
          returnValue = "RESET"  
       elif self.redis.llen("QUEUES:SPRINKLER:IRRIGATION_QUEUE") != 0 :
          returnValue = "RESET"
       else:
          returnValue = "DISABLE"
       print "verify empty queue",returnValue
       return returnValue



   def calculate_daily_eto( self, *args ):
        results = self.eto.integrate_eto_data( )
        print "results",results
        self.redis.hset("CONTROL_VARIABLES","ETO",results[0]["eto"] )
        self.redis.hset("CONTROL_VARIABLES","RAIN",results[0]["rain"])
        self.redis.hset("CONTROL_VARIABLES","ETO_DATA",results[1])
        self.redis.hset("CONTROL_VARIABLES","RAIN_DATA",results[2])        
         
       
        self.update_sprinklers_time_bins_new( results[0]["eto"] )
        self.redis.hset("CONTROL_VARIABLES","ETO_RESOURCE_UPDATED","TRUE") 
  
   def clear_flag( self,chainFlowHandle, chainObj, parameters, event ):
        self.redis.hset("CONTROL_VARIABLES","ETO_RESOURCE_UPDATED","FALSE")



  
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
 

          
   def delete_email_files( self,chainFlowHandle, chainOjb, parameters, event ):  
       print( str(datetime.datetime.now())+"\n")
       print("deleteing emails \n")
       imap_username = 'lacima.ranch@gmail.com'
       imap_password = 'Gr1234gfd'
       delete_cimis_email( imap_username, imap_password )
'''

     
if __name__ == "__main__":

   import time
   import construct_graph 
   import io_control.construct_classes
   import io_control.new_instrument

   graph_management = construct_graph.Graph_Management("PI_1","main_remote","LaCima_DataStore")
   moisture_stations = graph_management.find_remotes_by_function("moisture")
   data_store_nodes = graph_management.find_data_stores()
   
   data_values = data_store_nodes.values()
 

   # find ip and port for redis data store
   data_server_ip = data_values[0]["ip"]
   data_server_port = data_values[0]["port"]
   
   # Find data Stores
   moisture_data_start = graph_management.find_data_store_by_function("MOISTURE_STORE")
 



   moisture_data_stores = graph_management.find_data_store_by_function("MOISTURE_DATA")


   eto_step_up_data   =  graph_management.convert_namespace(graph_management.find_relationship_keys("ETO_SETUP_DATA")[0])
   humidity_eto       =  graph_management.convert_namespace(graph_management.find_data_store_by_function("TEMP_HUMIDITY_DAILY_ETO")["TEMP_HUMIDITY_DAILY_ETO"]["namespace"])
   eto_data_store     =  graph_management.convert_namespace(graph_management.find_data_store_by_function("ETO_SETUP_DATA")["ETO_SETUP_DATA"]["namespace"])   # access_codes
   status_store       =  graph_management.convert_namespace(graph_management.find_relationship_keys("STATUS_STURE")[0])

   redis_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 12 )
   eto = Eto_Management( redis_handle       = redis_handle  ,
                         status_store      = status_store, 
                         eto_step_up_data  = eto_step_up_data, 
                         humidity_eto      = humidity_eto,
                         eto_data_store    = eto_data_store )

  cf.define_chain("delete_cimis_email_data",True)
  cf.insert_link( "link_1","WaitTod",["*",9,"*","*" ])
  cf.insert_link( "link_3","One_Step",[etm.delete_email_files])
  cf.insert_link( "link_4","WaitTod",["*",10,"*","*" ])
  cf.insert_link( "link_5","Reset",[])  



 
  cf.define_chain("get_current_eto",True)
  cf.insert_link( "link_1","WaitTod",["*",9,"*","*" ])
  cf.insert_link( "link_2", "One_Step", [ etm.calculate_daily_eto ] )
  cf.insert_link( "link_3","WaitTod",["*",10,"*","*" ])
  cf.insert_link( "link_4", "Reset", [] )


 


 




'''
  redis_config = redis.StrictRedis(host='localhost', port=6379, db=2)
  redis_host  = redis_config.get("REDIS_SERVER_IP")
  redis_port  = redis_config.get("REDIS_SERVER_PORT")
  redis_db    = redis_config.get("REDIS_SERVER_DB")
  redis_handle = redis.StrictRedis( redis_host, redis_port, redis_db )
  action       = System_Monitoring( redis_handle )
  sched        = Schedule_Monitoring( redis_handle )
  sys_files    = load_files.SYS_FILES(redis_handle)
  access_data  = sys_files.load_file( "eto_api_setup.json")
  etm = Eto_Management( redis_handle, access_data )
  print( "made it here on startup")
  ntpd = Ntpd()
  pi_temp = PI_Internal_Temperature( redis_handle )
  wc = Watch_Dog_Client(redis_handle, "extern_ctrl","external control")
  wc.pat_wd(  )
  #
  # Adding chains
  #
  cf = py_cf.CF_Interpreter()
  

  cf.define_chain("get_current_eto",True)
  cf.insert_link( "link_1", "WaitEvent",    [ "MINUTE_TICK" ] )
  cf.insert_link( "link_2", "One_Step",     [ pi_temp.processor_temp ] )
  cf.insert_link( "link_3", "Code",         [ etm.verify_eto_resource_updated ] )
  cf.insert_link( "link_4", "Code",         [ etm.verify_empty_queue ] )
  cf.insert_link( "link_5", "One_Step",     [ etm.calculate_daily_eto ] )
  cf.insert_link( "link_6", "Reset", [] )


  cf.define_chain("delete_cimis_email_data",True)
 
  cf.insert_link( "link_1","WaitTod",["*",9,"*","*" ])
  cf.insert_link( "link_2","One_Step",[etm.clear_flag])
  cf.insert_link( "link_3","One_Step",[etm.delete_email_files])
  cf.insert_link( "link_4","WaitTod",["*",10,"*","*" ])
  cf.insert_link( "link_5","Reset",[])  


  cf.define_chain( "plc_auto_mode", True )
  cf.insert_link(  "link_2",  "One_Step", [ action.check_for_active_schedule ] )
  cf.insert_link(  "link_1",  "One_Step", [ sched.check_for_active_schedule ] )
  cf.insert_link(  "link_2",  "WaitEvent",[ "MINUTE_TICK" ] )
  cf.insert_link(  "link_3",  "Reset",[] )
    
  cf.define_chain("clear_done_flag",True)
  cf.insert_link(  "link_2",  "One_Step", [action.clear_done_flag ] )
  cf.insert_link(  "link_2",  "One_Step", [sched.clear_done_flag ] )
  cf.insert_link(  "link_1",  "WaitEvent",[ "MINUTE_TICK" ] )
  cf.insert_link(  "link_3",  "Reset",[] )




#  cf.define_chain("new_day_house_keeping",False)
#  cf.insert_link( "link_1","WaitTod",["*",12,"*","*" ])
#  cf.insert_link( "link_2","One_Step",[etm.do_house_keeping])
#  cf.insert_link( "link_3","WaitTod",["*",13,"*","*" ])
#  cf.insert_link( "link_4","Reset",[])
#
#  cf.define_chain("get_current_eto",False)
#  cf.insert_link( "link_1", "WaitTod", ["*",12, 20,"*" ] )
#  cf.insert_link( "link_2", "One_Step", [etm.calculate_current_eto ] )
#  cf.insert_link( "link_3", "One_Step", [etm.calculate_daily_eto ] )
#  cf.insert_link( "link_4", "WaitTod", ["*",13,50,"*" ] )
#  cf.insert_link( "link_5", "Reset", [] )
# 
 
 

#
#
# internet time update
#
#
  
  cf.define_chain("ntpd",True)
  cf.insert_link( "link_9","Log",["ntpd"] )
  cf.insert_link(  "link_1",  "One_Step", [ntpd.get_time] )
  cf.insert_link(  "link_10", "Log",["got time"] )
  cf.insert_link(  "link_2",  "WaitEvent",[ "HOUR_TICK" ] )
  cf.insert_link(  "link_3",  "Reset",[] )
#
#
# update clocks from internet
#
#

  cf.define_chain("watch_dog_thread",True)
  cf.insert_link( "link_1","WaitTod",["*","*","*",30 ])
  cf.insert_link( "link_2","One_Step",[ wc.pat_wd ])
  cf.insert_link( "link_3","WaitTod",["*","*","*",55 ])
  cf.insert_link( "link_4","Reset",[])  


  #
  # Executing chains
  #
  cf_environ = py_cf.Execute_Cf_Environment( cf )
  cf_environ.execute()



'''