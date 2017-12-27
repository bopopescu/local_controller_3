#
#  The purpose of this file is to load a system configuration
#  in the graphic data base
#

import json

import redis
from . import farm_template_py3
import time
'''
class Linux_System(object):

get "LINUX_HOUR_ACQUISTION" to get routing key
get LINUX_HOUR_ELEMENT to get fields
these Hour element become nodes 


'''
class Error_Object(object):

   def __init__(self):
       pass
       
   def construct_object(self,name=None, redis_key=None,callback_fn = None):
   
       self.default_time_out = 7*24*3600 # one_week
       temp = {}
      
       temp["name"] = name
       temp["redis_key"] = redis_key       
      
       temp["error_time"]  = self. default_time_out
       temp["time_stamp"] = time.time()
       temp["status"] = "GREEN"
       if callback_fn != None:
          temp = callback_fn(temp)
       
       
       return temp
 

   def construct_mapping_rom(self):
       self.mapping_array = {}
       temp = {}
       temp["RED"] = self.__error_update__
       temp["YELLOW"] = self.__error_update__
       temp["GREEN"] = self.__error_update__
       self.mapping_array["RED"] = temp
       temp = {}
       temp["RED"] = self.__conditional_update__
       temp["YELLOW"] = self.__error_update__
       temp["GREEN"] = self.__error_update__
       self.mapping_array["YELLOW"] = temp
       temp = {}
       temp["RED"] = self.__conditional_update__
       temp["YELLOW"] = self.__conditional_update__
       temp["GREEN"] = self.__error_update__
       self.mapping_array["GREEN"] = temp
 
   def monitor_time(self,data):
     
       if data["status"] != "GREEN":
           time_stamp = time.time()
           if time_stamp > data["time_stamp"]+data["error_time"] :
               data["status"] = "GREEN"
       return data        
               
   def log_error(self,data,status):
       status = status.upper()
       if status not in ["RED","YELLOW","GREEN"]:
          raise ValueError("error status is: "+str(status)+'  Should be: ["RED","YELLOW","GREEN"]')
       ref_status = data["status"]
       temp = self.mapping_array[status]
       error_fn = temp[ref_status]
       data = error_fn(data,status)
       return data   
       
   def __error_update__(self,data,status):
       data["time_stamp"] = time.time()
       data["status"] = status
       return data
       
   def __conditional_update__(self,data,status):
       time_stamp = time.time()
       if time_stamp > data["time_stamp"]+data["error_time"] :
           data = self.error_update(data,status)
       return data  


class Modbus_Class(object):

   def __init__(self,cf,gm,label):
       self.error_object = Error_Object()
       self.cf = cf
       self.label = label
       self.logging_key ="QUEUES:MODBUS_LOGGING"
       self.basic_key = "QUEUES:MODBUS_LOGGING:HOUR_DATA:BASIC_STATS"
       self.remote_key = "QUEUES:MODBUS_LOGGING:HOUR_DATA:REMOTES:"
       self.instant_key = "QUEUES:MODBUS_LOGGING:INSTANT_DATA:BASIC_STATS"
       self.remotes_key = []
 
      
       remote_lists = gm.match_terminal_relationship("REMOTE_UNIT",None)
       address_list = []
       for i in remote_lists:
          address_list.append(i["modbus_address"])
       temp = []

       for i in address_list:
          temp.append(int(i))
       temp.sort()
       address_list = []
       for i in temp:
          address_list.append(str(i))
          
       self.address_list = address_list
          

          
       self.properties = self.generate_properties()
       
 
 
   def generate_properties(self):
       return_value = []
       return_value.append(self.error_object.construct_object(name="BASIC_STATS",redis_key = self.basic_key))
       return_value.append(self.error_object.construct_object(name= "INSTANT_STATS",redis_key = self.instant_key))
       for i in self.address_list:
            return_value.append(self.error_object.construct_object(name= "REMOTE_STATS_"+str(i),redis_key = self.remote_key+str(i)))  
       return return_value

       
   def generate_graph(self):
       for i in self.properties:
          cf.add_info_node( self.label,i["name"],properties=i , json_flag = True) 
 
 
 
 
class Process_Class(object):
 
   def __init__(self,cf,label,process_list):
       self.cf           = cf
       self.error_object = Error_Object()
       self.process_list = process_list
       self.properties = self.generate_properties()
       self.label = label 
       
       
   def generate_properties(self):
      return_value = []
      for i in self.process_list:
         i.strip()
         temp = {}
         temp_list = i.split("/")
         name = temp_list[-1]
         temp_name = name.split(".")
         self.error_file = "/tmp/"+temp_name[-0]
         temp = self.error_object.construct_object(name= name,callback_fn=self.callback)   
         return_value.append(temp)
      return return_value
 
   def callback(self,data):
       data["error_file"] = self.error_file
       return data
       
 
   def generate_graph(self):
       for i in self.properties:
          cf.add_info_node( self.label,i["name"],properties=i , json_flag = True)
       
class Sub_Process_Class(Process_Class):

   def __init__(self,cf,label,parent_process, sub_process_list):
       self.parent_process = parent_process
       super(Sub_Process_Class,self).__init__(cf,label,sub_process_list)

          
   def callback(self,data):
       data["error_file"] = self.error_file
       data["parent_process"] = self.parent_process
       return data
         
        


if __name__ == "__main__" :
   print( "constructing graph")
   cf = farm_template_py3.Construct_Farm(db=13)
   gm = farm_template_py3.Graph_Management("" , "","",db = 14 )
   
   #
   #
   # Construct Systems
   #
   #
   cf.construct_system("LaCima Operations")

   #
   #
   # Construction Sites for LaCima
   #
   #

   cf.construct_site( name="LaCima",address="21005 Paseo Montana Murrieta, Ca 92562")

   # we are going to construct the data store here
   cf.add_header_node("SYSTEM_MONITORING")
   cf.add_header_node("MODBUS_MONITORING")
   modbus_class = Modbus_Class(cf,gm,"MODBUS_RESOURCE")
   modbus_class.generate_graph()
   cf.end_header_node("MODBUS_MONITORING")
   cf.add_header_node("LINUX_MONITORING")
   cf.end_header_node("LINUX_MONITORING")
   cf.add_header_node("PROCESS_MONITORING")
   process_class = Process_Class(cf,"PROCESS",["process_control_py3"])
   process_class.generate_graph()
   cf.add_header_node("SUB_PROCESS_MONITORING")
   temp = gm.match_terminal_relationship("PROCESS_CONTROL",None)[0]
   "PROCESS_CONTROL""PROCESS_CONTROL"
   sub_process_list = temp["command_string_list"]
  
   sub_process_class = Sub_Process_Class(cf,"SUB_PROCESS","process_control_py3",sub_process_list)
   sub_process_class.generate_graph()
   cf.end_header_node("SUB_PROCESS_MONITORING")
   
   
   cf.end_header_node("PROCESS_MONITORING")
   
   
   
   cf.end_header_node("SYSTEM_MONITORING")
   cf.end_site()
   cf.end_system()
   cf.check_namespace()
   cf.store_keys()

