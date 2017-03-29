# external control 
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




class Moisture_Control():
   def __init__(self, redis_handle , status_queue ): 
       self.redis_handle           = redis_handle
       self.redis_handle.hset("MOISTURE_CONTROL","MANUAL_UPDATE",0 )
       self.moisture_length = 1000 # 10 days @ 15 minute interval
       self.status_queue  = status_queue

 
        



   def make_measurements( self, modbus_address,   driver_class ):
       measure_properties = {}
       time_stamp = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(time.time()))
       measure_properties["time_stamp"] = time_stamp
       try:
         
         driver_class.make_soil_temperature( modbus_address )
         time.sleep(1.0)
         driver_class.make_air_temp_humidity( modbus_address )
         time.sleep(1.0)
         temp = driver_class.check_status( modbus_address )
         time.sleep(1.0)
         driver_class.force_moisture_reading(modbus_address)
         time.sleep(1.0)

         temp =  driver_class.read_moisture_control( modbus_address )
         measure_properties["air_humidity"]              =     temp["AIR_HUMIDITY_FLOAT"]
         measure_properties["soil_temperature"]          =     temp["MOISTURE_SOIL_TEMP_FLOAT"]
         measure_properties["air_temperature"]           =     temp["AIR_TEMP_FLOAT"]
         measure_properties["sensor_configuration"]      =     driver_class.read_moisture_configuration( modbus_address )
         measure_properties["sensor_data"]               =     driver_class.read_moisture_data(  modbus_address ) 
         measure_properties["resistive_data"]            =     driver_class.read_moisture_resistive_data( modbus_address )
         measure_properties["read_status"]               =     "Communication was successful at "+time_stamp

          
       except:
          #raise
          print "exception handler"
          measure_properties["read_status"]  = "Communications problems with moisture plc at "+time_stamp
       return measure_properties
       

   def update_moisture_readings( self,chainFlowHandle, chainOjb, parameters, event ):
       if event == "INIT":
         return "CONTINUE"
       #print self.moisture_stores
       for key, value in self.moisture_stores.items():
           io_device = self.moisture_stations[key]
           type = io_device["type"]
           modbus_address = io_device["modbus_address"]
           driver_class = self.remote_classes.find_class( type )
           properties = copy.deepcopy( value)
           measurement_properties = self.make_measurements( int(modbus_address), driver_class )
           properties["measurements"] = measurement_properties
           #
           # Now Store Data
           #
           namespace = self.graph_management.convert_namespace( properties["namespace"] )
           properties["namespace"] = namespace
           redis_handle.lpush( namespace, json.dumps(properties) )
           redis_handle.ltrim( namespace, 0, self.moisture_length )
           print redis_handle.llen(namespace)
           print redis_handle.lindex(namespace,0)
           self.status_queue.queue_message("moisture_measurement", properties )


   def check_update_flag( self,chainFlowHandle, chainOjb, parameters, event ):

       if event == "INIT":
         return "CONTINUE"

       update_flag = self.redis_handle.hget("MOISTURE_CONTROL","MANUAL_UPDATE")
       update_flag = int(update_flag)
       
       if update_flag == 0:
           return "RESET"
       else:
           print "update flag is not zero"
           self.redis_handle.hset("MOISTURE_CONTROL","MANUAL_UPDATE",0)
           return "DISABLE"


     
if __name__ == "__main__":
   import time
   import construct_graph 
   import io_control.construct_classes
   import io_control.new_instrument

   graph_management = construct_graph.Graph_Management("PI_1","main_remote","LaCima_DataStore")
   moisture_stations = graph_management.find_remotes_by_function("moisture")
   data_store_nodes = graph_management.find_data_stores()
   io_server_nodes  = graph_management.find_io_servers()
   
   data_values = data_store_nodes.values()
   io_values   = io_server_nodes.values()

   # find ip and port for redis data store
   data_server_ip = data_values[0]["ip"]
   data_server_port = data_values[0]["port"]
   io_server_ip =   io_values[0]["ip"]
   io_server_port = io_values[0]["port"]

   
   # find ip and port for ip server

   instrument  =  io_control.new_instrument.Modbus_Instrument()

   instrument.set_ip(ip= io_server_ip, port = int(io_server_port))     

   remote_classes = io_control.construct_classes.Construct_Access_Classes(instrument)
  
   #driver_class = remote_classes.find_class( "PSOC_4_Moisture" )
   #driver_class.make_soil_temperature( 40 )
  
   #
   # Find data Stores
   moisture_data_stores = graph_management.find_data_store_by_function("MOISTURE_DATA")
   moisture_stores     = set( moisture_data_stores.keys() )
   moisture_remotes = set ( moisture_stations.keys() )
   results = moisture_remotes ^ moisture_stores
   
   if len( results ) != 0:
      raise ValueError("Imbalance in setup graph")
   
   
  

   # 
   #  
   
   redis_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 12 )
   #import moisture.new_instrument_network
   #import moisture.psoc_4m_moisture_sensor_network 
   
   #new_instrument  =  moisture.new_instrument_network.new_instrument_network()
   #new_instrument.set_ip(ip= "192.168.1.82", port = 5005)     
  
   #psoc_moisture = moisture.psoc_4m_moisture_sensor_network.PSOC_4M_MOISTURE_UNIT( new_instrument )

   status_stores = graph_management.match_relationship("STATUS_STORE")
   print "status_stores",status_stores
   status_store  = status_stores[0]
   queue_name    = status_store["queue_name"]

   status_queue = rabbit_cloud_status_publish.Status_Queue(redis_handle, queue_name )
   moisture = Moisture_Control( redis_handle , status_queue)
   moisture.moisture_stations = moisture_stations
   moisture.moisture_stores = moisture_data_stores
   moisture.remote_classes = remote_classes
   moisture.graph_management = graph_management
  

   moisture.update_moisture_readings(None,None,None, None ) #populate data
 
   #
   # Adding chains
   #
   cf = py_cf.CF_Interpreter()
  

   cf.define_chain("update_moisture_readings",True)
   cf.insert_link( "link_1", "WaitEventCount",    [ "MINUTE_TICK",15,0 ] )
   cf.insert_link( "link_2", "One_Step",     [  moisture.update_moisture_readings ] )
   cf.insert_link( "link_3", "Reset", [] )


   cf.define_chain("check_for_moisture_update",True)
   cf.insert_link( "link_1", "WaitEvent",    [ "TIME_TICK" ] )
   cf.insert_link( "link_2", "Code",         [ moisture.check_update_flag ] )
   cf.insert_link( "link_3", "One_Step",      [ moisture.update_moisture_readings ] )
   cf.insert_link( "link_4", "Reset", [] )



 
 
 

#  cf.define_chain("watch_dog_thread",True)
#  cf.insert_link( "link_1","WaitTod",["*","*","*",30 ])
#  cf.insert_link( "link_2","One_Step",[ wc.pat_wd ])
#  cf.insert_link( "link_3","WaitTod",["*","*","*",55 ])
#  cf.insert_link( "link_4","Reset",[])  


  #
  # Executing chains
  #
   cf_environ = py_cf.Execute_Cf_Environment( cf )
   cf_environ.execute()



