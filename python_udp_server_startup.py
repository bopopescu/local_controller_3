
if __name__ == "__main__":
  import   json
  
  from     data_management.configuration import *
  import   python_udp_serial_server.modbus_redis_mgr
  import   python_udp_serial_server.rs485_mgr   
  import   python_udp_serial_server.modbus_serial_ctrl
  import   python_udp_serial_server.msg_manager
  import   python_udp_serial_server.python_udp_server

  msg_mgr         =  python_udp_serial_server.msg_manager.MessageManager()
  redis_handler   =  python_udp_serial_server.modbus_redis_mgr.ModbusRedisServer(msg_mgr)

  #rs485_interface_1 = python_udp_serial_server.rs485_mgr.RS485_Mgr()
  rs485_interface_2 = python_udp_serial_server.rs485_mgr.RS485_Mgr()

  #server_1_serial_interfaces[ "rtu_1" ]["handler"]  = rs485_interface_1 
  server_1_serial_interfaces[ "rtu_2" ]["handler"]  = rs485_interface_2 
 

  modbus_serial_ctrl                = python_udp_serial_server.modbus_serial_ctrl.ModbusSerialCtrl( server_1_serial_interfaces, server_1_remote_devices, msg_mgr)

  for i,j in server_1_remote_devices.items():
     msg_mgr.add_device( j["parameters"]["address"], modbus_serial_ctrl )

  msg_mgr.add_device( 255,    redis_handler) # This is for local server functions

  print msg_mgr.ping_devices( [31] )
  print msg_mgr.ping_devices( [100] )
  print msg_mgr.ping_all_devices()

  udp_server = python_udp_serial_server.python_udp_server.UDP_Server()
  udp_server.process_msg(msg_mgr)


