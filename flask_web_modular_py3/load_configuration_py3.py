import os
import json

class Load_Configuration_Data(object):

   def __init__( self, app, auth,render_template,request,app_files,sys_files ):
       self.app      = app
       self.auth     = auth
       self.render_template = render_template
       self.request = request
       self.app_files = app_files
       self.sys_files = sys_files
       

       a1 = auth.login_required( self.system_actions )
       app.add_url_rule('/system_actions',"system_actions",a1,methods=["GET"])
      
       a1 = auth.login_required( self.add_schedule )
       app.add_url_rule('/add_schedule',"add_schedule",a1,methods=["GET"])

       a1 = auth.login_required( self.copy_schedule )
       app.add_url_rule('/copy_schedule',"copy_schedule",a1,methods=["GET"])

       a1 = auth.login_required( self.delete_schedules )
       app.add_url_rule('/delete_schedules',"delete_schedules",a1,methods=["GET"])

       a1 = auth.login_required( self.edit_schedules )
       app.add_url_rule('/edit_schedules',"edit_schedules",a1,methods=["GET"])

       a1 = auth.login_required( self.overall_flow_limits )
       app.add_url_rule('/configure_flow_limits/<int:flow_id>/<int:schedule_id>',
                        "configure_flow_limits",a1,methods=["GET"])

       a1 = auth.login_required( self.overal_current_limits )
       app.add_url_rule('/configure_current_limits/<int:schedule_id>',
                           "configure_current_limits",a1,methods=["GET"])

       a1 = auth.login_required( self.overal_resistance_limits )
       app.add_url_rule('/overal_resistance_limits/<int:controller_id>',
                          "overal_resistance_limits",a1,methods=["GET"])

       a1 = auth.login_required( self.update_schedule )
       app.add_url_rule("/ajax/update_schedule",
                          "ajax_update_schedule",a1,methods=["POST"])

   def system_actions(self):  
       system_actions = self.app_files.load_file( "system_actions.json" )
       return self.render_template( "configuration/system_actions",  
                               title="Configure System Events",
                               system_actions       =  system_actions ,
                               system_actions_json  =  json.dumps( system_actions ) )

   def add_schedule(self): 
       schedule_data = self.get_schedule_data() 
       return self.render_template( "configuration/add_schedule",
                               template_type = "add", 
                               title="Add Schedule",
                               schedule_list      =  schedule_data.keys(),
                               pin_list           =  json.dumps(self.sys_files.load_file("controller_cable_assignment.json")),
                               schedule_data_json =  json.dumps(schedule_data)  ) 


   def copy_schedule(self):  
       schedule_data = self.get_schedule_data() 
       return self.render_template( "configuration/copy_schedule", 
                               template_type = "copy", 
                               title="Copy Schedule",
                               schedule_list      =  schedule_data.keys(),
                               pin_list           =  json.dumps(self.sys_files.load_file("controller_cable_assignment.json")),
                               schedule_data_json =  json.dumps(schedule_data)  ) 


   def delete_schedules(self):  
       schedule_data = self.get_schedule_data()
       return self.render_template( "configuration/delete_schedule", 
                               template_type = "delete", 
                               title="Delete Schedules",
                               schedule_list      =  schedule_data.keys(),
                               pin_list           =  json.dumps(self.sys_files.load_file("controller_cable_assignment.json")),
                               schedule_data_json =  json.dumps(schedule_data)  ) 



   def edit_schedules(self):
       schedule_data = self.get_schedule_data()  
       return self.render_template( "configuration/edit_schedule", 
                               template_type = "edit",
                               title="Edit Schedule",
                               schedule_list      =  schedule_data.keys(),
                               pin_list           =  json.dumps(self.sys_files.load_file("controller_cable_assignment.json")),
                               schedule_data_json =  json.dumps(schedule_data)  ) 

 
  
 
  
   def overall_flow_limits(self, flow_id, schedule_id ):
       schedule_list = statistics_module.schedule_data.keys()
       sensor_name  = statistics_module.sensor_names[flow_id]
       max_flow_rate = 33
       canvas_list = template_support.generate_canvas_list( schedule_list[schedule_id], flow_id   ) 
       return self.render_template("overall_flow_limits", 
                               schedule_id=schedule_id,
                               flow_id=flow_id,  
                               header_name="Flow Overview  Max Flow Rate "+str(max_flow_rate), 
                               flow_sensors = statistics_module.sensor_names,
                               schedule_list = schedule_list, 
                               max_flow_rate = max_flow_rate, 
                               canvas_list= canvas_list )

   def overal_current_limits(self, schedule_id):
       max_current = 30
       schedule_list = statistics_module.schedule_data.keys()
       canvas_list = template_support.generate_current_canvas_list( schedule_list[schedule_id]  ) 
       return self.render_template("overall_current_limits", 
                               schedule_id=schedule_id,
                               header_name="Valve Current Overview  Max Current "+str(max_current),
                               schedule_list = schedule_list, 
                               max_flow_rate = max_current, 
                               canvas_list= canvas_list )

  
   def overal_resistance_limits(self, controller_id):
       max_current      = 30
       controller_list,valve_list  = template_support.get_controller_list(controller_id)
       
       canvas_list      = template_support.resistance_canvas_list(  controller_id ) 
       return self.render_template("overal_resistance_limits", 
                               controller_id     = controller_id,
                               header_name       ="Valve Resistance Max Value:  "+str(max_current), 
                               controller_list   = controller_list,
                               max_current       = max_current, 
                               canvas_list       = canvas_list,
                               valve_list_json   = json.dumps(valve_list) )




   def update_schedule(self ):
       return_value     = {}
       param              = self.request.get_json()
       action             = param["action"] 
       schedule           = param["schedule"] 
       schedule_data      = param["data"] 
       
       if action == "delete":
           self.delete_schedule( schedule )
           self.delete_link_file( schedule )
           
       else:
           self.save_link_file( schedule, schedule_data[schedule] )
           self.save_schedule( schedule_data[schedule]  )
           
       return json.dumps("SUCCESS")



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



   def find_sched_index( self,  name, ref_sched_data ):
      
        for i in range(0, len(ref_sched_data) ):
           
           if ref_sched_data[i]["name"] == name:
              return i
        return None

  


   def save_schedule( self, schedule_data ):
       name = schedule_data["name"]
       ref_sched_data  = self.app_files.load_file( "sprinkler_ctrl.json" )

       index = self.find_sched_index( name, ref_sched_data )
       
       if index != None:
            ref_sched_data[ index ] = schedule_data
       else:
            ref_sched_data.append( schedule_data)
  
       self.app_files.save_file( "sprinkler_ctrl.json",ref_sched_data)
      

   def save_link_file( self, schedule, schedule_data ):
       print("@@@@@@@@@@@@@@@@@@@@@@@@",schedule,schedule_data)
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
       
       self.app_files.save_file( schedule+".json", link_data )

   def delete_link_file( self, schedule ):
       try:
         self.app_files.delete_file( schedule+".json" )
       except:
          pass
   def delete_schedule( self, schedule ):
       
       ref_sched_data  = self.app_files.load_file( "sprinkler_ctrl.json" )
       index = self.find_sched_index( schedule, ref_sched_data )
       
       if index != None:

            del ref_sched_data[ index ] 
            self.app_files.save_file( "sprinkler_ctrl.json" , ref_sched_data )
           







   '''

@app.route('/ajax/update_flow_limit',methods=["POST"])
@authDB.requires_auth
def update_flow_limit():
   return_value     = {}
   param              = request.get_json() 
   schedule           = param["schedule"]
   sensor             = param["sensor"] 
   data               = param["limit_data"]
   statistics_module.process_flow_limit_values( sensor, schedule, data)
   return json.dumps("SUCCESS")

@app.route('/ajax/update_current_limit',methods=["POST"])
@authDB.requires_auth
def update_current_limit():
   return_value     = {}
   param              = request.get_json() 
   schedule           = param["schedule"]
   data               = param["limit_data"]
   statistics_module.process_current_limit_values( schedule, data)
   return json.dumps("SUCCESS")

@app.route('/ajax/update_resistance_limit',methods=["POST"])
@authDB.requires_auth
def update_resistance_limit():
   return_value     = {}
   param              = request.get_json() 
   controller         = param["controller"]
   data               = param["limit_data"]
   template_support.process_resistance_limit_values( controller, data)
   return json.dumps("SUCCESS")
   '''
