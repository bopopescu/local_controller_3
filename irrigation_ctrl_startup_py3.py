




if __name__ == "__main__":
   import time
   import redis
   print("made it here")

   from redis_graph_py3.farm_template_py3 import Graph_Management 
   from irrigation_control_py3.misc_support_py3 import IO_Control
   from   io_control_py3 import construct_classes_py3
   from   io_control_py3 import new_instrument_py3


   gm =Graph_Management("PI_1","main_remote","LaCima_DataStore")

   data_store_nodes = gm.find_data_stores()
   io_server_nodes  = gm.find_io_servers()
  
   # find ip and port for redis data store
   data_server_ip   = data_store_nodes[0]["ip"]
   data_server_port = data_store_nodes[0]["port"]
   redis_new_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 12 )
   redis_old_handle  = redis.StrictRedis( host = '192.168.1.84', port=6379, db = 0 )


   
   io_server_ip     = io_server_nodes[0]["ip"]
   io_server_port   = io_server_nodes[0]["port"]
   instrument = new_instrument_py3.Modbus_Instrument()
   remote_classes = construct_classes_py3.Construct_Access_Classes(io_server_ip,io_server_port)
   io_control  = IO_Control(gm,remote_classes, redis_old_handle,redis_new_handle, instrument)
