import json
import base64

class Load_Irrigation_Pages(object):

   def __init__( self, app, auth, render_template, redis_handle, redis_new_handle, request ):
       self.app             = app
       self.auth            = auth
       self.redis_handle    = redis_handle
       self.redis_new_handle = redis_new_handle
       self.render_template = render_template
       self.request         = request

       a1 = auth.login_required( self.get_index_page )
       app.add_url_rule('/index.html',"get_index_page",a1) 
       app.add_url_rule("/","get_slash_page",a1)

       a1 = auth.login_required( self.get_diagnostic_page )
       app.add_url_rule('/diagnostics/<filename>',"get_diagnostic_page",a1 )

       a1 = auth.login_required( self.schedule_data )
       app.add_url_rule('/ajax/schedule_data',"get_schedule_data",a1 )

       a1 = auth.login_required( self.mode_change )
       app.add_url_rule('/ajax/mode_change',"get_mode_change",a1, methods=["POST"])

       a1= auth.login_required( self.irrigation_control )
       app.add_url_rule("/control/control","irrigation_control",a1)
 
       a1= auth.login_required( self.irrigation_queue )
       app.add_url_rule("/control/irrigation_queue","irrigation_queue",a1)

       a1= auth.login_required( self.display_irrigation_queue )
       app.add_url_rule("/control/display_irrigation_queue","display_irrigation_queue",a1)

       a1= auth.login_required( self.set_rain_day )
       app.add_url_rule("/control/set_rain_day","set_rain_day",a1)

       a1= auth.login_required( self.eto_management )
       app.add_url_rule("/control/eto_management","eto_management",a1)

   def irrigation_control(self):
       return self.render_template("irrigation_control")
      
   def get_index_page(self):
       return self.get_diagnostic_page( filename = "schedule_control" )

   def get_diagnostic_page(self, filename):   
       return self.render_template("irrigation_diagnostics", filename = filename )

   def irrigation_queue(self):
       return self.render_template("irrigation_queue" )

   def display_irrigation_queue(self):
       return self.render_template("display_irrigation_queue" )

   def set_rain_day(self):
       return self.render_template("set_rain_day" )
       

   def eto_management(self):
        return self.render_template("eto_management" )
      


   #  
   #  Function serves a post operation
   #
   def schedule_data(self):
     data           = self.redis_handle.hget("FILES:APP","sprinkler_ctrl.json").decode()
     sprinkler_ctrl = json.loads(data)
     returnValue = []
     for j in sprinkler_ctrl:
         data           = self.redis_handle.hget("FILES:APP",j["link"]).decode()
         temp           = json.loads(data)
         j["step_number"], j["steps"], j["controller_pins"] = self.generate_steps(temp)
         returnValue.append(j)
     return json.dumps(returnValue)   

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

   def mode_change( self):
       json_object = self.request.json
       scratch = json.dumps(json_object).encode()
       self.redis_handle.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
       return json.dumps("SUCCESS")
 


  