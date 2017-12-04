
import time
from datetime import datetime

class No_Server_In_Graph(Exception):
    """Base class for exceptions in this module."""
    pass

class Statistic_Handler( object ):
    
    def __init__(self,redis_handle,gm,graph_key, remote_units,modbus_key,logging_queue ):
        self.redis_handle = redis_handle
        self.gm = gm
        self.graph_key = graph_key
        self.remote_units = remote_units
        self.max_queue = 7
        self.time_base = time.time()
        self.modbus_key = modbus_key
        self.logging_queue = logging_queue
        self.initialize_logging_data()
        
        

        
    def initialize_logging_data( self ):
        self.time_stamp = datetime.now()
        self.busy_time = 0
        self.idle_time = 0
        self.message_count = 0
        self.message_loss = 0
        
        self.queue = {}
        for i in range(0,self.max_queue ):
            self.queue[i] = 0
        self.remote_complete = {}
        for i in self.remote_units:
           self.remote_attempted[i] = 0
        for i in self.remote_units:
           self.remote_losses[i] = 0
                
        
    def hour_rollover( self ):
        if self.message_count > 0:
            message_ratio = 100
        else:
            message_ratio = (self.message_count - self.message_loss )/message_count *100
        total_time = self.busy_time + self.idle_time
        if total_time == 0 :
            time_ratio = 100   
        else:
            time_ratio = ( self.busy_time *100)/total_time
        data = {}
        data["message_ratio"] = message_ratio
        data["time_ratio"] = time_ratio
        data["counts"] = self.message_count
        data["losses"] = self.message_loss        
        // store active% messages, losses percent       
        // store depth queue
        // store remote statistics
        self.initialize_logging_data()
        
    def process_null_message( self ):
        temp = time.time()
        delta_t = temp - self.time_base
        self.time_base = temp
        self.idle_time = self.idle_time + delta_t
        if self.datetime.hour != datetime.now().hour():
             self.hour_rollover()
        // update current redis state
        
        
        
    def process_start_message( self , modbus_address ):
        self.message_count += l
        self.start_base = time.time()
        waiting_number = self.redis.llindex( self.modbus_key, 0 )
        if waiting_number >= self.max_queue:
           waiting_number = self.max_queue -1
        self.queue[waiting_number] += 1
        if modbus_address in self.remote_units:
           self.remote_attempted[modbus_address] += 1
        
        
         
    def process_end_messager( self ):
        self.time_base = time.time()
        delta_t = self.time_base - self.start_base
        self.busy += delta_t
        if self.datetime.hour != datetime.now().hour():
             self.hour_rollover()
        // update redis state
        

    def log_bad_message( self, modbus_address ):
        self.message_loss += 1
        if modbus_address in self.remote_units:
            self.remote_losses[modbus_address] += 1
        
    def log_good_message( self, modbus_address ):
        pass

class Modbus_Server( object ):
    
   def __init__( self, redis_handle,msg_handler,redis_rpc_queue , gm, graph_key,modbus_key ):  # fill in proceedures
       self.msg_handler = msg_handler
       self.redis_handle = redis_handle
       self.statistic_handler = Statistic_Handler(redis_handle,gm,graph_key,modbus_key)
       self.redis_rpc_server = Redis_Rpc_Server(redis_handle,redis_rpc_queue, self.process_null_msg, timeout_value = 5 )
       self.redis_rpc_server.register_call_back( modbus_key, self.process_modbus_message)
       self.redis_rpc_server.start()
    
        
   def process_modbus_message( self,parameters ):
       self.statistic_handler.process_start_message(parameters[0])
       
       assert len(parameters) ==1, "rpc server client miss match"
       output_msg ,retries = self.msg_handler.process_msg( input_msg )
       if output_msg == "":
           output_msg = "@"
           self.statistic_handler.log_bad_message( input_msg[0], retries )
       else:
            self.statistic_handler.log_good_message( input_msg[0], retries )
       self.statistic_handler.process_end_message()
       return [output_msg]
        

   def process_null_msg( self ):
       self.statistic_handler.process_null_message()
        
class Setup_Remote_Devices(object):
       def __init__( self, gm ):
           self.gm = gm
            
       def find_server( self, server_name ):
           server_list  = (self.gm.match_terminal_relationship( "UDP_IO_SERVER" ,property_values = {"name":server_name} ))           
           if len(server_list) == 0:
               raise No_Server_In_Graph
       
           return server_list[0]



       def find_serial_links( self, server_name ):
            self.search_nodes =    gm.match_relationship_list ( [["UDP_IO_SERVER",server_name]], starting_set = None, property_values = None, fetch_values = False )
            serial_set = gm.match_terminal_relationship("SERIAL_LINK",starting_set = self.search_nodes)
            return gm.to_dictionary( serial_set, "name", json_flag = False )
   
 
           
       def find_and_register_remotes( self, serial_link ,interface_handler, msg_mgr ):
        
            serial_link["handler"] = interface_handler
            
            name = serial_link["name"]
            serial_search_nodes =    gm.match_relationship_list ( [["SERIAL_LINK",name ]], starting_set = self.search_nodes, property_values = None, fetch_values = False )
            remote_lists = gm.match_terminal_relationship("REMOTE_UNIT",starting_set = serial_search_nodes)
            remote_dict = gm.to_dictionary( remote_lists, "name", json_flag = False)
            for j,k in remote_dict.items():
                 k["interface"] = name
            return remote_dict
            
          

if __name__ == "__main__":
   import   redis
   import   sys 
   import   json
   from   modbus_redis_server_py3.modbus_redis_mgr_py3  import  ModbusRedisServer
   from     modbus_redis_server_py3.rs485_mgr_py3  import RS485_Mgr  
   from    modbus_redis_server_py3.modbus_serial_ctrl_py3  import ModbusSerialCtrl
   from   modbus_redis_server_py3.msg_manager_py3 import MessageManager
   from   redis_support_py3.redis_rpc_server_py3 import Redis_Rpc_Server
   
   from redis_graph_py3.farm_template_py3 import Graph_Management

   server_index = 0
   
   server_name =  sys.argv[1]
   
   gm = Graph_Management("PI_1","main_remote","LaCima_DataStore")
   setup  = Setup_Remote_Devices(gm)
   server_dict = setup.find_server( server_name )
   serial_links      = setup.find_serial_links( server_name )
   
  
   rs485_interface =   RS485_Mgr() 
   msg_mgr = MessageManager()
   redis_handle   =  redis.StrictRedis(  server_dict["ip"] , 6379, server_dict["redis_rpc_db"] )

   for i,item in serial_links.items():
       remote_dict = setup.find_and_register_remotes( item , rs485_interface, msg_mgr )
       temp_dict = {}
       temp_dict[i] = item
       modbus_serial_ctrl  = ModbusSerialCtrl( temp_dict, remote_dict, msg_mgr)
       for j,k in remote_dict.items():
           msg_mgr.add_device( k["modbus_address"], modbus_serial_ctrl )   
       msg_mgr.add_device( 255,    redis_handle) 
        
   print(msg_mgr.ping_devices([100]))
   
   Modbus_Server( redis_handle,msg_mgr, server_dict["redis_rpc_key"], gm, graph_key = "blank for now",modbus_key = "modbus_stream" )
    
   