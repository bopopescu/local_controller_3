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
          self.kill_process(process_handle)
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
       command_string = "python3   "+command_string
       self.command_string = command_string
       command_list= shlex.split(command_string)

       script_file_list = command_list[1].split("/")
     
       self.script_file_name = script_file_list[-1].split(".")[0]
       temp  = error_directory + "/"+self.script_file_name
       self.error_file = temp+".err"
       self.error_file_rollover = temp +".errr"
       self.error = False
       
   def get_script(self):
       return self.script_file_name
       

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
           print(self.restart_flag)
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
        
       self.startup_list = []
       self.process_hash = {}
       self.process_state = {}
       for command_string in command_string_list:
          temp_class = Manage_A_Python_Process( command_string )
          python_script = temp_class.get_script()
          self.startup_list.append(python_script)
          temp_class.active = False
          self.process_hash[python_script] = temp_class
          
       self.redis_handle.set(self.web_display_list_key,json.dumps(self.startup_list))
       self.update_web_display()
      
       
    

       
   def launch_processes( self,*unused ):
 
     for script in self.startup_list:
        temp = self.process_hash[script]
        if temp.active == False:
            return_value = temp.launch()
            if return_value == False:
                temp.rollover()
                temp.error = True
                return_data = json.dumps({ "script": script, "error_file" : temp.temp.error_file_rollover})
                self.redis_handle.publish(self.error_queue_key,return_data)
            else:
               temp.active = True
               temp.error = False

   
   def monitor( self, *unused ):
     
     for script in self.startup_list:
        temp = self.process_hash[script]
       
        if temp.active == True:
           if temp.monitor() == False:
              self.redis_handle.lpush(self.error_queue_key,{"script":script, "error_file":temp.error_file_rollover})       
     self.update_web_display()
           
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
      print("update_web_display")
      process_state = {}
      for script in self.startup_list:
          
          if self.process_hash[script].active == True:
              process_state[script] = True
          else:
              process_state[script] = False
     
      self.redis_handle.set(self.web_process_data_key,json.dumps(process_state))
      
      
 
 

  


      
   def add_chains(self,cf):

       cf.define_chain("initialization",True)
       cf.insert.one_step(self.launch_processes)
       cf.insert.enable_chains( ["monitor_web_command_queue","monitor_active_processes"] )
       cf.insert.terminate()
   
   
       cf.define_chain("monitor_web_command_queue", False)
       cf.insert.wait_event_count( event = "TIME_TICK", count = 10)
       cf.insert.one_step(self.process_web_queue)
       cf.insert.reset()
       
       cf.define_chain("monitor_active_processes",False)
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
   web_command_queue_key =process_data['web_command_key'] 
   error_queue_key = process_data['error_queue_key']
   command_string_list  = process_data["command_string_list"]
   web_process_data_key = process_data["web_process_data"]
   web_display_list_key = process_data["web_display_list"]
   print(web_process_data_key,web_display_list_key)
   system_control = System_Control(   redis_handle    = redis_handle,
                                      error_queue_key = error_queue_key,
                                      web_command_queue_key = web_command_queue_key,
                                      web_process_data_key = web_process_data_key,
                                      web_display_list_key = web_display_list_key,
                                      command_string_list = command_string_list )

   system_control.add_chains(cf)

   cf.execute()
 
