#
#
# This is Support for Drawing Bullet Charts
#
#
#
#
#
#
#

''' 
This is the return json value to the javascript front end  
{ "canvasName":"canvas1","featuredColor":"Green", "featuredMeasure":14.5,
                                                "qualScale1":14.5, "qualScale1Color":"Black","titleText":"Step 1" },
                                             { "canvasName":"canvas2","featuredColor":"Blue", "featuredMeasure":14.5,
                                                "qualScale1":14.5, "qualScale1Color":"Black","titleText":"Step 2" },
                                             { "canvasName":"canvas3","featuredColor":"Red", "featuredMeasure":14.5,
                                                "qualScale1":14.5, "qualScale1Color":"Black","titleText":"Step 3" },
'''
import base64
import json


class template_support():

   def __init__(self , redis_handle, statistics_module):
       self.redis_handle       = redis_handle
       self.statistics_module  = statistics_module


   def  generate_current_canvas_list( self, schedule_name, *args, **kwargs ):
       return_value = []
       
       self.schedule_name = schedule_name
       data = self.statistics_module.schedule_data[ schedule_name ]

       current_data      = self.statistics_module.get_current_data( data["step_number"],schedule_name )
       limit_values      = self.statistics_module.get_current_limit_values( data["step_number"],schedule_name )
       for i in range(0,data["step_number"]):
           
           temp                                = {}
           temp["canvasName"]                  = "canvas1"   +str(i+1)
           temp["titleText"]                   = "Step "     +str(i+1)
           temp["qualScale1Color"]             = "Black"
           temp["featuredColor"]               = "Red"
           temp["featuredMeasure"]             = current_data[i] 
           try:
              temp["qualScale1"]                  = limit_values[i]['limit_avg']  
              temp["limit"]                       = limit_values[i]['limit_std']
           except:
              temp["qualScale1"]                  = 0  
              temp["limit"]                       = 0
           temp["step"]                        = i
           return_value.append(temp)
           
       return return_value
          

   def resistance_canvas_list( self, controller_id,  *args,**kwargs):
       controller_list, valve_list = self.get_controller_list(controller_id)
       controller_name = controller_list[controller_id]
       limit = []
       for j in range(0,len(valve_list)):
          temp = []
          redis_key = "log_data:resistance_log_limit:"+controller_name+":"+valve_list[j]
          limit_value = self.redis_handle.get(redis_key)
          if limit_value == None:
              redis_list = "log_data:resistance_log:"+controller_name+":"+valve_list[j]
              limit_value = self.redis_handle.lindex(redis_list,0)
              self.redis_handle.set(redis_key,limit_value)
         
          limit.append(limit_value)
 
       resistance = []
       for j in valve_list:
          temp = []
          redis_list = "log_data:resistance_log:"+controller_name+":"+j
          length = self.redis_handle.llen(redis_list)
          for i in range(0,length):
             value = self.redis_handle.lindex(redis_list,i)
     
             temp.append(value)
          resistance.append(temp)
    
       
       return_value = []
      
       for i in range(0,len(valve_list)):
           
           temp                                = {}
           temp["canvasName"]                  = "canvas1"   +  valve_list[i]
           temp["titleText"]                   = "Valve "    +  valve_list[i]
           temp["qualScale1Color"]             = "Black"
           temp["featuredColor"]               = "Red"
           try:
                temp["qualScale1"]             =  float(int(float(float(limit[i])*100)))/100.
           except:
                temp["qualScale1"]             = 0

           try:
               temp["featuredMeasure"]         = resistance[i]
           except:
               temp["featuredMeasure"]         = 0
           try:
               temp["limit"]                   = 0 # limit_values[i]['limit_std']
           except:
               temp["limit"]                   = 0
           return_value.append(temp)
       
      
       return return_value

   

   def generate_canvas_list(self, schedule_name, flow_id ,  *args,**kwargs):
       return_value = []
       
       self.schedule_name = schedule_name
       data = self.statistics_module.schedule_data[ schedule_name ]
       flow_sensors = self.statistics_module.sensor_names 
       flow_sensor_name = flow_sensors[flow_id]

       conversion_rate   = self.statistics_module.conversion_rate[flow_id]

       flow_data      = self.statistics_module.get_average_flow_data( data["step_number"], flow_sensor_name, schedule_name )
       limit_values = self.statistics_module.get_flow_limit_values( data["step_number"], flow_sensor_name, schedule_name )
       
       for i in limit_values:
           try:
               i['limit_avg'] = float(i['limit_avg'])*conversion_rate
               i['limit_std'] = float(i['limit_std'])*conversion_rate
           except:
               i['limit_avg'] = 0
               i['limit_std'] = 0
          
       corrected_flow = []
       for i in flow_data:
           temp1 = []
           
           for j in i:
               temp1.append( j *conversion_rate)
           corrected_flow.append(temp1)
       
       
       for i in range(0,data["step_number"]):
           
           temp                                = {}
           temp["canvasName"]                  = "canvas1"   +str(i+1)
           temp["titleText"]                   = "Step "     +str(i+1)
           temp["qualScale1Color"]             = "Black"
           temp["featuredColor"]               = "Red"
           try:
                temp["qualScale1"]             = limit_values[i]['limit_avg']
           except:
                temp["qualScale1"]             = 0

           try:
               temp["featuredMeasure"]         = corrected_flow[i]
           except:
               temp["featuredMeasure"]         = 0
           try:
               temp["limit"]                       = limit_values[i]['limit_std']
           except:
               temp["limit"]                   = 0
           return_value.append(temp)
           
       return return_value

   def get_controller_list( self,controller_id ):
       base64_object     = self.redis_handle.get(  "SPRINKLER_RESISTANCE_DICTIONARY")
       json_string       = base64.b64decode(base64_object)
       resistance_dictionary = json.loads(json_string)
       
       controllers = resistance_dictionary.keys()
       controllers.sort()
       controller_name = controllers[controller_id]
       valve_data = resistance_dictionary[ controller_name ]
       valve_list  = valve_data.keys()
       valve_list  = map(int, valve_list) 
       valve_list.sort()
       valve_list  = map(str,valve_list)
       return  controllers, valve_list    

   def process_resistance_limit_values( self, controller, data ):
       for i in data :
          redis_key = "log_data:resistance_log_limit:"+controller+":"+i["valve"]
          self.redis_handle.set(redis_key,i["value"] )
          

