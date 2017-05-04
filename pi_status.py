
#
# File: pi_status.py

import os

class PI_Status( object ):

   def __init__( self, redis_handle ):
       self.redis_handle = redis_handle

   def measure_temperature( self, tag, value, parameters ):
      temp = os.popen("vcgencmd measure_temp").readline()
      temp = temp.replace("temp=","").replace("'C\n","")
      temp = float(temp)
      temp = (9.0/5.0*temp)+32.
      return temp


   def measure_disk_space( self, tag, value, parameters  ):
       f = os.popen("df")
       data = f.read()
       f.close()
       lines = data.split("\n")
       
       return_value = []
       for i in range(0,len(lines)):
           if i == 0:
               continue
           fields = lines[i].split()
          
           if len(fields) > 3:
              percent = float( fields[2] )/float( fields[1] )
              temp_value = { "disk": fields[0], "used":percent }  
              return_value.append( temp_value )
       return return_value

   def measure_processor_ram( self ,tag, value, parameters ):
       f = os.popen("free -m")
       data = f.read()
       f.close()
       lines = data.split("\n")
       return_value = []
       fields = lines[1].split()
       percent = float(fields[2])/float(fields[1])
       temp_value = { "Component": fields[0], "used":percent }
       return_value.append(temp_value )
       fields = lines[3].split()
       percent = float(fields[2])/float(fields[1])
       temp_value = { "Component": fields[0], "used":percent }
       return_value.append(temp_value )
       return return_value

   def measure_processor_load( self ,tag, value, parameters  ):
       headers = [ "USER","PID","%CPU","%MEM","VSZ","RSS","TTY","STAT","START","TIME","COMMAND", "PARAMETER1", "PARAMETER2" ]
       f = os.popen("ps -aux | grep python")
       data = f.read()
       f.close()
       lines = data.split("\n")
       return_value = []
       for i in range(0,len(lines)):
           print lines[i]
           if i == 0:
               continue
           fields = lines[i].split()
           temp_value = {}
           if len(fields) <= len(headers):
               for i in range(0,len(fields)):
                   temp_value[headers[i]] = fields[i]
               return_value.append( temp_value )
       return return_value

   def log_redis_info( self, tag,value,parameters):
        return self.redis_handle.info()

if __name__ == "__main__":

   import time
   import construct_graph 
   import redis

   gm = construct_graph.Graph_Management("PI_1","main_remote","LaCima_DataStore")
  
   data_store_nodes = gm.find_data_stores()
   io_server_nodes  = gm.find_io_servers()
  
   # find ip and port for redis data store
   data_server_ip   = data_store_nodes[0]["ip"]
   data_server_port = data_store_nodes[0]["port"]
   redis_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 12 )


   x = PI_Status(redis_handle)
   #print x.measure_temperature( None,None,None)
   #print x.measure_disk_space(None,None,None)
   #print x.measure_processor_load( None,None,None)
   #print x.measure_processor_ram( None,None,None)
   print x.log_redis_info( None,None,None )


