import json


from redis_graph.redis_graph_populate import Build_Configuration
from redis_graph.redis_graph_common import Redis_Graph_Common
#import copy

class Construct_Farm():

   def __init__( self, bc):
      self.bc = bc # Build configuration in graph_functions

   def construct_system( self,name,properties={}):
       properties["name"] = name
       self.bc.construct_node( push_namespace = True,  relationship="SYSTEM", label = "SYSTEM", name = name, 
          properties=properties)
       
   def end_system( self):
       self.bc.pop_namespace()

   def construct_site( self,name, address, properties={}):
       properties["name"] = name
       properties["address"] = address
       self.bc.construct_node(  push_namespace=True,relationship="SITE", label="SITE", name=name, 
               properties =properties)

   def end_site( self ):
      self.bc.pop_namespace()

   def add_redis_data_store( self, name, ip, port=6379, properties = {} ):
       
       properties["ip"] = ip
       properties["port"] = port
       self.bc.construct_node( push_namespace=True,relationship="DATA_STORE", label="DATA_STORE", name=name,
                               properties= properties )
   def start_moisture_store( self ):
       self.bc.construct_node( push_namespace=True,relationship="MOISTURE_STORE", label="MOISTURE_STORE", name="MOISTURE_STORE",
                               properties= {} )

   def end_moisture_store( self ):
      self.bc.pop_namespace()

      
   def add_moisture_sensor_store( self, name, description, description_map, depth_map, update_time ):
       properties = {}
       properties["description"] = description
       properties["description_map"] = description_map
       properties["update_time"] = update_time
       properties["depth_map"] = depth_map
       self.bc.construct_node( push_namespace=True,relationship="MOISTURE_DATA", label="MOISTURE_DATA", name=name,
                               properties= properties )
   
 
   def end_redis_data_store( self):
       self.bc.pop_namespace()

   def add_udp_io_sever(self, name, ip,remote_type, port, properties={} ):
       properties["name"]=name
       properties["ip"] = ip
       properties["remote_type"] = remote_type
       properties["port"] = port
       return self.bc.construct_node(  push_namespace=True,relationship="UDP_IO_SERVER", 
               label="UDP_IO_SERVER", name=name, properties = properties )


   def end_udp_io_server(self ):
       self.bc.pop_namespace()


   def add_rtu_interface(self, name ,protocol, baud_rate, properties={} ):
       properties["name"] = name
       properties["protocol"]= protocol
       properties["baud_rate"] = baud_rate
       return self.bc.construct_node(  push_namespace=True,relationship="RTU_INTERFACE", 
                 label="RTU_INTERFACE", name=name,properties = properties)

   def end_rtu_interface( self ):
       self.bc.pop_namespace()



   def add_remote( self, name,modbus_address,type, function, properties = {}):

       properties["name"]           = name
       properties["modbus_address"] = modbus_address
       properties["type"]           = type
       properties["function"]       = function
       self.bc.construct_node(  push_namespace=True,relationship="REMOTE", label="REMOTE", name=name, 
               properties = properties )


   def construct_controller( self,name, ip,type,properties={} ):
       properties["name"] = name
       properties["ip"]   = ip
       self.bc.construct_node(  push_namespace=True,relationship="CONTROLLER", label="CONTROLLER", name=name, 
               properties = properties)


   def end_controller( self ):
       self.bc.pop_namespace()

   def start_service( self, properties = {} ):
       self.bc.construct_node(  push_namespace=TRUE,relationship="SERVICES", label="SERVICES", name=name, 
               properties = properties)


   def construct_web_server( self, name,url,properties = {} ):
       properties["name"]  = name
       properties["url"]   = url
       self.bc.construct_node(  push_namespace=False,relationship="WEB_SERVER", label="WEB_SERVER", name=name, 
               properties = properties)

   def add_rabbitmq_command_rpc_queue( self,name, properties = {} ):
       properties["name"]  = "COMMAND_RPC_QUEUE"
       
       self.bc.construct_node(  push_namespace=False,relationship="COMMAND_RPC_QUEUE", label="COMMAND_RPC_QUEUE", 
                                name=name, properties = properties)

   def add_rabbitmq_web_rpc_queue( self,name, properties = {} ):
       properties["name"]  = "WEB_RPC_QUEUE"
       
       self.bc.construct_node(  push_namespace=False,relationship="WEB_RPC_QUEUE", label="WEB_RPC_QUEUE", 
                                name=name, properties = properties)

   def add_rabbitmq_event_queue( self,name, properties = {} ):
       properties["name"]  = "EVENT_QUEUE"
       
       self.bc.construct_node(  push_namespace=False,relationship="RABBITMQ_EVENT_QUEUE", label="RABBITMQ_EVENT_QUEUE", 
                                name=name, properties = properties)


   def add_ntpd_server( self,name, properties = {} ):
       properties["name"]  = "NTPD_SERVER"
       
       self.bc.construct_node(  push_namespace=False,relationship="ETO_SERVER", label="NTPD_SERVER", 
                                name=name, properties = properties)


   def add_eto_server( self,name, properties = {} ):
       properties["name"]  = "ETO_SERVER"
       
       self.bc.construct_node(  push_namespace=False,relationship="ETO_SERVER", label="ETO_SERVER", 
                                name=name, properties = properties)

   def add_linux_server_monitor( self, name,properties = {} ):
       properties["name"]  = "Linux Server Monitor"
       
       self.bc.construct_node(  push_namespace=False,relationship="LINUX_SERVER_MONITOR", label="LINUX_SERVER_MONITOR", 
                                name=name, properties = properties)

   def add_schedule_monitoring( self, name,properties = {} ):
       properties["name"]  = "NTPD_SERVER"
       
       self.bc.construct_node(  push_namespace=False,relationship="NTPD_SERVER", label="NTPD_SERVER", 
                                name=name, properties = properties)



   def add_moisture_monitoring( self, name, properties = {} ):
       properties["name"]  = "NTPD_SERVER"
       
       self.bc.construct_node(  push_namespace=False,relationship="NTPD_SERVER", label="NTPD_SERVER", 
                                name=name, properties = properties)

   def irrigation_monitoring( self, name,properties = {} ):
       properties["name"]  = "IRRIGATION_MONITOR"
       
       self.bc.construct_node(  push_namespace=False,relationship="IRRIGATION_MONITOR", label="IRRIGATION_MONITOR", 
                                name=name, properties = properties)

   def add_device_monitoring( self, name, properties = {} ):
       properties["name"]  = "DEVICE_MONITOR"
       
       self.bc.construct_node(  push_namespace=False,relationship="DEVICE_MONITOR", label="DEVICE_MONITOR", 
                                name=name, properties = properties)

   def add_process_monitoring( self,name, properties = {}  ):
       properties["name"]  = "PROCESS_MONITOR"
       
       self.bc.construct_node(  push_namespace=False,relationship="PROCESS_MONITOR", label="PROCESS_MONITOR", 
                                name=name, properties = properties)
   def add_watch_dog_monitoring( self,name, properties = {}  ):
       properties["name"]  = "WATCH_DOG_MONITORING"
       
       self.bc.construct_node(  push_namespace=False,relationship="WATCH_DOG_MONITORING", label="WATCH_DOG_MONITORING", 
                                name=name, properties = properties)


   def add_io_collection( self, name, properties = {} ):
       properties["name"]  = "IO_COLLECTION"
       
       self.bc.construct_node(  push_namespace=False,relationship="PROCESS_MONITOR", label="PROCESS_MONITOR", 
                                name=name, properties = properties)

   def add_local_ai( self, name, properties = {} ):
       properties["name"]  = "LOCAL_AI"
       
       self.bc.construct_node(  push_namespace=False,relationship="PROCESS_MONITOR", label="PROCESS_MONITOR", 
                                name=name, properties = properties)

   


