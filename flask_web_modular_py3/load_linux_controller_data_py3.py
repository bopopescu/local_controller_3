
import os
import json

class Load_Linux_Controller_Data(object):

   def __init__( self, app, auth, request,render_template,redis_new_handle ):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.render_template  = render_template
       self.redis_new_handle = redis_new_handle

       a1 = auth.login_required( self.view_running_process )
       app.add_url_rule('/view_running_process',"view_running_process",a1)
       
       a1 = auth.login_required( self.list_reboot_files )
       app.add_url_rule('/list_reboot_files',"list_reboot_files",a1)

       a1 = auth.login_required( self.display_environmental_conditions )
       app.add_url_rule('/display_environmental_conditions',"display_environmental_conditions",a1)


   def view_running_process(self):
       os.system("/home/pi/new_python/python_process.bsh > tmp_file")
       
       with open("tmp_file","r") as myfile:
           data = myfile.readlines()
       title_a = "View Python Running Processes"
       header_name_a = title_a
       header_a = title_a
      
       return self.render_template( "view_file_list",title =title_a, header_name= header_name_a, file_list = data ,header = header_a) 


   def list_reboot_files(self):

       os.system("ls -l /tmp/*.errr > tmp_file")
       data = ""
       with open("tmp_file","r") as myfile:
           data = myfile.readlines()
           
       title_a = "View Python Error Entries"
       header_name_a = title_a
       header_a = title_a
       return self.render_template( "view_file_list",title =title_a, header_name= header_name_a, file_list = data ,header = header_a) 

   def list_reboot_data( self ):
       #os.system("ls /tmp/*.errr > tmp_file")
       #output = []
       #with open("tmp_file","r") as myfile:
       #    data = myfile.readlines())
       #for i in data:
       #    output.append("/nLog Data for File: "+i)
       #    with open(data[i].strip(),"r" ) as my_file:
       #       output.append( my_file.readlines())
       #title_a = "View Python Error Data"
       #header_name_a = title_a
       #header_a = title_a
       #return self.render_template( "view_file_list",title =title_a, header_name= header_name_a, file_list = data ,header = header_a) 
       pass


   def display_environmental_conditions(self):
       
       data = self.redis_new_handle.lindex("LINUX_HOUR_LIST_STORE",0)
       data = json.loads(data)
       for i,item in data.items():
           if isinstance(item, list):
              pass
           else:
              data[i] = [ item ]

       return self.render_template( "linux_system/display_environmental_conditions",data  = data, keys = data.keys() ) 
       
   def linux_time_history( self ):
       # redis db = 12  key =  LINUX_HOUR_LIST_STORE
       # display time history graph
       pass