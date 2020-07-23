# This is the System State Modules
#
#
#
import json as simplejson
import json
import time
import os
import cherrypy
from urlparse import *
from shutil import *
import urllib
from cherrypy.lib.httputil import parse_query_string

import redis
import base64

redis_handle_15 = redis.StrictRedis(host='localhost', port=6379, db=15)
mode_string = [ 
                  "This should not happen",
                  "OFFLINE",
                  "QUEUE_SCHEDULE",
                  "QUEUE_SCHEDULE_STEP",
                  "QUEUE_SCHEDULE_STEP_TIME",
                  "CLEAN_FILTER",
                  "OPEN_MASTER_VALVE",
                  "CLOSE_MASTER_VALVE",
                  "RESTART_PROGRAM",
                  "RESET_SYSTEM"  ,
                  "CHECK_OFF",
                  "SHUT_DOWN",
                  "TURN_ON",
                  "SKIP_STATION"
                 ]

class System_state_modules:


  def __init__(self, module_dictionary ):
    module_dictionary["redis_get_status.html"] = self.redis_get_status
    module_dictionary["get_flow_sensor_name.html"] = self.get_flow_sensor_name
    module_dictionary["get_irrigation_queue.html"] = self.get_irrigation_queue
    module_dictionary["load_controller_pins.html"] = self.load_controller_pins
    module_dictionary["mode_request.html"] = self.mode_request_data
    module_dictionary["schedule_data.html"] = self.schedule_data
    module_dictionary["mode_change.html"] = self.change_mode
    module_dictionary["controller_pin_turn_off.html"] = self.pin_off
    module_dictionary["controller_pin_turn_on.html"] = self.pin_on
    module_dictionary["change_rain_flag.html"] = self.change_rain_flag  
    module_dictionary["change_eto_flag.html"] = self.change_eto_flag  
    module_dictionary["rain_flag.html"] =  self.get_rain_flag
    module_dictionary["eto_flag.html"] =   self.get_eto_flag 
    module_dictionary["get_queue_entry.html"] = self.get_queue_entry
    module_dictionary["delete_queue_element.html"] = self.delete_queue
    module_dictionary["get_eto_entries.html"] = self.get_eto_entries
    module_dictionary["save_eto_data.html"] = self.save_eto_data
    module_dictionary["flow_sensor_name.html"] = self.flow_sensor_name
    module_dictionary["get_flow_queue.html"] = self.get_queue
    module_dictionary["recent_plc.html"] = self.recent_plc
    module_dictionary["recent_coil.html"] = self.recent_coil
    module_dictionary["start_time_update.html"] = self.start_time_update
    module_dictionary["run_time_update.html"] = self.update_run_time
    module_dictionary["delete_schedule.html"] = self.delete_schedule
    module_dictionary["insert_schedule.html"] = self.insert_schedule
    module_dictionary["copy_schedule.html"] = self.copy_schedule 
    module_dictionary["change_schedule.html"] = self.change_schedule
    module_dictionary["schedule_entry.html"] = self.schedule_entry
    module_dictionary["load_valve_groups.html"] = self.load_valve_groups
    module_dictionary["get_cleaning_interval.html"] = self.get_cleaning_interval
    module_dictionary["set_cleaning_interval.html"] = self.set_cleaning_interval
    module_dictionary["set_max_flow_rate_cut_off.html"]  = self.set_max_flow_rate_cut_off
    module_dictionary["get_max_flow_rate_cut_off.html"]  = self.get_max_flow_rate_cut_off


  def get_max_flow_rate_cut_off(self, url_list, redis_handle, cherrypy ):

     temp = redis_handle.get( "max_flow_rate_cutoff")
     if temp == None:
        max_flow_rate_cutoff = 0
     else:
        max_flow_rate_cutoff = float(temp)
 

     temp = redis_handle.get( "max_flow_rate_time")
     if temp == None:
        max_flow_rate_time = 0
     else:
        max_flow_rate_time = float(temp)
     temp = json.dumps([ max_flow_rate_cutoff, max_flow_rate_time ] )
     return temp


  def set_max_flow_rate_cut_off(self, url_list, redis_handle, cherrypy ):
     json_object = cherrypy.request.params["JSON"]
     redis_handle.set("max_flow_rate_cutoff",int(json_object[0]))
     redis_handle.set("max_flow_rate_time",int(json_object[1]))
     return json.dumps("SUCCESS")


  def set_cleaning_interval(self, url_list, redis_handle, cherrypy ):
     json_object = cherrypy.request.params["JSON"]
     json_object = float( json_object )
     redis_handle.set("cleaning_interval",json_object)
     return json.dumps("SUCCESS")



  def get_cleaning_interval(self, url_list, redis_handle, cherrypy ):
     temp = redis_handle.get( "cleaning_interval")
     if temp == None:
        temp = 0
     else:
        temp = float(temp)
     temp = json.dumps(temp)
     return temp



  def redis_get_status(self, url_list, redis_handle, cherrypy ):
      return_data = {}

      return_data["controller_time_stamp"]  = redis_handle.get("sprinkler_time_stamp")
      return_data["flow_rate"]              = redis_handle.get( "global_flow_sensor")
      return_data["op_mode"]                = redis_handle.get( "sprinkler_ctrl_mode")
      return_data["schedule"]               = redis_handle.get( "schedule_name" )
      return_data["step"]                   = redis_handle.get( "schedule_step")
      return_data["time_of_step"]           = redis_handle.get( "schedule_time_max" )
      return_data["current_duration"]       = redis_handle.get( "schedule_time_count")
      return_data["derating_factor"]        = redis_handle.get("derating_factor")
      return_data["rain_day"]               = redis_handle.get("rain_day" )
      return_data["pcl_current"]            = redis_handle.get( "plc_current" )
      return_data["coil_current"]           = redis_handle.get( "coil_current" )
      return_data["eto_yesterday"]          = redis_handle.get( "YESTERDAY_ETO" )
      return_data["eto_current"]            = redis_handle.get( "CURRENT_ETO" )
      return_data["eto_main_valve"]       = redis_handle.get("MASTER_VALVE_SETUP")
      return_data["eto_managment_flag"]     = redis_handle.get("ETO_MANAGE_FLAG")
      temp = json.dumps(return_data)
      return temp


  def get_flow_sensor_name( self, url_list, redis_handle, cherrypy ):
     return_data = []
     
     json_data=open("/media/mmc1/system_data_files/global_sensors.json")
     data = json.load(json_data)
     for i in data:
       temp = []
       temp.append(i[0])
       temp.append(i[3])
       return_data.append(temp)
     temp = json.dumps(return_data)
     return temp

  
  # this is generating data for a bar graph program on java script side
  # Essentially what we are doing is generating a list for each schedule
  # unspecified is for a step scheduling
  # We return the cummulative total as a dummy value and a list of 
  # All elements in the queue
  def get_irrigation_queue( self, url_list, redis_handle, cherrypy ):
      return_data = []

      queue_len =  redis_handle.llen("IRRIGATION_QUEUE")
  
      element_list = []
      if queue_len > 0 :
         name      = "unspecified"
         total     = 0
         sub_total = 0
         element_list.append(0) # first element of the list is the total
         state = 0
         for i  in range(0, queue_len):
             data = redis_handle.lindex("IRRIGATION_QUEUE", queue_len - i-1)
         
             if data != None:
	        data = json.loads(data)
                if  data["type"] == "END_SCHEDULE":
	            element = {}
	            name = data["schedule_name"]
	            element["name"]   = name            # this is the name of the bar graph 
	            element["value"]  = element_list    # these are values in a stacked bar graph
	            return_data.append(element)         # adding to return array 
	            element_list = []
	            element_list.append(total)  # first element of the list is the total
	            name = "unspecified"
	        if data["type"] == "IRRIGATION_STEP" :
                
	            total = total + float( data["run_time"])
	            element_list.append( float( data["run_time"] ))
	 
      if len(element_list) > 1 : # we have an element with out an END_SCHEDULE ELEMENT
      	element = {}      # generating a list value for the return_data array
	element["name"]   = name
	element["value"]  = element_list
	return_data.append( element )
    
      json_string = json.dumps(return_data)
      print "json_string--------------->",json_string
      return json_string



  def load_valve_groups( self, url_list, redis_handle, cherrypy ):
     
     json_data=open("/media/mmc1/system_data_files/valve_group_assignments.json")
     print "json data ",json_data
     data = json.load(json_data)
     return json.dumps(data)


  def load_controller_pins( self, url_list, redis_handle, cherrypy ):
     
     json_data=open("/media/mmc1/system_data_files/controller_cable_assignment.json")
     print "json data ",json_data
     data = json.load(json_data)
     return json.dumps(data)
    


  def mode_request_data(self, url_list, redis_handle, cherrypy ):
   
     return_data = {} 
     mode_object = {
       "SHOULD NOT HAPPEN!":0,
       "OFFLINE": 1,
       "QUEUE_SCHEDULE":2,
       "QUEUE_SCHEDULE_STEP":3,
       "QUEUE_SCHEDULE_STEP_TIME":4,
       "CLEAN_FILTER":5,
       "OPEN_MASTER_VALVE":6,
       "CLOSE_MASTER_VALVE":7,
       "RESTART_PROGRAM":8,
       "RESET_SYSTEM":9,
       "CHECK_OFF":10,
       "SHUT_DOWN":11,
       "TURN_ON":12,
       "SKIP_STATION":13
 
      }
      
     temp = redis_handle.get( "sprinkler_ctrl_mode")
     if mode_object.has_key( temp ):
        id = mode_object[temp]
     else:
        id = 0
      
     return_data["mode"] = id
     return_data["step"] = 0
     return_data["run_time"] = 0
     return json.dumps(return_data)



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




  def schedule_data( self, url_list, redis_handle,cherrypy):
    
     json_data=open("/media/mmc1/app_data_files/sprinkler_ctrl.json")
     sprinkler_ctrl = json.load(json_data)
     returnValue = []
     for j in sprinkler_ctrl:
    
         json_data=open("/media/mmc1/app_data_files/"+j["link"])
         temp = json.load(json_data)
         j["step_number"], j["steps"], j["controller_pins"] = self.generate_steps(temp)
         returnValue.append(j)
  

     return json.dumps(returnValue)
 

  def change_mode( self, url_list, redis_handle, cherrypy ):
        
        json_object = cherrypy.request.params["JSON"]
        
        mode = int(json_object["mode"])
        schedule_name =  json_object["schedule_name"]
        step = int(json_object["step"]) 
        run_time =   int(json_object["run_time"])
        if (mode == 0 ) or (mode==1 ) : 
           schedule_name = "offline"
           step = 1
           run_time = 1
           
        temp = {}
        temp["command"] = mode_string[mode]
        temp["schedule_name"]  = schedule_name
        temp["step"]           = step
        temp["run_time"]       = run_time
        scratch = json.dumps(temp)
        redis_handle.lpush("sprinkler_ctrl_queue", base64.b64encode(scratch) )
        return json.dumps("SUCCESS")

    
  def pin_off( self, url_list, redis_handle, cherrypy ):
      
       json_object = cherrypy.request.params["JSON"]       
       temp = {}
       temp["command"]        = "OFFLINE"
       temp["schedule_name"]  = "offline"
       temp["step"]           =  1
       temp["run_time"]       =  1
       scratch = json.dumps(temp)
       redis_handle.lpush("sprinkler_ctrl_queue", base64.b64encode(scratch) )
       return json.dumps("SUCCESS")

  def pin_on( self, url_list, redis_handle, cherrypy ):
       
       json_object = cherrypy.request.params["JSON"]
       self.pin_off( url_list,redis_handle, cherrypy)  # sending offline command before native mode command 
       temp = {}
       temp["command"]        = "NATIVE_SPRINKLER"
       temp["schedule_remote_queue"]  = json_object["controller"] 
       temp["schedule_pin_queue"]           =  json_object["pin"]
       temp["schedule_time_queue"]       =  json_object["run_time"]
       scratch = json.dumps(temp)
       redis_handle.lpush("sprinkler_ctrl_queue", base64.b64encode(scratch) )
       return json.dumps("SUCCESS")



  def change_eto_flag( self, url_list, redis_handle, cherrypy ):
       json_object = cherrypy.request.params["JSON"]
       redis_handle.set( "ETO_MANAGE_FLAG", json_object["eto_flag"] )
       return json.dumps("SUCCESS")
   
     

  def change_rain_flag( self, url_list, redis_handle, cherrypy ):
       json_object = cherrypy.request.params["JSON"]
       redis_handle.set( "rain_day", json_object["rain_flag"] )
       return json.dumps("SUCCESS")

  def get_rain_flag( self, url_list, redis_handle, cherrypy ):
       json_object = {}
       json_object["rain_flag"] = redis_handle.get( "rain_day" )
       return json.dumps( json_object )

  def get_eto_flag( self, url_list, redis_handle, cherrypy ):
       json_object = {}
       json_object["eto_flag"] = redis_handle.get( "ETO_MANAGE_FLAG" )
       return json.dumps( json_object )

  def get_queue_entry( self, url_list, redis_handle, cherrypy ):

     json_object = []
     length =   redis_handle.llen( "IRRIGATION_QUEUE" )
     if length > 0 :
        name      = "unspecified"
        total     = 0
        for i in  range(0, length):
           data = redis_handle.lindex( "IRRIGATION_QUEUE", length-1  -i)
           
           if data != None :
	     data = json.loads(data)
             if  data["type"] == "END_SCHEDULE" :
	        element = {}
	        name = data["schedule_name"]
	        element["name"]   = name
	        element["value"]  = total
	        json_object.append( element)
	        element_list = []
	        element_list.append(total)
	        name = "unspecified"
	        total = 0
	
	     if data["type"] == "IRRIGATION_STEP" :
	       total = total + int( data["run_time"])
	 

      
        if total > 0 :
      	   element = {}    
	   element["name"]   = name
	   element["value"]  = total
	   json_object.append(element)
    

  
     json_string = json.dumps(json_object)
    
     return json_string
 

 
  def delete_queue( self, url_list, redis_handle, cherrypy ):
     json_object = cherrypy.request.params["JSON"]   
     length =   redis_handle.llen( "IRRIGATION_QUEUE" )
     if length > 0 :
          queue_index = 0
          for i in range(0,length):
              queue_index_temp = queue_index
              data = redis_handle.lindex( "IRRIGATION_QUEUE", length - 1 -i)
              if data != None:
	         data = json.loads(data)
                 if  data["type"] == "END_SCHEDULE" :
                   queue_index_temp = queue_index +1 
                 if json_object[ queue_index ] != 0 :
                    redis_handle.lset( "IRRIGATION_QUEUE",length - 1 -i,"NULL/NULL")
                    redis_handle.lrem( "IRRIGATION_QUEUE", 1, "NULL/NULL" )
                      
                
              queue_index = queue_index_temp
        

     json_string = json.dumps("SUCCESS")
     return json_string


  def get_eto_entries( self, url_list, redis_handle, cherrypy ):
  
  
     json_object = []
     
     eto_dictionary = redis_handle.get(  "ETO_RESOURCE_LIST")
     eto_list = eto_dictionary.split(":")
  
     for j in eto_list:
       temp = {}
       temp["name"] = j
       temp["data"]  = redis_handle.get( j )
       json_object.append(temp)
     
     
     json_string = json.dumps( json_object )

     return json_string
 
  
  
  


  def save_eto_data( self, url_list, redis_handle, cherrypy ):
 
     json_object = cherrypy.request.params["JSON"]   
    
     for j in  json_object:
         redis_handle.set(j["name"],j["data"])

     return json.dumps("SUCCESS")
 

  def flow_sensor_name( self, url_list, redis_handle, cherrypy ):

     data =open("/media/mmc1/system_data_files/global_sensors.json")
     flow_sensor_data = json.load(data)
     json_object = []
     for j in flow_sensor_data:
       json_object.append( [ j[0], j[3] ] )
    
     json_string = json.dumps(json_object) 
     
     return json_string



  def get_queue( self, url_list, redis_handle, cherrypy ):

      json_object = {}
      json_string = cherrypy.request.query_string
      
      queue = json_string
      print "-------------------------->",queue,"----------------------------"

      json_object["flow_queue"] = []
      
      length = redis_handle_15.llen("redis_flow_queue_"+queue )
     
      for i in range(0,length): 
        data =  redis_handle_15.lindex("redis_flow_queue_"+queue, i )
        
        json_object["flow_queue"].append(data)
    
      json_string = json.dumps( json_object )
      return json_string
  
  def recent_plc( self, url_list, redis_handle, cherrypy ):

      length = redis_handle_15.llen("plc_current_queue" )
      json_object = {}
      json_object["plc_current_queue"] = []
      for i in range(0,length): 
        data =  redis_handle_15.lindex("plc_current_queue", i )
        
        json_object["plc_current_queue"].append(data)
    
      json_string = json.dumps( json_object )
      return json_string

  def recent_coil( self, url_list, redis_handle, cherrypy ):

      length = redis_handle_15.llen("plc_current_queue" )
      json_object = {}
      json_object["coil_current_queue"] = []
      for i in range(0,length): 
        data =  redis_handle_15.lindex("coil_current_queue", i )
        
        json_object["coil_current_queue"].append(data)
    
      json_string = json.dumps( json_object )
      return json_string



  def find_step( self, sprinkler_ctrl, schedule_name ):
      returnValue = None
      count = 0
      for j in sprinkler_ctrl:
         if j["name"] == schedule_name: 
             returnValue = count
             return returnValue
         count = count +1
      return returnValue


  def start_time_update( self, url_list, redis_handle, cherrypy ):

    json_object = cherrypy.request.params["JSON"] 
    json_file = open("/media/mmc1/app_data_files/sprinkler_ctrl.json")
    sprinkler_ctrl = json.load(json_file)
    step = self.find_step( sprinkler_ctrl, json_object["schedule_name"] );
    sprinkler_ctrl[step]["start_time"] = json_object["start_time"];
    sprinkler_ctrl[step]["end_time"] = json_object["end_time"];
    sprinkler_ctrl[step]["dow"] =  json_object["dow"];
    json_file = open("/media/mmc1/app_data_files/sprinkler_ctrl.json",'w' )
    json.dump( sprinkler_ctrl, json_file  )
    return json.dumps("SUCCESS")
 


  def update_run_time( self, url_list, redis_handle, cherrypy ):
     
     json_object = cherrypy.request.params["JSON"]
     json_file = open("/media/mmc1/app_data_files/sprinkler_ctrl.json")
     sprinkler_ctrl = json.load(json_file)
     json_object["schedule_step"] = int(json_object["schedule_step"])
     json_object["runtime_step"] =  int(json_object["runtime_step"])
     step = self.find_step( sprinkler_ctrl, json_object["schedule_name"])
     json_file = open("/media/mmc1/app_data_files/"+sprinkler_ctrl[step]["link"] )
     temp = json.load(json_file)
     temp["schedule"][json_object["schedule_step"]][0][2] = json_object["runtime_step"]
     json_file = open("/media/mmc1/app_data_files/"+sprinkler_ctrl[step]["link"],'w' )
     json.dump( temp, json_file )
     return json.dumps("SUCCESS") 


  def delete_schedule( self, url_list, redis_handle, cherrypy ):
     json_object = cherrypy.request.params["JSON"]
     print("------------------------ made it here -----------------")
     json_file = open("/media/mmc1/app_data_files/sprinkler_ctrl.json")
     sprinkler_ctrl = json.load(json_file)
     step = self.find_step( sprinkler_ctrl, json_object["deleted_schedule"])
     link_file = "/media/mmc1/app_data_files/"+sprinkler_ctrl[step]["link"] 
     os.remove( link_file ) 
     del sprinkler_ctrl[step]

     json_file = open("/media/mmc1/app_data_files/sprinkler_ctrl.json",'w' )
     json.dump( sprinkler_ctrl, json_file )
     return json.dumps("SUCCESS")


  def insert_schedule( self, url_list, redis_handle, cherrypy ):
    
     json_object = cherrypy.request.params["JSON"]
     insert_schedule = json_object["insert_schedule"]
     temp = {}
     temp["name"] = insert_schedule
     temp["description"] = ""
     temp["end_time"] = []
     temp["start_time"] = []
     for i in range(0,2):
        temp["start_time"].append(0)
     for i in range(0,2):
       temp["end_time"].append(0)
     
     temp["dow"] = []
     for i in range(0,7):
      temp["dow"].append(0)
     
     temp["link"] = insert_schedule+".json"
     json_file = open("/media/mmc1/app_data_files/sprinkler_ctrl.json")
     sprinkler_ctrl = json.load(json_file)
     sprinkler_ctrl.append(temp)

     json_file = open("/media/mmc1/app_data_files/sprinkler_ctrl.json",'w' )
     json.dump( sprinkler_ctrl, json_file )

     temp = {}
     temp["bits"] = []
     temp["bits"].append("C201")
     temp["bits"].append("C2")
     temp["bits"].append("DS2")
     temp["schedule"] = None
     
     json_file = open("/media/mmc1/app_data_files/"+insert_schedule+".json",'w' )
     json.dump( temp, json_file )
     return json.dumps("SUCCESS")

  def copy_schedule( self, url_list, redis_handle, cherrypy ):
     json_object = cherrypy.request.params["JSON"]
     copy_source = json_object["copy_source"]
     copy_destination = json_object["copy_destination"]

     json_file = open("/media/mmc1/app_data_files/sprinkler_ctrl.json")
     sprinkler_ctrl = json.load(json_file)
     step = self.find_step(sprinkler_ctrl,copy_source)
     temp = json.dumps(sprinkler_ctrl[step])
     temp = json.loads(temp)
     temp["name"] =copy_destination
     temp["link"] = copy_destination+".json"
     sprinkler_ctrl.append(temp)

     json_file = open("/media/mmc1/app_data_files/sprinkler_ctrl.json",'w' )
     json.dump( sprinkler_ctrl, json_file )
     copyfile("/media/mmc1/app_data_files/"+copy_source+".json",
              "/media/mmc1/app_data_files/"+copy_destination+".json" )

     
     return json.dumps("SUCCESS")

  def change_schedule( self, url_list, redis_handle, cherrypy ):
      field_map = {"station_1","station_2","station_3","station_4","station_5"} 
      json_object = cherrypy.request.params["JSON"]

      temp = {}
      temp["name"] = json_object["schedule_name"]
      temp["description"] = json_object["description"]
      
      temp["end_time"] = []
      for i in range(0,2):
        temp["end_time"].append(json_object["end_time"][i])
     
      temp["start_time"] = []
      for i in range(0,2):
        temp["start_time"].append( json_object["start_time"][i])
    
      temp["dow"] = []
      for i in range(0,7):
         temp["dow"].append( json_object["dow"][i] )

      temp["link"] = json_object["schedule_name"]+".json"
    
      json_file = open("/media/mmc1/app_data_files/sprinkler_ctrl.json")
      sprinkler_ctrl = json.load(json_file)
      index = self.find_step( sprinkler_ctrl, json_object["schedule_name"] )
      sprinkler_ctrl[index] = temp

      json_file = open("/media/mmc1/app_data_files/sprinkler_ctrl.json",'w' )
      json.dump( sprinkler_ctrl, json_file )

     
      temp = {}
      temp["bits"] = {}
      temp["bits"][1] = "C201"
      temp["bits"][2] = "C2"
      temp["bits"][3] = "DS2"
      if json_object["grid_data"] == None:
        temp["schedule"]= None
      else:

       temp["schedule"] = []
       for j in json_object["grid_data"]:
   
          temp_schedule = []
          

          for  m in field_map:
            if j.has_key(m) ==  True :
              # builds the following element [ "satellite_1",  [2],15   ]
              controller_pin = j[m].split(":")
              temp_element = []
              temp_element.append(controller_pin[0])
              temp_element.append([])
              temp_element[1].append( int(controller_pin[1]))
              temp_element.append(int(j["time"]))
              temp_schedule.append(temp_element)
            else:
              break
            
         
          temp["schedule"].append(temp_schedule) 
         
     

      json_file = open("/media/mmc1/app_data_files/"+json_object["schedule_name"]+".json",'w' )
      json.dump(  temp, json_file )
      return json.dumps("SUCCESS")     





  def schedule_entry( self, url_list, redis_handle, cherrypy ):
      returnValue = []
      query_string = cherrypy.request.query_string
     
      json_string = urllib.unquote(query_string)
      json_object = json.loads(json_string)
     
      schedule_name = json_object["schedule_name"]

      json_file = open("/media/mmc1/app_data_files/sprinkler_ctrl.json")
      sprinkler_ctrl = json.load(json_file)
      for j in  sprinkler_ctrl:
         json_file = open("/media/mmc1/app_data_files/"+j["link"])
         temp = json.load(json_file)
         j["step_number"], j["steps"], j["controller_pins"] = self.generate_steps(temp)
         returnValue.append(j)
   
      index = self.find_step( sprinkler_ctrl, schedule_name )
      returnValue = returnValue[index];
      return json.dumps( returnValue )
 
 
