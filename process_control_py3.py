import time
import json
import redis
import subprocess
from subprocess import Popen, check_output
import shlex
import os
from py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter
from redis_graph_py3 import farm_template_py3

class Process_Control(object ):

   def __init__(self):
       pass
  
   def run_process_to_completion(self,command_string, shell_flag = False, timeout_value = None):

       try:
          command_parameters = shlex.split(command_string)
          return_value = check_output(command_parameters, stderr=subprocess.STDOUT , shell = shell_flag, timeout = timeout_value)
          return [0,return_value.decode()]
       except subprocess.CalledProcessError as cp:

           return [ cp.returncode  , cp.output.decode() ]
       except :
           return [-1,""]
       
   def launch_process(self,command_string,stderr=None,shell=True):
       command_parameters = shlex.split(command_string)
       try:

           process_handle = Popen(command_parameters, stderr=open(self.error_file,'w' ))
           return [ True, process_handle ]  
       except:
           return [False, None]       
           
      
   
   def monitor_process(self, process_handle):
       returncode = process_handle.poll()
       if returncode == None:
          return [ True, 0]
       else:
          del process_handle
          return [ False, returncode ]
       
   def kill_process(self,process_handle):
      try:
         process_handle.kill()
         del process_handle
      except:
         pass
    
       
class Manage_A_Python_Process(Process_Control):

   def __init__(self,command_string, restart_flag = True,  error_directory = "/tmp"):

       super(Process_Control,self)
       
       self.restart_flag = restart_flag
       self.command_string = command_string
       command_list= shlex.split(command_string)
     
       script_file_list = command_list[1].split("/")
     
       self.script_file_name = script_file_list[-1].split(".")[0]
       temp  = error_directory + "/"+self.script_file_name
       self.error_file = temp+".errr"
       self.error_file_rollover = temp +".errrr"
       temp.error = False
       


   def launch(self):
      temp = self.launch_process(self.command_string, stderr=self.error_file)
      return_value = temp[0]
      self.handle = temp[1]
      return return_value
    
   def monitor(self):
       return_value = self.monitor_process(self.handle)

       if return_value[0] == True:
             return True
       else:
           self.rollover()
           if self.restart_flag == True:
              self.launch()
           return False


   def rollover(self):
        os.system("mv "+self.error_file+"  " +self.error_file_rollover)
           
   def kill(self):
       self.kill_process(self.handle)
       self.rollover()
       
           
       
             
 

class System_Control(object):
   def __init__(self,
               redis_handle,
               error_queue_key,
               web_command_queue_key,
               web_process_data_key,
               web_display_list_key,
               command_string_list ):
               
       self.redis_handle = redis_handle
       self.error_queue_key = error_queue_key
       self.web_command_queue_key = web_command_queue_key
       self.web_process_data_key = web_process_data_key
       self.web_display_list_key = web_display_list_key
       self.command_string_list = command_string_list
        
       self.start_up_list = []
       self.process_hash = {}
       self.process_state = {}
       for command_string in command_list:
          temp_class = Manage_A_Python_Process( command_string )
          python_script = temp_class.get_script()
          self.startup_list.append(python_script)
          temp_class.active = True
          self.process_hash[python_script] = temp_class
          
       self.redis_handle.set(self.web_display_list_key,json.dumps(self.startup_list))
       self.launch_processes()
       self.update_web_display()
       
    

       
   def launch_processes( self ):
     for script in startup_list:
        temp = self.process_hash[script]
        if temp.active == True:
            return_value = temp.launch()
            if return_value[0] == False:
                temp.active = False
                temp.error = True
                return_data = json.dumps({ "script": script, "error_file" : temp.error_file})
                self.redis_handle.publish(self.error_queue_key,return_data)

   
   def monitor( self, process_objects ):
     for script in startup_list:
        temp = self.process_hash[script]
        if temp.active == True:
           if temp.monitor() == False:
              pass #fix this
              

           
   def process_web_queue( self, *unused ):
     
       if self.redis_handle.llen(self.web_command_queue_key) > 0 :
           start_list = []
           kill_list = []
           try:
               data_json = redis_handle.lpop(self.web_command_queue_key)
               self.redis_handle.ltrim(self.web_command_queue_key)
               data = json.loads(data)

               for item in data:
                   if item["active"] == True:
                       start_list.append(item["name"] )
                   else:
                      kill_list.append(item["name"])
               self.execute_web_queue(kill_list,start_list)
           except:
               pass
           self.update_web_display()    
                      

   def execute_web_queue(self,start_list,kill_list):
      for script in kill_list:
         if script in self.process_hash:
            temp_class = self.process_hash[script]
            if temp_class.active == True:
                self.temp_class.kill()
      for script in start_list_list:
         if script in self.process_hash:
            temp_class = self.process_hash[script] 
            if temp_class.active == False:
                self.temp_class.launch()

                
   def update_web_display(self):
      process_state = {}
      for script in self.startup_list:
          if self.process_handle[script].active == True:
              process_state[script] = True
          else:
              process_state[script] = False
      self.redis_handle.set(self.web_command_queue_key,json.dumps(process_state))
      
      
 
 

  


      
   def add_chains(self,cf):

       cf.define_chain("monitor_web_command_queue", True)
       cf.insert.wait_event_count( event = "TIME_TICK", count = 10)
       cf.insert.one_step(self.process_web_queue)
       cf.insert.reset()
       
       cf.define_chain("monitor_active_processes",True)
       cf.insert.wait_event_count( event = "TIME_TICK",count = 10)
       cf.insert.one_step(self.monitor)
       cf.insert.reset()
 



if __name__ == "__main__":
   
   cf = CF_Base_Interpreter()
   gm = farm_template_py3.Graph_Management(
        "PI_1", "main_remote", "LaCima_DataStore")
        
        
   process_data = gm.match_terminal_relationship("PROCESS_CONTROL")[0]
  
   redis_data = process_data["redis"]
   redis_handle = redis.StrictRedis(
        host=redis_data["ip"], port=redis_data["port"], db=redis_data["db"], decode_responses=True)
   web_command_key =process_data['web_command_key'] 
   error_queue_key = process_data['error_queue_key']
   command_string_list  = process_data["command_string_list"]
   web_process_data = process_data["web_process_data"]
   web_display_list = process_data["web_display_list"]
   print(web_command_key,error_queue_key,web_process_data,web_display_list)
   print(command_string_list)
   quit()
   # find process list
   # find redis ip server
   # find process list
   # find error_queue
   # find active queue
   system_control = System_Control( redis_handke, error_queue, web_command_queue, command_string_list )
   system_control.add_chains()
   
   
   # contruct chains
   cf.execute()
 
   '''
   data_store_nodes = gm.find_data_stores()
    # find ip and port for redis data store
    data_server_ip = data_store_nodes[0]["ip"]
    data_server_port = data_store_nodes[0]["port"]
    # find ip and port for ip server
    #print "data_server_ip", data_server_ip, data_server_port
    redis_handle = redis.StrictRedis(
        host=data_server_ip, port=data_server_port, db=12, decode_responses=True)
    eto = construct_eto_instance(gm, redis_handle)
    #
    # Adding chains
    #
    
    add_eto_chains(eto, cf)
    #
    # Executing chains
    #
    
    

  '''
   '''
   process_control = Process_Control()
   print( process_control.run_process_to_completion("ls *.py",shell_flag=True))
   process_handle = process_control.launch_process("ls ./*.py",shell=True)
   print( process_control.monitor_process(process_handle))
   time.sleep(1)
   print( process_control.monitor_process(process_handle))
   print(process_control.kill_process(process_handle))
   '''
   '''
   x = Manage_A_Python_Process("python3 /home/pi/new_python/eto_py3.py")
   print(x.launch())
   for i in range(0,10):
      time.sleep(1)
      print(x.monitor())
   x.kill()
   '''