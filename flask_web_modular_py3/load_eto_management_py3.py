
import os
import json

class Load_ETO_Management(object):

   def __init__( self, app, auth, request, app_files, sys_files,gm ,
                   redis_new_handle,render_template):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.app_files = app_files
       self.sys_files = sys_files
       self.gm        = gm
       self.redis_new_handle = redis_new_handle
       self.render_template  = render_template
 
       temp = gm.match_terminal_relationship("ETO_SITES")
       self.eto_measurement    = temp[0]["measurement"]
       temp = gm.match_terminal_relationship("RAIN_SOURCES")
       self.rain_measurement    =  temp[0]["measurement"]
       

       a1 = auth.login_required( self.eto_setup )
       app.add_url_rule('/eto/eto_setup',"eto_setup",a1)

       a1 = auth.login_required( self.eto_readings )
       app.add_url_rule('/eto/eto_readings',"eto_raw_data",a1)


       a1 = auth.login_required( self.eto_manage )
       app.add_url_rule('/eto/eto_manage',"eto_manage",a1)
       


   def eto_setup(self):
       eto_data  = self.app_files.load_file( "eto_site_setup.json" )
       pin_list  = self.sys_files.load_file("controller_cable_assignment.json")
       return self.render_template("eto_templates/eto_setup",
                               eto_data = eto_data, 
                               eto_data_json = json.dumps(eto_data), 
                               st = str, 
                               pin_list_json = json.dumps(pin_list) ) 


   def eto_readings(self):
       print(self.eto_measurement)
       eto_data =  self.redis_new_handle.get(self.eto_measurement)
       rain_data = self.redis_new_handle.get(self.rain_measurement)
       return self.render_template( "eto_templates/eto_readings",eto_data = eto_data, rain_data = rain_data ) 


   def eto_manage( self ):
       return self.render_template("eto_templates/eto_manage")
