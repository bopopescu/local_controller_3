import os
import json
import base64
import collections

class Load_Statistic_Data(object):

   def __init__( self, app, auth,render_template,request,
                 app_files,sys_files,redis_old_handle, redis_new_handle,gm ):
       self.app      = app
       self.auth     = auth
       self.render_template = render_template
       self.request = request
       self.app_files = app_files
       self.sys_files = sys_files
       self.redis_old_handle = redis_old_handle
       self.redis_new_handle = redis_new_handle
       self.gm               = gm
      
       a1 = auth.login_required( self.detail_statistics_setup_page )
       app.add_url_rule('/detail_statistics/<int:schedule>/<int:step>/<int:field_id>/<int:attribute_id>',
                             "detail_statistics",a1,methods=["GET"])
                           
       a1 = auth.login_required( self.time_series_statistics_setup_page )
       app.add_url_rule('/time_series_statistics/<int:schedule_index>/<int:step>/<int:field_index>/<int:time_step_index>/<int:display_number_index>',
                             "time_series_statistics",a1,methods=["GET"])

   def detail_statistics_setup_page(self, schedule,step ,field_id, attribute_id ):
    
        schedule_data = self.get_schedule_data()
        schedule_list = sorted(list(schedule_data.keys()))
        
        schedule_name = schedule_list[schedule]
        step_number = schedule_data[schedule_name]["step_number"]
        
        if step >= step_number:
            step = step_number-1
            
        log_name = "log_data:unified:"+schedule_name+":"+str(step+1)
        limit_name = "limit_data:unified:"+schedule_name+":"+str(step+1)
        data = self.redis_old_handle.lindex(log_name,0)
        data = json.loads(data)
        field_list = sorted(set(data["fields"].keys()))
        flatten_data = self.flatten(data["fields"][field_list[0]])
        sub_field_list   =  sorted(set(flatten_data.keys()))
        irrigation_data = self.get_irrigation_data( log_name )
        limit_data      = self.get_limit_data(limit_name,log_name)
        return self.render_template("statistics/detail_statistics", 
                                      title = "Time Series Irrigation Profile",
                                      schedule_id = schedule,
                                      field_list=field_list, 
                                      sub_field_list = sub_field_list, 
                                      schedule_data = schedule_data,
                                      schedule_name = schedule_name, 
                                      schedule_step = step , 
                                      step_number = step_number,
                                      schedule_list = schedule_list ,
                                      irrigation_data = irrigation_data,
                                      limit_data      = limit_data,
                                      field_id        =  field_id,
                                      attribute_id    =  attribute_id )
                                      
                                      
                                      
   def time_series_statistics_setup_page(self, schedule_index ,step , field_index, time_step_index, display_number_index):
    
        schedule_data = self.get_schedule_data()
        schedule_list = sorted(list(schedule_data.keys()))
        
        schedule_name = schedule_list[schedule_index]
        step_number = schedule_data[schedule_name]["step_number"]
        
        if step >= step_number:
            step = step_number-1
            
        log_name = "log_data:unified:"+schedule_name+":"+str(step+1)
        limit_name = "limit_data:unified:"+schedule_name+":"+str(step+1)
        data = self.redis_old_handle.lindex(log_name,0)
        if data == None:
             data = []
             field_list = []
             irrigation_data = []
             limit_data = []
        else:
            data = json.loads(data)
            field_list = sorted(set(data["fields"].keys()))
            irrigation_data = self.get_irrigation_time_data( log_name )
            limit_data      = self.get_limit_time_data(limit_name,log_name)
        return self.render_template("statistics/time_series_statitics",
                                      title = "Time Irrigation Profile",
                                      schedule_id = schedule_index,
                                      field_list=field_list, 
                                      schedule_data = schedule_data,
                                      schedule_name = schedule_name, 
                                      schedule_step = step , 
                                      step_number = step_number,
                                      schedule_list = schedule_list ,
                                      irrigation_data = irrigation_data,
                                      limit_data      = limit_data,
                                      field_index       =  field_index,
                                      time_step_index      =  time_step_index,
                                      display_number_index    = display_number_index )                                      
                                      
#  correct step
#  add step number
       
   #
   #  Internal functions
   #
   
       
   def get_schedule_data( self, *args):
       sprinkler_ctrl           = self.app_files.load_file("sprinkler_ctrl.json")
     
       returnValue = {}
       for j in sprinkler_ctrl:
           data           = self.app_files.load_file(j["link"])
           
           j["step_number"], j["steps"], j["controller_pins"] = self.generate_steps(data)         
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


   def get_irrigation_data( self, log_name ):
       return_value = []
       temp_list = self.redis_old_handle.lrange(log_name, 0,-1) 
       for i in temp_list:
          temp_dict = json.loads(i)
          return_value.append(self.compose_array_element( temp_dict ))
       return return_value

   def get_irrigation_time_data( self, log_name ):
       return_value = []
       temp_list = self.redis_old_handle.lrange(log_name, 0,-1) 
       for i in temp_list:
          temp_dict = json.loads(i)
          return_value.append(self.compose_time_array_element( temp_dict ))
       return return_value



   def get_limit_data( self, limit_name, log_name):
       temp_limit_json = self.redis_old_handle.get(limit_name)
       if temp_limit_json == None: # add limit  as last element
            print("derived limit")
            temp_limit_json = self.redis_old_handle.lindex( log_name, 0 )
            self.redis_old_handle.set(limit_name,temp_limit_json)
       else:
           print("normal limits")
       temp_limit = json.loads(temp_limit_json )
       return self.compose_time_array_element(temp_limit)
       
   def get_limit_time_data( self, limit_name, log_name):
       temp_limit_json = self.redis_old_handle.get(limit_name)
       if temp_limit_json == None: # add limit  as last element
        
            temp_limit_json = self.redis_old_handle.lindex( log_name, 0 )
            self.redis_old_handle.set(limit_name,temp_limit_json)
       
       temp_limit = json.loads(temp_limit_json )
       return self.compose_time_array_element(temp_limit)
      
   def compose_array_element( self, array_element ):
        return_value = {}
        return_value["time"] = array_element["time"]
        return_value["fields"] = {}
        for key,item in array_element["fields"].items():
            if key != "data":
               return_value["fields"][key] = self.flatten(item)
        return return_value
        
   def compose_time_array_element( self, array_element ):
        return_value = {}
        return_value["time"] = array_element["time"]
        for k,v in array_element["fields"].items():
            return_value[k] = v["data"]
        return return_value

   def flatten(  self, d, parent_key='', sep='_'):
       items = []
       for k, v in d.items():
           new_key = parent_key + sep + k if parent_key else k
           if isinstance(v, collections.MutableMapping):
               items.extend(self.flatten(v, new_key, sep=sep).items())
           else:
               items.append((new_key, v))
       return dict(items)



if __name__ == "__main__":
   pass