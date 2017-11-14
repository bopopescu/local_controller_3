#
#
#  File: flask_web_py3.py
#
#
#
import os
import json
import redis
import load_files_py3
from redis_graph_py3 import farm_template_py3
from flask_web_modular_py3.load_static_pages_py3          import   Load_Static_Files 
from flask_web_modular_py3.load_app_sys_files_py3         import  Load_App_Sys_Files
from flask_web_modular_py3.load_redis_access_py3          import  Load_Redis_Access
from flask_web_modular_py3.load_irrigation_control_py3    import  Load_Irrigation_Pages
from flask_web_modular_py3.load_eto_management_py3        import  Load_ETO_Management
from flask_web_modular_py3.load_site_data_py3             import  Load_Site_Data
from flask_web_modular_py3.load_configuration_py3         import Load_Configuration_Data
from flask_web_modular_py3.load_streaming_data_py3            import Load_Streaming_Data
from flask_web_modular_py3.load_linux_controller_data_py3  import Load_Linux_Controller_Data
from flask_web_modular_py3.load_statistic_data_py3  import Load_Statistic_Data


import flask
from flask import Flask
from flask import render_template,jsonify
from flask_httpauth import HTTPDigestAuth
from flask import request, session


class PI_Web_Server(object):

   def __init__(self , name, redis_handle, redis_new_handle, app_files, sys_files,gm, startup_dict ):
       app         = Flask(name) 
       auth = HTTPDigestAuth()
       auth.get_password( self.get_pw )
       self.startup_dict = startup_dict
       self.app = app
      
       app.template_folder       =   'flask_web_modular_py3/templates'
       app.static_folder         =   'flask_web_modular_py3/static'  
       app.config['SECRET_KEY']      = startup_dict["SECRET_KEY"]
       app.config["DEBUG"]           = startup_dict["DEBUG"]
       self.users                    = json.loads(startup_dict["users"])
       #authDB = FlaskRealmDigestDB(startup_dict["RealmDigestDB"])
       '''
       temp =  json.loads(startup_dict["users"])
       for i in temp.keys():
            print(temp[i])
            authDB.add_user(i, temp[i] )
       '''
       Load_Static_Files( app, auth )
       Load_App_Sys_Files( app,auth,request, app_files, sys_files)
       Load_Redis_Access(  app,auth,request,redis_handle)
       Load_Irrigation_Pages(app,auth,render_template, redis_handle = redis_handle,
                             redis_new_handle =redis_new_handle, request = request)

       Load_ETO_Management(app, auth, request, app_files, sys_files, gm, redis_new_handle,render_template )
       Load_Site_Data(app,auth,render_template)
       Load_Configuration_Data(app,auth,render_template,request , app_files,sys_files,
                               redis_handle,redis_new_handle )
       Load_Streaming_Data(app,auth,render_template,request , app_files,sys_files,
                               redis_handle,redis_new_handle,gm )
       Load_Linux_Controller_Data( app, auth, request,render_template ,redis_new_handle)
       
       Load_Statistic_Data(app,auth,render_template,request , app_files,sys_files, redis_handle,redis_new_handle,gm )

        

   def run_http( self):
       self.app.run(threaded=True , use_reloader=True, host='0.0.0.0',port=80)

   def run_https( self ):
       startup_dict          = self.startup_dict
       self.app.run(threaded=True , use_reloader=True, host='0.0.0.0',
           port=int(startup_dict["PORT"]) ,ssl_context=(startup_dict["crt_file"], startup_dict["key_file"]))
       
 

   
   def get_pw( self,username):
       
      
       if username in self.users:
           return self.users[username]
       return None

 
       
if __name__ == "__main__":

   redis_startup         = redis.StrictRedis( decode_responses=True )


   gm = farm_template_py3.Graph_Management(
        "PI_1", "main_remote", "LaCima_DataStore")

   data_store_nodes = gm.find_data_stores()
   # find ip and port for redis data store
   data_server_ip = data_store_nodes[0]["ip"]
   data_server_port = data_store_nodes[0]["port"]
   # find ip and port for ip server
   #print "data_server_ip", data_server_ip, data_server_port
   redis_new_handle = redis.StrictRedis(
        host=data_server_ip, port=data_server_port, db=12, decode_responses=True)
   redis_handle = redis.StrictRedis(
        host=data_server_ip, port=data_server_port, db=0 , decode_responses=True)

   sys_files = load_files_py3.SYS_FILES(redis_handle)
   app_files = load_files_py3.APP_FILES(redis_handle)
   startup_dict = redis_startup.hgetall("web")
   print(startup_dict)
   pi_web_server = PI_Web_Server(__name__, redis_handle,redis_new_handle, app_files, sys_files,gm, startup_dict )
   pi_web_server.run_https()
   
   