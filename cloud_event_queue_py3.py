#
#  File: cloud_event_queue_py3
#  This file has two purposes   
#  1.  Called as a main file  with Two parameters
#      A.  event
#      B.  process 
#      Store action in queue for pickup by cloud server
#  2.  Called as a package.
#      Used to store and action into a queue for pickup by cloud server
#
#  Need to straight out concepts for queues and add to the queue




import time
import json
import base64
import redis
import sys

class Cloud_Event_Queue():
   def __init__(self,redis_handle):
        self.redis_handle = redis_handle

   def store_event_queue( self, event, data,status ="RED" ):
          log_data = {}
          log_data["event"] = event
          log_data["data"]  = data
          log_data["time"]  = time.time()
          log_data['status'] = status
          json_data = json.dumps(log_data)
          
          json_data = base64.b64encode(json_data.encode())
          self.redis_handle.lpush( "QUEUES:CLOUD_ALARM_QUEUE", json_data)
          self.redis_handle.ltrim(  "QUEUES:CLOUD_ALARM_QUEUE", 0,800)
          self.redis_handle.lpush( "QUEUES:SYSTEM:PAST_ACTIONS", json_data)
          self.redis_handle.ltrim(  "QUEUES:SYSTEM:PAST_ACTIONS", 0,800)
          

if __name__ == "__main__":

   from   redis_graph_py3 import farm_template_py3
   graph_management = farm_template_py3.Graph_Management("PI_1","main_remote","LaCima_DataStore")
   data_store_nodes =graph_management.find_data_stores()
  
   # find ip and port for redis data store
   data_server_ip   = data_store_nodes[0]["ip"]
   data_server_port = data_store_nodes[0]["port"]
   redis_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 12, decode_responses=True)
   cloud_event_queue = Cloud_Event_Queue( redis_handle )
   event   =  sys.argv[1]
   process =  sys.argv[2]
   print( "event",event,"process",process )
   data = { "action":"reboot" ,"process":process }
   cloud_event_queue.store_event_queue( event,data )
   redis_handle.hincrby("PROCESS_REBOOTS", process )    
