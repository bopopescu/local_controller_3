import os
import json
import base64
import collections

from  .statistics_handlers.Detail_Elements_py3 import Detail_Elements
from  .statistics_handlers.Composite_Elements_py3 import Composite_Elements

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
       detail_elements = Detail_Elements( redis_old_handle, render_template, app_files)
       composite_elements = Composite_Elements(render_template,redis_old_handle, app_files )
 
       a1 = auth.login_required( detail_elements.detail_statistics_setup_page )
       app.add_url_rule('/detail_statistics/<int:schedule>/<int:step>/<int:field_id>/<int:attribute_id>',
                             "detail_statistics",a1,methods=["GET"])
                           
       a1 = auth.login_required( detail_elements.time_series_statistics_setup_page )
       app.add_url_rule('/time_series_statistics/<int:schedule_index>/<int:step>/<int:field_index>/<int:time_step_index>/<int:display_number_index>',
                             "time_series_statistics",a1,methods=["GET"])
                       

       a1 = auth.login_required( composite_elements.composite_statistics )
       app.add_url_rule('/composite_statistics/<int:schedule_index>/<int:field_index>',
                             "composite_statistics",a1,methods=["GET"])
                     




   




if __name__ == "__main__":
   pass