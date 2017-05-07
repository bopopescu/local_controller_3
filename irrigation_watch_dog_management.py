import py_cf
  
class PLC_WATCH_DOG():

   def __init__(self, redis_handle, graph_management, instrument,remote_classes ):
       self.redis_handle           = redis_handle
       self.gm                     = graph_management
       self.instrument             = instrument
       self.remote_classes         = remote_classes
       slave_nodes  = gm.match_relationship(  "REMOTE_UNIT", json_flag = True)
       self.slave_dict    = {}
       

       for i in slave_nodes:
           class_inst     = remote_classes.find_class( i["type"] )
           self.slave_dict[i["name"]] = { "modbus_address": i["modbus_address"], "type":i["type"], "class":class_inst }
      

   def read_wd_flag( self, cf_handle, chainObj, parameters,event ):
       #print "read watch dog flag"
       for i,value in self.slave_dict.items():
           
           if  hasattr( value["class"],"m_tags") == False:
               
               continue
           
           modbus_address   = (value["modbus_address"])
           
           if value["class"].m_tags.has_key("read_wd_flag"):
               
               action_function  =self.slave_dict[i]["class"].m_tags["read_wd_flag"]
               try:      
                   wd_flag   = action_function( modbus_address, [] )  
                   #print "wd_flag",wd_flag
                   if wd_flag != 0:
                       
                       event         = {}
                       event["name"] = "BAD_WD_FLAG"
                       event["data"] = modbus_address
                       cf_handle.event_queue.append(event)
               except:
                   #print "send event b"
                   event         = {}
                   event["name"] = "NO_MODBUS_RESPONSE"
                   event["data"] = modbus_address
                   cf_handle.event_queue.append(event)
       return "DISABLE"
    
   def write_wd_flag( self, cf_handle, chainObj, parameters,event ):
       #print "write wd flag"
       for i,value in self.slave_dict.items():
           
           if  hasattr( value["class"],"m_tags") == False:
               
               continue
           
           modbus_address   = (value["modbus_address"])
           
           if value["class"].m_tags.has_key("write_wd_flag"):
               
               action_function  =self.slave_dict[i]["class"].m_tags["write_wd_flag"]
               try:      
                   action_function( modbus_address, [] )  
               except:
                   #print "send event b",i
                   event         = {}
                   event["name"] = "NO_MODBUS_RESPONSE"
                   event["data"] = modbus_address
                   cf_handle.event_queue.append(event)
                   raise
       return "DISABLE"
     
   def read_mode_switch( self, cf_handle, chainObj, parameters,event ):
       #print "read_mode_switch"
       for i,value in self.slave_dict.items():
           
           if  hasattr( value["class"],"m_tags") == False:
               
               continue
           
           modbus_address   = (value["modbus_address"])
           
           if value["class"].m_tags.has_key("read_mode_switch"):
               
               action_function  =self.slave_dict[i]["class"].m_tags["read_mode_switch"]
               try:      
                   mode             = action_function( modbus_address, [] )  
                   if mode != 1:
                       #print "send event a",i
                       event         = {}
                       event["name"] = "BAD_MODE_SWITCH"
                       event["data"] = modbus_address
                       cf_handle.event_queue.append(event)
               except:
                   #print "send event b",i
                   event         = {}
                   event["name"] = "NO_MODBUS_RESPONSE"
                   event["data"] = modbus_address
                   cf_handle.event_queue.append(event)
       return "DISABLE"

   def read_mode( self, cf_handle, chainObj, parameters,event ):
       #print "read mode"  
       for i,value in self.slave_dict.items():
           
           if  hasattr( value["class"],"m_tags") == False:
               
               continue
           
           modbus_address   = (value["modbus_address"])
           
           if value["class"].m_tags.has_key("read_mode"):
               
               action_function  =self.slave_dict[i]["class"].m_tags["read_mode"]
               try:      
                   mode             = action_function( modbus_address, [] )  
                   if mode != 1:
                       #print "send event a"
                       event         = {}
                       event["name"] = "BAD_MODE"
                       event["data"] = modbus_address
                       cf_handle.event_queue.append(event)
               except:
                   print "send event b"
                   event         = {}
                   event["name"] = "NO_MODBUS_RESPONSE"
                   event["data"] = modbus_address
                   cf_handle.event_queue.append(event)
       return "DISABLE"

def construct_chains( plc_watch_dog ):
   cf.define_chain("plc_watch_dog", True ) #TBD
   #cf.insert_link( "link_1",  "Log",        ["plc watch dog thread"] )
   cf.insert_link( "link_2",  "One_Step",   [ plc_watch_dog.read_mode ] )
   cf.insert_link( "link_3",  "One_Step",   [ plc_watch_dog.read_mode_switch ] ) 
   cf.insert_link( "link_4",  "One_Step",   [ plc_watch_dog.read_wd_flag  ]      )
   cf.insert_link( "link_5",  "One_Step",   [ plc_watch_dog.write_wd_flag ]      )
   cf.insert_link( "link_1", "WaitTime",    [ 30,0,0,0] ) # wait 1 seconds
   cf.insert_link( "link_7",  "Reset",    [] )



if __name__ == "__main__":
   import construct_graph
   import io_control.new_instrument
   import redis
   import io_control.construct_classes

   #plc_watch_dog_interface   = io_control_backup.irrigation_ctl.WatchDogControl( remote_devices, plc_map )
   #plc_watch_dog             = PLC_WATCH_DOG( redis, alarm_queue,plc_watch_dog_interface )

   gm = construct_graph.Graph_Management("PI_1","main_remote","LaCima_DataStore")
  
   data_store_nodes = gm.find_data_stores()
   io_server_nodes  = gm.find_io_servers()
  
   # find ip and port for redis data store
   data_server_ip   = data_store_nodes[0]["ip"]
   data_server_port = data_store_nodes[0]["port"]
   redis_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 12 )


   io_server_ip     = io_server_nodes[0]["ip"]
   io_server_port   = io_server_nodes[0]["port"]
   # find ip and port for ip server

   instrument  =  io_control.new_instrument.Modbus_Instrument()

   instrument.set_ip(ip= io_server_ip, port = int(io_server_port)) 
   remote_classes = io_control.construct_classes.Construct_Access_Classes(instrument)
   plc_monitoring_class =  PLC_WATCH_DOG( redis_handle, gm, instrument, remote_classes )

   cf = py_cf.CF_Interpreter()


   construct_chains( plc_monitoring_class )
   


   
   cf_environ = py_cf.Execute_Cf_Environment( cf )
   cf_environ.execute()
   
  

       
     

      

