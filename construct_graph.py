# file build system
#
#  The purpose of this file is to load a system configuration
#  in the graphic data base
#

import json

import redis
from redis_graph.redis_graph_common   import Redis_Graph_Common
from redis_graph.redis_graph_populate import Build_Configuration
from farm_template        import Construct_Farm
from redis_graph.redis_graph_query   import Query_Configuration
import copy
 
class Graph_Management():

   def __init__( self , controller_name, io_server_name, data_store_name ):
      self.redis_handle  = redis.StrictRedis( host = "localhost", port=6379, db = 15 )   
      self.common = Redis_Graph_Common( self.redis_handle)
      self.qc = Query_Configuration( self.redis_handle, self.common )
      
      self.controller_name = controller_name
      self.io_server_name  = io_server_name
      self.data_store_name = data_store_name

   def match_relationship( self, query_string, json_flag = True ):
      keys =  self.qc.match_relationship( query_string ) 
      return_value = []
      for i in keys:
         data = self.redis_handle.hgetall(i)

         return_value.append(data)
      return return_value

   def find_remotes( self  ):
      keys = self.qc.match_label_property_generic( "UDP_IO_SERVER", "name", self.io_server_name, "REMOTE" )
      return_value = {}
      for i in keys:
         data = self.redis_handle.hgetall(i)
         return_value[data["name"]]= data
      return return_value


   def find_remotes_by_function( self,  function ):
       keys = self.qc.match_relationship_property_specific( "UDP_IO_SERVER", "name",  self.io_server_name, "REMOTE", "function", function)
       return_value = {}
       for i in keys:
          data = self.redis_handle.hgetall(i)
          return_value[data["name"]]= data
       return return_value

   def find_data_store_by_function(self, function):
      keys = self.qc.match_label_property_generic( "DATA_STORE", "name", self.data_store_name, function )
      return_value = {}
      for i in keys:
         data = self.redis_handle.hgetall(i)
         return_value[data["name"]]= data
      return return_value

   def find_data_stores( self ):
       keys = self.qc.match_relationship("DATA_STORE")
       return_value = {}
       for i in keys:
           data = self.redis_handle.hgetall(i)
           return_value[data["name"]] = data
       return return_value 

   def find_io_servers( self ):
       keys = self.qc.match_relationship("UDP_IO_SERVER")
       return_value = {}
       for i in keys:
           data = self.redis_handle.hgetall(i)
           return_value[data["name"]] = data
       return return_value 



   def get_value( self, key ):
      return self.redis_handle.hgetall(key["namespace"])

   def convert_namespace( self, name ):
       name = name.replace(chr(0x82),"[")
       name = name.replace(chr(0x83),"~")
       name = name.replace(chr(0x84),"]")
       name = name.replace(chr(0x85),":")
       return name

if __name__ == "__main__" :
   redis_handle  = redis.StrictRedis( host = "localhost", port=6379, db = 15 )   
   common = Redis_Graph_Common( redis_handle)


   qc = Query_Configuration( redis_handle, common )
   bc = Build_Configuration(redis_handle,common)
   cf = Construct_Farm(bc)
   
   #
   #
   # Construct Systems
   #
   #
   cf.construct_system("LaCima Operations")

   #
   #
   # Construction Sites for LaCima
   #
   #

   cf.construct_site( name="LaCima",address="21005 Paseo Montana Murrieta, Ca 92562")

   # we are going to construct the data store here
   cf.add_redis_data_store(name="LaCima_DataStore", ip="192.168.1.84" )  # want a fresh data store
 
   cf.start_moisture_store()
   description_map = ["Bank 10A Watermark 8 inch","Bank 10A Resistive 8 inch", "Bank 10A Resistive 18 inch", "empty",
                      "Bank 10B Watermark 8 inch", "Bank 10B Resistive 8 inch","Bank 10B Resistive 18 inch","empty",
                      "empty", "empty","empty","empty",
                      "empty", "empty","empty","empty"]

   depth_map = [8,8,18,0,8,8,18,0,0,0,0,0,0,0,0,0]
   cf.add_moisture_sensor_store( "moisture_1", "Moisture Sensor for Irrigation Bank10", description_map=description_map, 
                                  depth_map= depth_map, update_time= 15 )

   cf.add_status_store( "status_store", "status_store" )
   cf.end_moisture_store()
      



   cf.end_redis_data_store()

   cf.add_udp_io_sever(name="main_remote", ip = "192.168.1.82", remote_type= "UDP", port=5005   )
   cf.add_rtu_interface(name = "rtu_2",protocol="modbus_rtu",baud_rate=38400 )
   cf.add_remote(  name="satellite_1",modbus_address=100,type = "click_44", function="irrigation" )
   cf.add_remote(  name="satellite_2",modbus_address=125 ,type="click_22", function="irrigation" )
   cf.add_remote(  name="satellite_3",modbus_address=170,type="click_22", function="irrigation" )
   cf.add_remote(  name="moisture_1",modbus_address=40,type="PSOC_4_Moisture", function ="moisture")
   cf.end_rtu_interface()
   cf.end_udp_io_server()




   cf.construct_controller(  name="PI_1", ip = "192.168.1.82",type="PI")
   cf.end_controller()

   cf.construct_web_server( name="main_web_server",url="https://192.168.1.84" )
  
   cf.add_rabbitmq_command_rpc_queue("LaCima" )
   cf.add_rabbitmq_web_rpc_queue("LaCima")
   cf.add_rabbitmq_event_queue("LaCima")


   cf.add_rabbitmq_status_queue( "LaCima",vhost="LaCima",queue="status_queue",port=5671,server = 'lacimaRanch.cloudapp.net' )

   cf.add_eto_server("LaCima")
   cf.add_ntpd_server("LaCima")
   cf.add_moisture_monitoring("LaCima")
   cf.irrigation_monitoring("LaCima")
   cf.add_device_monitoring("LaCima")
   cf.add_watch_dog_monitoring("LaCima")
   cf.end_site()
   cf.end_system()

   '''
   keys = redis_handle.keys("*")
   
   for i in keys:
      print "+++++++++++++:"
      print i
      temp = i.split( common.sep)
      print len(temp)
      print redis_handle.hgetall(i)
      print "----------------"
   print "lenght",len(keys)
   print "testing query functions"

   print qc.match_labels( "CONTROLLER" ) # match single item
   temp = qc.match_labels( "REMOTE" ) # match single item
   print len(temp),temp

   print len(qc.match_relationship( "CONTROLLER" )) # match single item
   temp = qc.match_relationship( "REMOTE" ) # match single item
   print "single match", len(temp)
   

   temp = qc.match_label_property( "REMOTE", "name", "satellite_1")
   print "specific_match",len(temp)

   temp = qc.match_label_property(  "UDP_IO_SERVER", "name", "main_remote")
   print "specific_match",len(temp)



   temp= qc.match_label_property_specific( "UDP_IO_SERVER", "name", "main_remote", "REMOTE", "name", "satellite_1")
   print "specific property match", len(temp)


   temp = qc.match_label_property_generic(  "UDP_IO_SERVER", "name", "main_remote", "REMOTE" )
   print "general match", len(temp) #temp

   temp= qc.match_relationship_property_specific( "UDP_IO_SERVER", "name", "main_remote", "REMOTE", "name", "satellite_1")
   print "match relationship", len(temp) #temp

   temp = qc.match_relationship_property_generic(  "UDP_IO_SERVER", "name", "main_remote", "REMOTE" )
   print "general match", len(temp) #temp

   '''

   temp = qc.match_label_property_generic(  "UDP_IO_SERVER", "name", "main_remote", "REMOTE" )
   print "general match", len(temp) ,temp

   print "testing class functions"

   graph_management = Graph_Management("PI_1","main_remote","LaCima_DataStore" )
   print graph_management.find_remotes()
   print len(graph_management.find_remotes_by_function( "moisture" ))
   print len(graph_management.find_remotes_by_function( "irrigation"  ))


