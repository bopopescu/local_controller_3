if __name__ == "__main__":
   import   sys
   import   json
   import   modbus_redis_server_py3.modbus_redis_mgr_py3
   import   modbus_redis_server_py3.rs485_mgr_py3   
   import   modbus_redis_server_py3.modbus_serial_ctrl_py3
   import   modbus_redis_server_py3.msg_manager_py3
   
   from redis_graph_py3.farm_template_py3 import Graph_Management

   server_index = 0
   
   server_name =  sys.argv[1]
   
   gm = Graph_Management("PI_1","main_remote","LaCima_DataStore")
   #  get redis handler
   #  get serial links
   #  # get  units
   temp_sets = (gm.match_relationship( "UDP_IO_SERVER" )) 
   print(list(temp_sets))
   server_dict = gm.to_dictionary( list(temp_sets), "UDP_IO_SERVER" , json_flag = True)
   server = server_dict[server_name]
   
   
   print(server)
   quit()
   serial_set = gm.match_terminal_relationship("SERIAL_LINK",starting_set = temp_sets)
   serial_link= {}
   for i in serial_set:
       serial_link[i["name"]] = i
   #print("serial_link",serial_link)
 
    
  #match_terminal_relationship( self, relationship, label= None , starting_set = None,property_values = None, data_flag = True )  
   
   
   '''
   # Cheating here only assuming one udp io server and one serial link
   udp_io_server = gm.match_relationship("UDP_IO_SERVER")[0]
   temp_link   = gm.match_relationship("SERIAL_LINK")[0]
   rs485_interface =  python_udp_serial_server_py3.rs485_mgr.RS485_Mgr() 
   temp_link["handler"] = rs485_interface
   serial_link = {}
   serial_link[temp_link["name"]] = temp_link  
 

   temp_remote_units  = gm.match_relationship("REMOTE_UNIT")
   remote_units = {}
   for i in temp_remote_units:
     i["interface"] = temp_link["name"]
     remote_units[i["name"]] = i

   serial_link = {}
   serial_link[temp_link["name"]] = temp_link  
   
   msg_mgr         =  python_udp_serial_server.msg_manager.MessageManager()
   print( "temp_link",temp_link)
   redis_host      =  udp_io_server["redis_host"]
   redis_db        =  int(udp_io_server["redis_db"])
   redis_handler   =  python_udp_serial_server.modbus_redis_mgr.ModbusRedisServer( message_handler= msg_mgr, host = "localhost" , redis_db = redis_db )


   modbus_serial_ctrl  = python_udp_serial_server.modbus_serial_ctrl.ModbusSerialCtrl( serial_link, remote_units, msg_mgr)

 
   for i,j in remote_units.items():
       msg_mgr.add_device( j["modbus_address"], modbus_serial_ctrl )



   msg_mgr.add_device( 255,    redis_handler) # This is for local server function
   '''