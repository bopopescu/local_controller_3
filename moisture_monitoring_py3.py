# external control 
import datetime
import time
import string
#import urllib2
import math
import redis
import base64
import json


import os
import copy




class Moisture_Control(object):
   def __init__(self, redis_handle , graph_management,status_queue_classes, moisture_app_classes, moisture_remote_classes, remote_classes):
       self.redis_handle            = redis_handle
       self.gm                      = graph_management 
       self.status_queue_class      = status_queue_classes
       self.moisture_app_classes    = moisture_app_classes
       self.moisture_remote_classes = moisture_remote_classes   
       self.remote_classes          = remote_classes
       self.unpack_graph()
       self.clear_update_flag()
      

   def unpack_graph( self ):
       self.update_flag = self.gm.match_terminal_relationship("MOISTURE_MANUAL_UPDATE_FLAG" )[0]
       self.web_moisture_trigger_key = self.update_flag["name"]
       print( self.web_moisture_trigger_key )
       self.store_data_list = {}
       self.store_air_list  = {}
       self.rollover_list   = {}
       moisture_data = self.gm.match_terminal_relationship("MOISTURE_DATA" )
       air_temp_list = self.gm.match_terminal_relationship("MOISTURE_AIR_TEMP_LIST" )
       moisture_rollover = self.gm.match_terminal_relationship("MOISTURE_ROLLOVER" )

       for i in moisture_data:
           self.store_data_list[i["name"] ] = i

       for i in air_temp_list:
           self.store_air_list[i["name"] ] = i

       for i in moisture_rollover:
           self.rollover_list[i["name"] ] = i

   def clear_update_flag( self ):
      list = self.update_flag["name"]
      self.redis_handle.delete(list)

   def find_driver( self, port ):
       for i in self.moisture_remote_classes:
           
           if i["modbus_address"] == port:
               return i
       raise ValueError("Cannot find device at specified port")


   def update_moisture_readings( self,chainFlowHandle, chainOjb, parameters, event ):
       
       list_data = []
       
       for value in self.moisture_app_classes:
           modbus_address = value["slave_controller_address"]
           driver = self.find_driver( modbus_address )
           self.update_a_reading( value, driver, list_data )
           


          

   def update_a_reading(self, value, driver, list_data ):
          
           properties = copy.deepcopy( value)
           modbus_address = driver["modbus_address"]
           measurement_properties = self.make_measurements( int(modbus_address), driver,list_data )
           if measurement_properties["measurement_status"] == 0:
               return
           properties["measurements"] = measurement_properties
           
           name = properties["name"]
           redis_key = self.store_data_list[name]["queue_name"]
           redis_length = self.store_data_list[name]["list_length"]
           self.redis_handle.lpush(redis_key,json.dumps(properties))
           self.redis_handle.ltrim(redis_key,0,redis_length)
 
           self.status_queue_class.queue_message("moisture_measurement", properties )



   def make_measurements( self, modbus_address,   io_wrapper , list_data):
       type = io_wrapper["type"]
       driver_class = remote_classes.find_class(type)
       measure_properties = {}
       time_stamp = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(time.time()))
       measure_properties["time_stamp"] = time_stamp
       try:
         item = {}
         driver_class.make_soil_temperature( modbus_address )
         time.sleep(1.0)
         driver_class.make_air_temp_humidity( modbus_address )
         time.sleep(1.0)
         temp = driver_class.check_status( modbus_address )
         time.sleep(1.0)
         driver_class.force_moisture_reading(modbus_address)
         time.sleep(1.5)

         temp =  driver_class.read_moisture_control( modbus_address )
         item["humidity"] = temp["AIR_HUMIDITY_FLOAT"]
         item["temperature"] =temp["AIR_TEMP_FLOAT"]
         list_data.append(item)
         measure_properties["air_humidity"]              =     temp["AIR_HUMIDITY_FLOAT"]
         measure_properties["soil_temperature"]          =     temp["MOISTURE_SOIL_TEMP_FLOAT"]
         measure_properties["air_temperature"]           =     temp["AIR_TEMP_FLOAT"]
         measure_properties["sensor_configuration"]      =     driver_class.read_moisture_configuration( modbus_address )
         measure_properties["sensor_data"]               =     driver_class.read_moisture_data(  modbus_address ) 
         measure_properties["resistive_data"]            =     driver_class.read_moisture_resistive_data( modbus_address )
         measure_properties["read_status"]               =     "Communication was successful at "+time_stamp
         measure_properties["measurement_status"]        =     1
         #print("measure_properties",measure_properties)
       except:
          #raise
          print ("exception handler")
          measure_properties["read_status"]  = "Communications problems with moisture plc at "+time_stamp
          measure_properties["measurement_status"]        =     0
       return measure_properties
       


       

   def check_update_flag( self,chainFlowHandle, chainOjb, parameters, event ):

       if self.redis_handle.llen( self.web_moisture_trigger_key ) > 0:
       
          key = self.redis_handle.rpop(self.web_moisture_trigger_key)
          if key != None:
             self.update_moisture_readings( None, None, None, None )             
       

       return "DISABLE"
 


 

   def hour_update( self,chainFlowHandle, chainOjb, parameters, event ):

       #print "hour tick"
       for  i in self.moisture_app_classes:
           name = i["name"]
           redis_key = self.store_data_list[name]["queue_name"]
           data_json  = redis_handle.lindex( redis_key, 0)
           data   = json.loads(data_json)          
           temp = {"air_temperature": data["measurements"]["air_temperature"],"air_humidity": data["measurements"]["air_humidity"]}
           redis_key = self.store_air_list[name]["queue_name"]
           redis_length = self.store_air_list[name]["list_length"]
           self.redis_handle.lpush(redis_key,json.dumps(temp))
           self.redis_handle.ltrim(redis_key,0,redis_length)
       return "DISABLE" 
       
 
   def day_update( self,chainFlowHandle, chainOjb, parameters, event ):

       for  i in self.moisture_app_classes:
           name = i["name"]
           hour_redis_key = self.store_air_list[name]["queue_name"]
           #print "hour_redis_key",hour_redis_key
           #print "hour_redis_key",self.redis_handle.llen(hour_redis_key)
           rollover_redis_key = self.rollover_list[name]["queue_name"]
           #print "rollover",self.rollover_list[name]["name"]
           #print "--->", self.redis_handle.llen(rollover_redis_key)
           if self.redis_handle.llen(rollover_redis_key) > 0:
                  #print "---"
                  self.redis_handle.delete(rollover_redis_key)
           #print "++++",self.redis_handle.llen(hour_redis_key)

           self.redis_handle.rename( hour_redis_key , rollover_redis_key)
           #print "len",self.redis_handle.llen(rollover_redis_key)
           return "DISABLE"
 


     
if __name__ == "__main__":
   import time
   import farm_template_py3 
   import rabbit_cloud_status_publish_py3
   import io_control_py3
   import io_control_py3.new_instrument_py3
   import io_control_py3.io_controller_py3
   import construct_classes_py3

   def find_remotes_by_function( graph_management, function ):
       keys = graph_management.match_terminal_relationship("REMOTE_UNIT")
       return_value = []
       for i in keys:
           if function in i["function"]:
              return_value.append(i)
       
       return return_value


   from py_cf_py3.chain_flow import CF_Base_Interpreter
   cf = CF_Base_Interpreter()

   graph_management = farm_template_py3.Graph_Management("PI_1","main_remote","LaCima_DataStore")
  
   data_store_nodes = graph_management.find_data_stores()
   io_server_nodes  = graph_management.find_io_servers()
  
   # find ip and port for redis data store
   data_server_ip   = data_store_nodes[0]["ip"]
   data_server_port = data_store_nodes[0]["port"]
   io_server_ip     = io_server_nodes[0]["ip"]
   io_server_port   = io_server_nodes[0]["port"]
   # find ip and port for ip server
   instrument  =  io_control_py3.new_instrument_py3.Modbus_Instrument()

   instrument.set_ip(ip= io_server_ip, port = int(io_server_port))     
   
   remote_classes =construct_classes_py3.Construct_Access_Classes(instrument)

   moisture_app_classes = graph_management.match_terminal_relationship( "MOISTURE_CTR")
   moisture_remote_classes = find_remotes_by_function(graph_management, "moisture")

   
   if len(moisture_app_classes) > len(moisture_remote_classes):
      raise ValueError("Imbalance in setup graph")

   
   redis_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 12 )
   status_stores = graph_management.match_terminal_relationship("CLOUD_STATUS_STORE")

   status_stores = list(status_stores)
   queue_name    = status_stores[0]["queue_name"]

   status_queue_class = rabbit_cloud_status_publish_py3.Status_Queue(redis_handle, queue_name )

   

   moisture_class = Moisture_Control( redis_handle , graph_management,
                    status_queue_class, moisture_app_classes, moisture_remote_classes , remote_classes )
   

   moisture_class.update_moisture_readings(None,None,None, None ) #populate data

   #
   # Adding chains
   #

   
   #cf.define_chain("test",True)
   #cf.insert_link( "link_1", "SendEvent",    [ "HOUR_TICK",1 ] )
   #cf.insert_link( "link_2", "WaitEvent", ["TIME_TICK"])
   #cf.insert_link( "link_3", "SendEvent",    [ "DAY_TICK", 1] )
   

   cf.define_chain("update_moisture_readings",True)
   cf.insert_link( "link_1", "WaitEventCount",    [ "MINUTE_TICK",15,0 ] )
   cf.insert_link( "link_2", "One_Step",     [  moisture_class.update_moisture_readings ] )
   cf.insert_link( "link_3", "Reset", [] )


   cf.define_chain("check_for_moisture_update",True)
   cf.insert_link( "link_1", "WaitEvent",    [ "TIME_TICK" ] )
   cf.insert_link( "link_2", "One_Step",         [ moisture_class.check_update_flag ] )
   cf.insert_link( "link_4", "Reset", [] )


   cf.define_chain("update_hour_readings",True)
   cf.insert_link( "link_1", "WaitEvent",    [ "HOUR_TICK" ] )
   cf.insert_link( "link_2", "One_Step",         [ moisture_class.hour_update ] )
   cf.insert_link( "link_4", "Reset", [] )


  
   cf.define_chain("update_day_readings",True)
   cf.insert_link( "link_1", "WaitEvent",    [ "DAY_TICK" ] )
   cf.insert_link( "link_2", "One_Step",         [ moisture_class.day_update ] )
   cf.insert_link( "link_4", "Reset", [] )
 
 
 
 

#  cf.define_chain("watch_dog_thread",True)
#  cf.insert_link( "link_1","WaitTod",["*","*","*",30 ])
#  cf.insert_link( "link_2","One_Step",[ wc.pat_wd ])
#  cf.insert_link( "link_3","WaitTod",["*","*","*",55 ])
#  cf.insert_link( "link_4","Reset",[])  


  #
  # Executing chains
  #

   cf.execute()


