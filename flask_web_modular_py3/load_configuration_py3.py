import os
import json

class Load_Configuration_Data(object):

   def __init__( self, app, auth,render_template,app_files,sys_files ):
       self.app      = app
       self.auth     = auth
       self.render_template = render_template
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
       return render_template( "schedule_list", 
                               template_type = "copy", 
                               title="Copy Schedule",
                               schedule_list      =  statistics_module.schedule_data.keys(),
                               pin_list           =  json.dumps(sys_files.load_file("controller_cable_assignment.json")),
                               schedule_data_json =  json.dumps(statistics_module.schedule_data)  ) 


   def delete_schedules(self):  
       
       return render_template( "schedule_list", 
                               template_type = "delete", 
                               title="Delete Schedules",
                               schedule_list      =  statistics_module.schedule_data.keys(),
                               pin_list           =  json.dumps(sys_files.load_file("controller_cable_assignment.json")),
                               schedule_data_json =  json.dumps(statistics_module.schedule_data)  ) 



   def edit_schedules(self):  
       return render_template( "schedule_list", 
                               template_type = "edit",
                               title="Edit Schedule",
                               schedule_list      =  statistics_module.schedule_data.keys(),
                               pin_list           =  json.dumps(sys_files.load_file("controller_cable_assignment.json")),
                               schedule_data_json =  json.dumps(statistics_module.schedule_data)  ) 

 
  
 
  
   def overall_flow_limits(self, flow_id, schedule_id ):
       schedule_list = statistics_module.schedule_data.keys()
       sensor_name  = statistics_module.sensor_names[flow_id]
       max_flow_rate = 33
       canvas_list = template_support.generate_canvas_list( schedule_list[schedule_id], flow_id   ) 
       return render_template("overall_flow_limits", 
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
       return render_template("overall_current_limits", 
                               schedule_id=schedule_id,
                               header_name="Valve Current Overview  Max Current "+str(max_current),
                               schedule_list = schedule_list, 
                               max_flow_rate = max_current, 
                               canvas_list= canvas_list )

  
   def overal_resistance_limits(self, controller_id):
       max_current      = 30
       controller_list,valve_list  = template_support.get_controller_list(controller_id)
       
       canvas_list      = template_support.resistance_canvas_list(  controller_id ) 
       return render_template("overal_resistance_limits", 
                               controller_id     = controller_id,
                               header_name       ="Valve Resistance Max Value:  "+str(max_current), 
                               controller_list   = controller_list,
                               max_current       = max_current, 
                               canvas_list       = canvas_list,
                               valve_list_json   = json.dumps(valve_list) )


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

