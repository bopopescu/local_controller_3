import time
import json
import redis
import subprocess
from subprocess import Popen, check_output
import shlex

class Process_Control(object ):

   def __init__(self):
       pass
  
   def run_process_to_completion(self,command_string, shell_flag = False, timeout_value = None):

       try:
          command_parameters = shlex.split(command_string)
          return_value = check_output(command_parameters, stderr=subprocess.STDOUT , shell = shell_flag, timeout = timeout_value)
          return [0,return_value.decode()]
       except subprocess.CalledProcessError as cp:
           print("made it here")
           return [ cp.returncode  , cp.output.decode() ]
       except :
           return [-1,""]
       
   def launch_process(self,command_string,stderr=None,shell=True):
       command_parameters = shlex.split(command_string)
       try:
           process_handle = Popen(command_parameters, stderr=stderr , shell=shell)
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
    
       
class Manage_A_Python_Process(object)

   def __init__(self,parameters):
       command_list = ["/usr/bin/python3"]
       script_file = parameters[0].split("/")
       command = 
          
    
  
 

class System_Control(object):
   def __init__(self):
       pass





if __name__ == "__main__":

   process_control = Process_Control()
   print( process_control.run_process_to_completion("ls *.py",shell_flag=True))
   process_handle = process_control.launch_process("ls ./*.py",shell=True)
   print( process_control.monitor_process(process_handle))
   time.sleep(1)
   print( process_control.monitor_process(process_handle))
   print(process_control.kill_process(process_handle))
   
