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

   def match_relationship( self, query_string, json_flag = False ):
      keys =  self.qc.match_relationship( query_string ) 
      return_value = []
      for i in keys:
         data = self.redis_handle.hgetall(i)
         #print "data",data
         temp = {}
         for j in data.keys():
            #print j, data[j]
            try:
               if json_flag == True:
	            temp[j] = json.loads(data[j])
               else:
                 temp[j] = data[j]
            except:
               temp[j] = data[j]
         return_value.append(temp)
      return return_value

   def find_relationship_keys( self, query_string, json_flag = True ):
      return self.qc.match_relationship( query_string ) 


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
   cf = Construct_Farm(redis_handle,common)
   
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
                      "Bank 10C Watermark 8 inch","Bank 10C Resistive 8 inch", "Bank 10C Resistive 18 inch", "empty",
                      "Bank 10D Watermark 8 inch", "Bank 10D Resistive 8 inch","Bank 10D Resistive 18 inch","empty" ]

   depth_map = [8,8,18,0,8,8,18,0,8,8,18,0,8,8,18,0]
   cf.add_moisture_sensor_store( "moisture_1", "Moisture Sensor for Irrigation Bank10", description_map=description_map, 
                                  depth_map= depth_map, update_time= 15 )

   cf.add_status_store( "status_store", "status_store" )
   
   cf.end_moisture_store()
   '''
   access_codes = {
      "messo_eto": {"api-key":"8b165ee73a734f379a8c91460afc98a1"  ,"url":"http://api.mesowest.net/v2/stations/timeseries?" ,  "station":"SRUC1" },
      "messo_precp":{"api-key":"8b165ee73a734f379a8c91460afc98a1"  ,"url":"http://api.mesowest.net/v2/stations/precip?" ,  "station":"SRUC1" },
      "cimis_eto":{ "api-key":"e1d03467-5c0d-4a9b-978d-7da2c32d95de"  , "url":"http://et.water.ca.gov/api/data"     , "station":179 },
      "cimis_spatial":{ "api-key":"e1d03467-5c0d-4a9b-978d-7da2c32d95de"  , "url":"http://et.water.ca.gov/api/data"     , "longitude":  -117.299459  ,"latitude":33.578156  }
      }
   '''
   #altitude = 2400
   #cf.add_eto_setup_code(access_codes = access_codes, altitude = altitude)
   #cf.start_info_store()
   #cf.add_eto_store()
   #cf.add_header_node( "ETO_STORES")

   properties = { "api-key":"e1d03467-5c0d-4a9b-978d-7da2c32d95de"  , "url":"http://et.water.ca.gov/api/data"     , "longitude":  -117.299459  ,"latitude":33.578156  }
   properties["altitude"] = 2400
   properties["measurement_tag"] = "CIMIS_SATELLITE_ETO"

   cf.add_info_node( "ETO_ENTRY","ETO_CIMIS_SATELLITE",properties=properties, json_flag=True)

   properties = { "api-key":"e1d03467-5c0d-4a9b-978d-7da2c32d95de"  , "url":"http://et.water.ca.gov/api/data"     , "station":62 }
   properties["altitude"]        = 2400
   properties["measurement_tag"] = "CIMIS_ETO"
   properties["list_length"]     = 100
   cf.add_info_node( "ETO_ENTRY","ETO_CIMIS",properties=properties, json_flag=True)

   properties = {"api-key":"8b165ee73a734f379a8c91460afc98a1"  ,"url":"http://api.mesowest.net/v2/stations/timeseries?" ,  "station":"SRUC1" }
   properties["altitude"] = 2400
   properties["measurement_tag"] = "CIMIS_MESO"
   properties["list_length"]     = 100

   cf.add_info_node( "ETO_ENTRY","Santa_Rosa_RAWS",properties=properties, json_flag=True)
   

   properties = {"api-key":"8b165ee73a734f379a8c91460afc98a1"  ,"url":"http://api.mesowest.net/v2/stations/timeseries?" ,  "station":"SRUC1" }
   properties["altitude"] = 2400
   properties["measurement_tag"] = "HYBRID_SITE"
   properties["list_length"]     = 100

   cf.add_info_node( "ETO_ENTRY","LaCima_Ranch",properties=properties, json_flag=True)
   cf.end_header_node()

   cf.add_header_node("DAILY_RAIN_STORES")

   properties = { "api-key":"e1d03467-5c0d-4a9b-978d-7da2c32d95de"  , "url":"http://et.water.ca.gov/api/data"     , "station":62 }
   properties["measurement_tag"] = "CIMIS_RAIN"
   properties["list_length"]     = 100

   cf.add_info_node( "RAIN_ENTRY","CIMIS_RAIN",properties=properties, json_flag=True)

   properties = {"api-key":"8b165ee73a734f379a8c91460afc98a1"  ,"url":"http://api.mesowest.net/v2/stations/precip?" ,  "station":"SRUC1" }
   properties["measurement_tag"] = "MESO_RAIN"
   properties["list_length"]     = 100

   cf.add_info_node( "RAIN_ENTRY","MESO_RAIN",properties=properties, json_flag=True)

   cf.end_header_node()
   cf.add_info_node("INTEGRATED_RAIN_ESTIMATE","INTEGRATED_RAIN_ESTIMATE",properties={"list_length":300},json_flag = True)
   cf.add_info_node("INTEGRATED_ETO_ESTIMATE","INTEGRATED_ETO_ESTIMATE",properties={"list_length":300},json_flag = True )

 
   cf.add_header_node( "DATA_ACQUISITION")


    ###### need to add function_key
   cf.add_header_node( "MINUTE_ACQUISITION")
   cf.add_info_node( "MINUTE_DATA","CONTROLLER_CURRENT",properties={"units":"mAmps"}, json_flag=True)
   cf.add_info_node( "MINUTE_ELEMENT","IRRIGATION_VALVE_CURRENT",properties={"units":"mAmps"}, json_flag=True)
   cf.add_header_node("FLOW_METER_LIST")
   cf.add_info_node( "FLOW_METER","MAIN_FLOW_METER",properties={"units":"GPM" }, json_flag=True)
   cf.end_header_node()
   cf.add_info_node( "MINUTE_ELEMENT","WELL_CONTROLLER_OUTPUT",properties={"units":"AMPS"}, json_flag = True )
   cf.add_info_node( "MINUTE_ELEMENT","WELL_CONTROLLER_INPUT", properties={"units":"AMPS" }, json_flag = True)
   cf.add_info_node( "MINUTE_ELEMENT","FILTER_PRESSURE", properties = { "units":"PSI" }, json_flag = True )
   cf.add_info_node( "MINUTE_ELEMENT", "WELL_PRESSURE", properties = {"units":"PSI" }, json_flag = True )
   cf.add_info_node( "MINUTE_VALUE", "MINUTE_VALUE", properties = {} , json_flag= True)
   cf.add_info_node( "MINUTE_LIST", "MINUTE_LIST",properties =  { "LIST_LENGTH" :10000} , json_flag = True) # about 1 week of data
   cf.end_header_node()


   cf.add_header_node( "HOUR_ACQUISTION")
   cf.add_info_node( "HOUR_ELEMENT","MODBUS_STATISTICS",properties={"units":"Counts"},json_flag=True )
   cf.add_info_node( "HOUR_ELEMENT","PI_TEMPERATURE",properties={"units":"Deg F" }, json_flag = True )
   cf.add_info_node( "HOUR_VALUE", "HOUR_VALUE", properties = {} , json_flag= True)
   cf.add_info_node( "HOUR_LIST", "MINUTE_LIST",properties =  { "LIST_LENGTH" :300} , json_flag = True) # about 1 week of data
   cf.end_header_node()


   cf.add_header_node( "DAILY_ACQUISTION")
   cf.add_info_node( "HOUR_VALUE", "HOUR_VALUE", properties = {} , json_flag= True)
   cf.add_info_node( "HOUR_LIST", "HOUR_LIST",properties =  { "LIST_LENGTH" :100} , json_flag = True) # about 3 months of data
   cf.end_header_node()




   cf.end_header_node()
   cf.end_info_store()   

  

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


   cf.add_ntpd_server("LaCima")
   cf.add_info_node( "CIMIS_EMAIL","CIMIS_EMAIL",properties =  { "imap_username" :'lacima.ranch@gmail.com',"imap_password" : 'Gr1234gfd'} , json_flag = True)


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


