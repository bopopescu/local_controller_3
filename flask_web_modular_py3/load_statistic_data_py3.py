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
       app.add_url_rule('/detail_statistics/<int:schedule>/<int:step>',
                             "detail_statistics",a1,methods=["GET"])

   def detail_statistics_setup_page(self, schedule,step  ):
    
        schedule_data = self.get_schedule_data()
        schedule_list = sorted(list(schedule_data.keys()))
        
        schedule_name = schedule_list[schedule]
        step_number = schedule_data[schedule_name]["step_number"]
        
        if step >= step_number:
            step = step_number-1
            
        log_name = "log_data:unified:"+schedule_name+":"+str(step+1)
        data = self.redis_old_handle.lindex(log_name,0)
        data = json.loads(data)
        field_list = sorted(set(data["fields"].keys()))
        flatten_data = self.flatten(data["fields"][field_list[0]])
        sub_field_list   =  sorted(set(flatten_data.keys()))
        irrigation_data = {}
        return self.render_template("statistics/detail_statistics", 
                                      title = "Detail Irrigation Profile",
                                      schedule_id = schedule,
                                      field_list=field_list, 
                                      sub_field_list = sub_field_list, 
                                      schedule_data = schedule_data,
                                      schedule_name = schedule_name, 
                                      schedule_step = step , 
                                      step_number = step_number,
                                      schedule_list = schedule_list ,
                                      irrigation_data = irrigation_data)
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
'''

       <li><a href="/composite_statistics/0/0" target="_self">Composite Statistics</a></li>        
        <li><a href="/detail_statistics/0/0/0/0/0" target="_self">Detail Statistics</a></li>
        <li><a href="/irrigation_time_profile/0/0/0/0/0" target="_self">Irrigation Time Profile</a></li>
@app.route('/detail_statistics_ajax/<int:chart_type>/<int:flow_sensor_id>/<int:schedule_id>/<int:step_id>/<int:time_id>',methods=["GET"])
@authDB.requires_auth
def detail_statistics_ajax(chart_type, flow_sensor_id,schedule_id,step_id,time_id):
   if chart_type == 0:
       schedule_name = statistics_module.schedule_data.keys()[schedule_id]
       sensor_name   = statistics_module.flow_rate_sensor_names[ flow_sensor_id ]
      
       return_value  = statistics_module.get_average_flow_data_queue( step_id, sensor_name, schedule_name )

   if chart_type == 1:
       schedule_name = statistics_module.schedule_data.keys()[schedule_id]
       sensor_name   = statistics_module.flow_rate_sensor_names[ flow_sensor_id ]
       return_value  = statistics_module.get_time_index_flow( time_id, step_id, sensor_name, schedule_name )
   if chart_type == 2:
       schedule_name = statistics_module.schedule_data.keys()[schedule_id]
       sensor_name   = statistics_module.flow_rate_sensor_names[ flow_sensor_id ]
       return_value  = statistics_module.get_total_flow_data( step_id, sensor_name, schedule_name )

   if chart_type == 3:
       schedule_name = statistics_module.schedule_data.keys()[schedule_id]
       return_value  = statistics_module.get_average_current_data_queue( step_id,  schedule_name )


   if chart_type == 4:
       schedule_name = statistics_module.schedule_data.keys()[schedule_id]
       return_value  = statistics_module.get_time_index_current( time_id, step_id,schedule_name )
   
   return_value = json.dumps(return_value)
   return return_value


@app.route('/detail_statistics/<int:chart_type>/<int:flow_sensor_id>/<int:schedule_id>/<int:step_id>/<int:time_id>',methods=["GET"])
@authDB.requires_auth
def detail_1(chart_type, flow_sensor_id,schedule_id,step_id,time_id):

       if chart_type < 0:
           chart_type = 0
       if chart_type > len(display_control)-1:
           chart_type = len(display_control)-1
          
       chart_data        = display_control[ chart_type ]
       schedule_list     = statistics_module.schedule_data.keys()
       
       if schedule_id > len(schedule_list)-1:
           schedule_id = len(schedule_list)-1
       
       logscale = False
       step_number       = statistics_module.schedule_data[ schedule_list[schedule_id] ]["step_number"]
       conversion_factor = statistics_module.conversion_rate[ flow_sensor_id ]
       if step_id > step_number-1:
          step_id = step_number-1
       if time_id > 50:
           time_id = 50
       flow_sensors      = statistics_module.flow_rate_sensor_names
       if chart_type == 0:
            legend_name = "Flow Meter: "+flow_sensors[flow_sensor_id]+"     <br>Schedule:  "+schedule_list[schedule_id]+" <br>Step Number:  "+ str(step_id+1)
       if chart_type == 1:
            legend_name = "Flow Meter: "+flow_sensors[flow_sensor_id]+"     <br>Schedule:  "+schedule_list[schedule_id]+" <br>Step Number:  "+ str(step_id+1) +" <br>Time Index:  "+ str(time_id+1)

       if chart_type == 2:
            legend_name = "Flow Meter: "+flow_sensors[flow_sensor_id]+"     <br>Schedule:  "+schedule_list[schedule_id]+" <br>Step Number:  "+ str(step_id+1)
            logscale = True

       if chart_type == 3:
            legend_name = "Coil Current:<br>Schedule:  "+schedule_list[schedule_id]+" <br>Step Number:  "+ str(step_id+1) 
            conversion_factor = 1.0

       if chart_type == 4:
            legend_name = "Coil Current:<br>Schedule:  "+schedule_list[schedule_id]+" <br>Step Number:  "+ str(step_id+1) +" <br>Time Index:  "+ str(time_id+1)
            conversion_factor = 1.0
       
    
       return render_template(  "detail_statistics",
                                logscale              = logscale,
                                legend_name           = legend_name,
                                conversion_factor     = conversion_factor,
                                chart_list            = chart_list,
                                chart_data            = chart_data,
                                chart_type            = chart_type,
                                flow_sensor_id        = flow_sensor_id,
                                schedule_id           = schedule_id,
                                step_id               = step_id,
                                time_id               = time_id,
                                header_name           = chart_data["name"],
                                schedule_list         = schedule_list,
                                flow_sensors          = flow_sensors,
                                step_number           = step_number ,
                                label_array           = chart_data["label_array"],
                                schedule_data         = json.dumps(statistics_module.schedule_data),
                                schedule_list_json    = json.dumps( schedule_list) )
                                
'''