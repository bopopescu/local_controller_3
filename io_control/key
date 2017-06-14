'''
**  file: io_controllers.py
**
**
**
'''

import redis
import time
import json
import redis

class Generate_IO_System:

   def __init__( self , slave_types ):
       self.slave_types = set(slave_types)
       self.redis_handle =  redis.StrictRedis(host='localhost', port=6379, db=3)
       self.redis_handle.delete("IO_CONTROLLER_HASH")
       self.redis_handle.delete("SLAVE_REMOTE_HASH")   
       self.io_controller = None

   def add_io_controller( self, name, ip,  port = 5005 ):

       ip = str(ip)
       data = {}
       data["name"] = name
       data["ip"]   = ip
       data["port"] = port
       self.redis_handle.hmset("IO_CONTROLLER_HASH", {ip:json.dumps(data)})
       self.io_controller_ip = ip


   def add_slave( self, name, type, slave_address):
       if type not in self.slave_types:
           raise ValueError("improper type "+type)
       data = {}
       data["ip"]     = self.io_controller_ip
       data["name"]   = name
       data["type"]   = type
       data["slave_address"] = slave_address
       remote_name = "IP_ADDRESS:"+self.io_controller_ip+":SLAVE_ADDRESS:"+str(slave_address)+":TYPE:"+type
       self.redis_handle.hmset("SLAVE_REMOTE_HASH",{remote_name:json.dumps(data)})

   def list_controller_ip( self ):
       return self.redis_handle.hkeys("IO_CONTROLLER_HASH" )


   def list_slaves_by_fields( self, fields ):

       return_value = []
       temp1 = self.redis_handle.hkeys("SLAVE_REMOTE_HASH")  
       for i in temp1:
          temp2_string = self.redis_handle.hget("SLAVE_REMOTE_HASH", i)
          temp2_dict = json.loads(temp2_string)
          
          for index, value in fields.items():
               
               if temp2_dict[index] != value:
                   break
          else:
              return_value.append(i)
       return return_value

   def list_all_slaves( self ):
       return self.redis_handle.hkeys("SLAVE_REMOTE_HASH")   


if __name__ == "__main__":

   generate = Generate_IO_System(["CLICK","MOISTURE"])
   generate.add_io_controller("192.168.1.82","192.168.1.82" )
   print generate.list_controller_ip()
   generate.add_slave("Main","CLICK",100)
   generate.add_slave("Satellite_1","CLICK",125)
   generate.add_slave("Satellite_2","CLICK",170)
   generate.add_slave("Moisture_1","MOISTURE",40)
   print generate.list_all_slaves()
   print generate.list_slaves_by_fields( {"type":"CLICK","ip":"192.168.1.82"})
   print generate.list_slaves_by_fields( {"type":"MOISTURE"})


