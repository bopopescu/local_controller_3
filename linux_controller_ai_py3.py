'''
File: linux_controller_ai_py3.py

This module is a standalone processs which does the following actions.

1. Initialization


    
2.  Monitor Modbus Status

3.  Monitor Process Terminations

4.  Monitor Linux System

5.  Monitor_Time_Outs

'''


class Monitoring_Object(object):
'''
  This object is responsible for managing a single information points
'''

   def __init__(self,gm,redis_key):
        self.gm = gm
        self.redis_key = redis_key
        self.monitor_key()
       
       
   def monitor_key():
      # get redis key 
      # assert key is not None
      #
       
       pass


class Modbus_Monitor(object):

   def __init__(self,cf,redis_handle):
        self.cf = cf
        self.redis_handle = redis_handle
        
   def get_statistics(self,*values):
         pass
       
   def construct_chains(self):
       cf.define_chain("init", True)
       cf.insert.enable_chains(["minute_interval"])
       cf.insert.terminate()

       cf.define_chain("minute_interval", True)
       cf.insert.log("minute interval")
       cf.insert.wait_event_count( event = "MINUTE_TICK")
       cf.insert.one_step(self.get_statistics)
       cf.insert.reset()
        
class Process_Termination(object):
 
   def __init__(self,cf,redis_handle):
       self.cf = cf
       self.redis_handle = redis_handle
       
   def monitor_cloud_queue(self,*values):
      pass
   
   def monitor_process_control(self,*values):
      pass
      
   def construct_chains(self):
       cf.define_chain("init", True)
       cf.insert.enable_chains(["minute_interval"])
       cf.insert.terminate()

       cf.define_chain("minute_interval", True)
       cf.insert.log("minute interval")
       cf.insert.wait_event_count( event = "MINUTE_TICK")
       cf.insert.one_step(self.monitor_cloud_queue)
       cf.insert.one_step(self.monitor_process_control)
       cf.insert.reset()
   
class Linux_System(object):

   def __init__(self,cf,redis_handle):
       self.cf = cf
       self.redis_handle = redis_handle
       
   def monitor_system_internals(self,*values):
       pass
      
   def construct_chains(self):
       cf.define_chain("init", True)
       cf.insert.enable_chains(["minute_interval"])
       cf.insert.terminate()

       cf.define_chain("minute_interval", True)
       cf.insert.log("minute interval")
       cf.insert.wait_event_count( event = "MINUTE_TICK")
       cf.insert.one_step(self.monitor_system_internals)
       cf.insert.reset()

 
if __name__ == "__main__":
   import math
   import redis
   import base64
   import json
   from redis_graph_py3 import farm_template_py3
   import datetime
   from   irrigation_control_py3.alarm_queue_py3     import AlarmQueue
   from py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter

   cf = CF_Base_Interpreter()
   gm = farm_template_py3.Graph_Management(
        "PI_1", "main_remote", "LaCima_DataStore")

   
   data_store_nodes = gm.find_data_stores()
   # find ip and port for redis data store
   data_server_ip = data_store_nodes[0]["ip"]
   data_server_port = data_store_nodes[0]["port"]
   # find ip and port for ip server
    
   redis_handle = redis.StrictRedis(
        host=data_server_ip, port=data_server_port, db=12, decode_responses=True)

   mm = Modbus_Monitor(cf,redis_handle)
   pm = Process_Termination(cf,redis_handle)
   lm = Linux_System(cf,redis_handle)
   mm.construct_chains()
   pm.construct_chains()
   lm.construct_chains()
   #cf.execute()
