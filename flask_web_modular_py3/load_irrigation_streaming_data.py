import os
import json
import base64

class Load_Irrigation_Streaming_Data(object):

   def __init__( self, app, auth,render_template,request,
                 app_files,sys_files,redis_old_handle, redis_new_handle,gm ):
       self.app      = app
       self.auth     = auth
       self.render_template = render_template
       self.request = request
       self.app_files = app_files
       self.sys_files = sys_files
       self.redis_old_handle = redis_old_handle
       self.gm               = gm

       // find redis queue positions for irrigation 
       
  

       a1 = auth.login_required( self._fifteen_second )
       app.add_url_rule('/irrigation_streaming_data/fifteen_second_irrigation',
                             "fifteen_second_irrigation",a1,methods=["GET"])
      
       a1 = auth.login_required( self._one_minute )
       app.add_url_rule('/irrigation_streaming_data/display_minute_irrigation',
                             "display_minute_irrigation",a1,methods=["GET"])
      

       a1 = auth.login_required( self._one_hour )
       app.add_url_rule('/irrigation_streaming_data/display_hour_irrigation',
                            "display_hour_irrigation",a1,methods=["GET"])

       a1 = auth.login_required( self._one_day )
       app.add_url_rule("/irrigation_streaming_data/display_daily_irrigation",
                          "display_daily_irrigation",a1,methods=["GET"])

   def _fifteen_second(self): 
       pass 

   def _one_minute(self): 
       pass 

   def _one_hour(self): 
       pass 

   def _one_day(self): 
       pass 

if __name__ == "__main__":
   pass

   '''
@app.route('/sel_chart/<filename>',methods=["GET"])
@authDB.requires_auth
def sel_chart(filename):
   if sel_prop.has_key(filename ):
       header_name   = sel_prop[filename]["header"]
       queue         = sel_prop[filename]["queue"]
       limit_low     = sel_prop[filename]["limit_low"]
       limit_high    = sel_prop[filename]["limit_high"]
       sel_function  = sel_prop[filename]["sel_function"]
       sel_label     = sel_prop[filename]["sel_label"]
       x_axis        = sel_prop[filename]["x_axis"]
       y_axis        = sel_prop[filename]["y_axis"]

    
       return render_template("sel_chart", queue= queue, header_name = header_name,limit_low = limit_low,limit_high=limit_high, 
                               sel_function = sel_function,sel_label = sel_label, x_axis=x_axis,y_axis=y_axis )


   '''
