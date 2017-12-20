import json 

import redis
import base64

class System_Status():

   def __init__(self,redis_handle ):
       self.redis_handle = redis_handle
       pass

   def save_eto_data( self, json_object ):
 
       for j in  json_object:
           self.redis_handle.hset("ETO_RESOURCE",j["name"],j["data"])
       return json.dumps("SUCCESS")
 


   def get_eto_entries( self, *args ):
  
  
       json_object = []
     
       eto_list = self.redis_handle.hkeys(  "ETO_RESOURCE")
  
       for j in eto_list:
           temp = {}
           temp["name"]  = j
           temp["data"]  = self.redis_handle.hget("ETO_RESOURCE", j )
           json_object.append(temp)
     
     
       json_string = json.dumps( json_object )

       return json_string
 


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



   def schedule_data( self, *args):
     data           = self.redis_handle.hget("FILES:APP","sprinkler_ctrl.json")

     sprinkler_ctrl = json.loads(data)
     returnValue = []
     for j in sprinkler_ctrl:
         ###---
         data           = self.redis_handle.hget("FILES:APP",j["link"])

         temp           = json.loads(data)
         print "temp",temp
         j["step_number"], j["steps"], j["controller_pins"] = self.generate_steps(temp)
         returnValue.append(j)
  

     return json.dumps(returnValue)   


   def get_schedule_data( self, *args):
     data           = self.redis_handle.hget("FILES:APP","sprinkler_ctrl.json")
     sprinkler_ctrl = json.loads(data)
     returnValue = []
     for j in sprinkler_ctrl:
         ###---
         data           = self.redis_handle.hget("FILES:APP",j["link"])

         temp           = json.loads(data)
         j["step_number"], j["steps"], j["controller_pins"] = self.generate_steps(temp)
         returnValue.append(j)
  

     return json.dumps(returnValue)   

   def native_mode_change( self, json_object ):
       
        temp = {}
        temp["command"] =        json_object["command"]
        temp["controller"]       = json_object["controller"]
        temp["pin"]           = int(json_object["pin"])
        temp["run_time"]       = int(json_object["run_time"])
        print "temp",temp
        scratch = json.dumps(temp)
        print "native_mode_change"
 
        command = temp["command"]
        print "-------------->",temp["command"]
        if command == "CLEAR":
           temp["command"] = "OFFLINE"
           scratch = json.dumps(temp)
           self.redis_handle.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
           temp["command"] = "RESUME"
           scratch = json.dumps(temp)
           self.redis_handle.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
        elif command == "NATIVE_SPRINKLER":
           temp["command"] = "OFFLINE"
           scratch = json.dumps(temp)
           self.redis_handle.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
           temp["command"] = "RESUME"
           scratch = json.dumps(temp)
           self.redis_handle.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
           temp["command"] = "NATIVE_SPRINKLER"
           scratch = json.dumps(temp)
           
           self.redis_handle.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
        else:
            scratch = json.dumps(temp)
            self.redis_handle.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
        return json.dumps("SUCCESS")
 



   def mode_change( self, json_object ):
       
        temp = {}
        temp["command"] =        json_object["command"]
        temp["schedule_name"]  = json_object["schedule_name"]
        temp["step"]           = int(json_object["step"])
        temp["run_time"]       = int(json_object["run_time"])
        command = temp["command"]
        if command == "CLEAR":
           temp["command"] = "OFFLINE"
           scratch = json.dumps(temp)
           self.redis_handle.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
           temp["command"] = "RESUME"
           scratch = json.dumps(temp)
           self.redis_handle.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
        elif command == "NATIVE_SCHEDULE":
           temp["command"] = "OFFLINE"
           scratch = json.dumps(temp)
           self.redis_handle.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
           temp["command"] = "RESUME"
           scratch = json.dumps(temp)
           self.redis_handle.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
           temp["command"] = "NATIVE_SCHEDULE"
           scratch = json.dumps(temp)
           
           self.redis_handle.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
        else:
            scratch = json.dumps(temp)
            self.redis_handle.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
        return json.dumps("SUCCESS")
 


   def get_queue_entry( self, *args ):

     json_object = []
     length =   self.redis_handle.llen( "IRRIGATION_QUEUE" )
     if length > 0 :
        name      = "unspecified"
        total     = 0
        for i in  range(0, length):
           data = self.redis_handle.lindex( "IRRIGATION_QUEUE", length-1  -i)
           
           if data != None :
	     data = json.loads(data)
             if  data["type"] == "END_SCHEDULE" :
	        element = {}
	        name = data["schedule_name"]
                if len(json_object) == 0:
                  schedule_time_max = int(self.redis_handle.get("schedule_time_max"))
                  schedule_step     = int(self.redis_handle.get("schedule_time_count"))
                  print "total",total
                  total = total +schedule_time_max-schedule_step
                  print "total",total

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
           if len(json_object) == 0:
             schedule_time_max = int(self.redis_handle.get("schedule_time_max"))
             schedule_step     = int(self.redis_handle.get("schedule_time_count"))
             total = total +schedule_time_max-schedule_step
           
	   element["value"]  = total
	   json_object.append(element)
    

  
     json_string = json.dumps(json_object)
    
     return json_string
 

 
   def delete_queue( self, json_object, *parms ):
  
       length =   self.redis_handle.llen( "IRRIGATION_QUEUE" )
       if length > 0 :
           queue_index = 0
           for i in range(0,length):
               queue_index_temp = queue_index
               data = self.redis_handle.lindex( "IRRIGATION_QUEUE", length - 1 -i)
               if data != None:
	           data = json.loads(data)
                   if  data["type"] == "END_SCHEDULE" :
                       queue_index_temp = queue_index +1 
                   if json_object[ queue_index ] != 0 :
                       self.redis_handle.lset( "IRRIGATION_QUEUE",length - 1 -i,"NULL/NULL")
                       self.redis_handle.lrem( "IRRIGATION_QUEUE", 1, "NULL/NULL" )
                      
                
               queue_index = queue_index_temp
        

       json_string = json.dumps("SUCCESS")
       return json_string


