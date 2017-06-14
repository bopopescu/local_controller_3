import json as simplejson
import json
import time
import os

from urlparse import *
from shutil import *
import urllib

from load_files import *

import redis
from types import *

import base64






class Save_Schedule:
 
   def __init__( self,  redis_handle ):
       self.redis_handle = redis_handle
       self.app_files    = APP_FILES( redis_handle )


   def find_index( self,  name, ref_sched_data ):
      
        for i in range(0, len(ref_sched_data) ):
           
           if ref_sched_data[i]["name"] == name:
              return i
        return None

  


   def save_schedule( self, schedule_data ):
       name = schedule_data["name"]
       ref_sched_data  = self.app_files.load_file( "sprinkler_ctrl.json" )

       index = self.find_index( name, ref_sched_data )
       
       if index != None:
            ref_sched_data[ index ] = schedule_data
       else:
            ref_sched_data.append( schedule_data)
  
       self.app_files.save_file( "sprinkler_ctrl.json",ref_sched_data)
      

   def save_link_file( self, schedule, schedule_data ):
       link_data = {}
       link_data["bits"] = {'1':'C201', '3':'DS2', '2':'C2'}
       link_data["schedule"] = []
       for step in range(0,len(schedule_data["controller_pins"] ) ):
           valve_data = schedule_data["controller_pins"][step]
           time       = schedule_data["steps"][step]
           valve_return = []
           for valve_index in range(0,len(valve_data)):
                 valve_return.append( [ valve_data[valve_index][0], [ valve_data[valve_index][1] ] , time ])
           link_data["schedule"].append( valve_return )
       print "save link",schedule
       self.app_files.save_file( schedule+".json", link_data )

   def delete_link_file( self, schedule ):
       try:
         self.app_files.delete_file( schedule+".json" )
       except:
          pass
   def delete_schedule( self, schedule ):
       
       ref_sched_data  = self.app_files.load_file( "sprinkler_ctrl.json" )
       index = self.find_index( schedule, ref_sched_data )
       
       if index != None:

            del ref_sched_data[ index ] 
            self.app_files.save_file( "sprinkler_ctrl.json" , ref_sched_data )
           




class Statistics_Module:

   def __init__( self ,redis_handle):
         self.redis_handle            = redis_handle
         self.schedule_data           = self.get_schedule_data()
         self.sensor_names            = self.get_flow_rate_sensor_names()
         self.conversion_rate         = self.get_conversion_rates()
         self.flow_rate_sensor_names  = self.get_flow_rate_sensor_names()
         self.save_schedule           = Save_Schedule( redis_handle )

   def save_schedule_data( self,action,schedule, data ):

      
       if action == "delete":
           self.save_schedule.delete_schedule( schedule )
           self.save_schedule.delete_link_file( schedule )
           del self.schedule_data[schedule]
       else:
           self.schedule_data = data
           self.save_schedule.save_link_file( schedule, data[schedule] )
           self.save_schedule.save_schedule( data[schedule]  )
      
        






   
   
   def get_schedule_data( self, *args):
     data           = self.redis_handle.hget("FILES:APP","sprinkler_ctrl.json")
     data           = base64.b64decode(data)
     sprinkler_ctrl = json.loads(data)
     
     returnValue = {}
     for j in sprinkler_ctrl:
         print j["name"]
         data           = self.redis_handle.hget("FILES:APP",j["link"])
         data           = base64.b64decode(data)
         temp = json.loads(data)
         
         j["step_number"], j["steps"], j["controller_pins"] = self.generate_steps(temp)
         
         returnValue[j["name"]] = j
     return returnValue

   def generate_steps( self, file_data):
       returnValue = []
       controller_pins = []
       if file_data["schedule"] != None:
         schedule = file_data["schedule"]
         
         for i  in schedule:
             returnValue.append(i[0][2])
             temp = []
             for l in  i:
	       temp.append(  [ l[0], l[1][0] ] )
             controller_pins.append(temp)
  
  
       return len(returnValue), returnValue, controller_pins

   def get_flow_limit_values( self, step_number, sensor_name, schedule_name ):
       
      
       key = "log_data:flow_limits:"+schedule_name+":"+sensor_name
       data = self.redis_handle.get( key )
       if data == None :
            returnValue = self.generate_default_limits( step_number )
       else:
          temp = json.loads(data)
          if (data == None) or (len(temp) != step_number):
              returnValue = self.generate_default_limits( step_number )
          else:
              returnValue = temp
       return returnValue 
       
   def get_flow_limit_values_a( self, step_number, sensor_name, schedule_name ):
       key = "log_data:flow_limits:"+schedule_name+":"+sensor_name
       data = self.redis_handle.get( key )
       if data == None :
            returnValue = self.generate_default_limits( step_number )
       else:
          temp = json.loads(data)
          if (data == None) or (len(temp) != step_number):
              returnValue = self.generate_default_limits( step_number )
          else:
              returnValue = temp
       return returnValue 

   def save_all_flow_limit_data( self, limit_function, limit_data, *args):

       temp = self.schedule_data
       
       for i in temp.keys():
           sched_dat    = temp[i]
           for step_number in range(0,len(sched_data.steps)):
               sensor_list = self.get_flow_rate_sensor_names()
               for sensor_name in sensor_list:
                  save_flow_limit_values( step_number, sensor_name,sched_dat["name"], limit_data[sched_data][step_number][sensor_name] )
                    
   

   def find_sensor_id( self, sensor_name ):
     
       try:
           sensor_id = self.statistics_module.sensor_names.index( sensor_name )
       except:
           sensor_id = 0
       return sensor_id  
     


   def process_flow_limit_values( self, sensor_name, schedule, data):
        sensor_id = self.find_sensor_id( sensor_name )
        inverse_conversion_rate = 1./self.conversion_rate[sensor_id]
        corrected_data = self.assemble_corrected_data( data, inverse_conversion_rate )
        self.save_flow_limit_values( sensor_name, schedule, corrected_data )
   
       


   def save_flow_limit_values( self, sensor_name, schedule_name, data ):
       json_data = json.dumps(data)
       key = "log_data:flow_limits:"+schedule_name+":"+sensor_name
       self.redis_handle.set( key , json_data )
       
     
 


   def assemble_corrected_data( self, data, conversion_rate):
       corrected_data = []
       for i in data:

           corrected_data.append( {"limit_avg":float(i)*conversion_rate, "limit_std" : 0 } )
       return corrected_data 
       

   def generate_default_limits( self, step_number ):
       returnValue = []
       for i in range(0,step_number):
           temp = {}
           temp["limit_avg"] = 0
           temp["limit_std"] = 0
           returnValue.append(temp)
    
       return returnValue

   def get_flow_rate_sensor_names( self, data_file_path = "../system_data_files/global_sensors.json" ):
       return_data = []
       ###---
       data           = self.redis_handle.hget("FILES:SYS","global_sensors.json")
       data           = base64.b64decode(data)
       temp           = json.loads(data)

       for i in temp:
           
           return_data.append(i[0])

       return return_data


   def get_conversion_rates( self, data_file_path = "../system_data_files/global_sensors.json" ):
       return_data = []
       ###---
       data           = self.redis_handle.hget("FILES:SYS","global_sensors.json")
       data           = base64.b64decode(data)
       temp           = json.loads(data)
   
       for i in temp:
           
           return_data.append(i[3])

       return return_data

   def get_average_flow_data( self,  step_number, sensor_name, schedule_name ):  
       returnValue = []
       for i in range(0,step_number):
           key = "log_data:flow:"+schedule_name+":"+str(i+1)
           value_array = []
           for j in range(0,10):
               composite_string = self.redis_handle.lindex(key,j)
               try:
                   composite_object = json.loads( composite_string )
 	           value = composite_object["fields"][sensor_name]["average"] 
               
               except:
                   value = 0
               value_array.append(value)
           returnValue.append(value_array)   
       return returnValue

   def get_average_flow_data_queue( self,  step_id, sensor_name, schedule_name ):  
       
       
       key = "log_data:flow:"+schedule_name+":"+str(step_id+1)
       value_array = []
       number = self.redis_handle.llen(key)
       
       for j in range(0,number):
           composite_string = self.redis_handle.lindex(key,j)
           try:
               composite_object = json.loads( composite_string )
               
 	       value =  [ composite_object["time"], composite_object["fields"][sensor_name]["average"] ]
           except:
               value = [ 0,0]
           value_array.append(value)
       
       value_array.reverse()    
       return value_array




   def get_current_data( self, step_number, schedule_name ):
       returnValue = []
       for i in range(0,step_number):
           key = "log_data:coil:"+schedule_name+":"+str(i+1)
           value_array = []
           for j in range(0,10):
               composite_string = self.redis_handle.lindex(key,j)
              
               try:
                   composite_object = json.loads( composite_string )
 	           value = composite_object["fields"]["coil_current"]["average"] 
               
               except:
                   value = 0
               value_array.append(value)
           returnValue.append(value_array)   
       return returnValue


   def save_all_current_limit_data( self, limit_function, limit_data, *args):

       temp = self.schedule_data
       
       for i in temp.keys():
           sched_dat    = temp[i]
           for step_number in range(0,len(sched_data.steps)):
                  save_current_limit_values( step_number, sched_dat["name"], limit_data[sched_data][step_number] )

   def process_current_limit_values( self,  schedule, data):
       key = "log_data:coil_limits:"+schedule
       corrected_data = self.assemble_corrected_data( data, 1. )
       self.redis_handle.set( key , json.dumps(corrected_data) )

      
   

   def get_all_current_limit_data( self, limit_function, *args):

       temp = self.schedule_data
       return_value = {}
       for i in temp.keys():
           sched_return = []
           sched_dat    = temp[i]
           for step_number in range(0,len(sched_data.steps)):
               step_return.push( get_current_limit_values(step_number, sched_dat["name"] ) )
                    
           return_value[sched_dat["name"]] = sched_return
       return return_value

 

   def get_current_limit_values( self,  step_number, schedule_name ):
       key = "log_data:coil_limits:"+schedule_name
       data = self.redis_handle.get( key )
       if data == None:
	   returnValue = self.generate_default_limits( step_number )
       else:
           returnValue = json.loads(data)
       return returnValue

   def get_time_index_flow( self,time_id, step_id, sensor_name, schedule_name ):
       key = "log_data:flow:"+schedule_name+":"+str(step_id+1)
       returnValue = []
       count = 0
       for i in range(time_id,time_id+5):
           composite_string = self.redis_handle.lindex(key,i)
           
           if composite_string == None:
	       returnValue.append([])
           else:
	       try:
	           composite_object = json.loads( composite_string )
                   
	           temp = {}
                   
	           if type( composite_object["fields"]) is   DictType:
                        
                       returnValue.append(composite_object["fields"][sensor_name])
                       
                   else:
                       returnValue.append(None)
                       
	       except:
	           returnValue.append(None)
                   
	   count = count +1
       

       #print "return Value",returnValue
       return returnValue

   def get_average_current_data_queue( self, step_id,  schedule_name ):
      
       key = "log_data:coil:"+schedule_name+":"+str(step_id+1)
       value_array = []
       number = self.redis_handle.llen(key)
       
       for j in range(0,number):
           composite_string = self.redis_handle.lindex(key,j)
           try:
               composite_object = json.loads( composite_string )
               
 	       value =  [ composite_object["time"], composite_object["fields"]["coil_current"]["average"] ]
           except:
               value = [ 0,0]
           value_array.append(value)
       
       value_array.reverse()  
       
       return value_array


   def get_time_index_current( self, time_id, step_id,  schedule_name ):
       key = "log_data:coil:"+schedule_name+":"+str(step_id+1)
       returnValue = []
       count = 0
       for i in range(time_id,time_id+5):
           composite_string = self.redis_handle.lindex(key,i)
           
           if composite_string == None:
	       returnValue.append([])
           else:
	       try:
	           composite_object = json.loads( composite_string )
                   
	           temp = {}
                   
	           if type( composite_object["fields"]) is   DictType:
                        
                       returnValue.append(composite_object["fields"]["coil_current"])
                       
                   else:
                       returnValue.append(None)
                       
	       except:
	           returnValue.append(None)
                   
	   count = count +1
       

       #print "return Value",returnValue
       return returnValue

   def get_total_flow_data( self,  step_number, sensor_name, schedule_name ):     
   
       returnValue = []
       key = "log_data:flow:"+schedule_name+":"+str(step_number+1)
       index = self.redis_handle.llen(key)
       for i in range(0,index):
           composite_string = self.redis_handle.lindex(key,i)
           if composite_string == None:
	       pass # do nothing
       	   
           else:
	       try:
	           composite_object = json.loads( composite_string )
                   returnValue.append( [ composite_object["time"], composite_object["fields"][sensor_name]["total"] ] )
               except:
                   pass # do nothing

       returnValue.reverse() 
       return returnValue

   def get_controller_list( self ):
       base64_object     = self.redis_handle.get(  "SPRINKLER_RESISTANCE_DICTIONARY")
       json_string       = base64.b64decode(base64_object)
       resistance_dictionary = json.loads(json_string)
       
       controllers = resistance_dictionary.keys()
       controllers.sort()
       return controllers
   

