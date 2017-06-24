# 
#
# File: utilities.py
#
#
#
#


import datetime
import time
import string

import math
import redis
import base64
import json

import os
import copy
import load_files_py3
import rabbit_cloud_status_publish_py3

#from   eto_py3.eto import *
#_from   eto_py3.cimis_request import *
#import load_files



#
#
#  This Class Deletes Legacy cimis emails sent to lacima ranch
#  Emails are not used as an api key now is used to access data
#
#
#



class Delete_Cimis_Email():

   def __init__(self,  email_data   ):
     
       self.email_data   = email_data
 


   def delete_email_files( self,chainFlowHandle, chainOjb, parameters, event ):  
       #print "make it here"
       if self.email_data != None: 
           IMAP_SERVER = 'imap.gmail.com'
           IMAP_PORT = '993'
           #print self.email_data
           imap_username = self.email_data["imap_username"] 
           imap_password = self.email_data["imap_password"] 
           self.imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
           self.imap.login(imap_username, imap_password)
           self.imap.select('Inbox')
           status, data = self.imap.search(None, 'ALL')
           count = sum(1 for num in data[0].split())
           print ("count",count)
           if count > 0 :
              self.imap.select('Inbox')
              status, data = self.imap.search(None, 'ALL')
              for num in data[0].split():
                  self.imap.store(num, '+FLAGS', r'\Deleted')
              self.imap.expunge()


#
#  This class schedules actions in the system action file
#  self.app_files.load_file("system_actions.json")
#
#
#
class System_Monitoring():
   def __init__(self, redis_handle ):
     self.redis_handle         = redis_handle
     self.app_files    =  load_files_py3.APP_FILES(redis_handle)



    
   def check_schedule_flag( self, schedule_name ):
      
      data =  self.redis_handle.hget("SYSTEM_COMPLETED", schedule_name)
      data = data.decode()
      try:
        data = json.loads( data)

      except:
         data = [ 0 , -3 ]

      if int(data[0]) == 0 :
         return_value = True
      else:
         return_value = False
       
      
      return return_value
  

   def match_time( self, compare, value ):
     return_value = False
     if compare[0] < value[0]:
       return_value = True
     if (compare[0] ==  value[0]) and ( compare[1] <= value[1] ):
       return_value = True
     return return_value

   def determine_start_time( self, start_time,end_time ):
       return_value = False
       temp = datetime.datetime.today()
       st_array = [ temp.hour, temp.minute ]
       if self.match_time( start_time,end_time ) == True:
	           if ( self.match_time( start_time, st_array) and 
	                self.match_time( st_array, end_time )) == True:
	              return_value = True
       else: 
	         # this is a wrap around case
          if   self.match_time( start_time,st_array) :
               return_value = True
          if  self.match_time(st_array,end_time):
                return_value = True
       return return_value
     



   def clear_done_flag( self, *arg ):
      dow_array = [ 1,2,3,4,5,6,0]
      dow = datetime.datetime.today().weekday()
      dow = dow_array[dow]
      sprinkler_ctrl = self.app_files.load_file("system_actions.json")
      for  j in sprinkler_ctrl:
           name = j["name"]
           if self.determine_start_time( j["start_time"],j["end_time"]) == False: 
               temp_1 = json.dumps( [0,-1] )
               self.redis_handle.hset( "SYSTEM_COMPLETED", name,temp_1  ) 
    
  

   def check_for_active_schedule( self, *args):

      temp = datetime.datetime.today()
      dow_array = [ 1,2,3,4,5,6,0]
      dow = datetime.datetime.today().weekday()
      dow = dow_array[dow]
      st_array = [temp.hour,temp.minute]
      sprinkler_ctrl = self.app_files.load_file("system_actions.json")
      for j in sprinkler_ctrl:
          name     = j["name"]
          command  = j["command_string"]
          print( "checking schedule",name)
          if j["dow"][dow] != 0 :
	    
            start_time = j["start_time"]
            end_time   = j["end_time"]
    
            if self.determine_start_time( start_time,end_time ):
                 print( "made it past start time",start_time,end_time)
                 if self.check_schedule_flag( name ):
                     print( "queue in schedule ",name )
                     temp = {}
                     temp["command"]        = command
                     temp["schedule_name"]  = name
                     temp["step"]           = 0
                     temp["run_time"]       = 0
                     scratch = json.dumps(temp)
                     #self.redis_handle.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
                     temp = [1,time.time()+60*3600 ]  # +hour prevents a race condition
                     self.redis_handle.hset( "SYSTEM_COMPLETED",name,json.dumps(temp) ) 



  
class Schedule_Monitoring():
   def __init__(self, redis_handle ):
     self.redis_handle         = redis_handle
     self.app_files    =  load_files_py3.APP_FILES(redis_handle)



    
   def check_schedule_flag( self, schedule_name ):
      
      data =  self.redis_handle.hget("SCHEDULE_COMPLETED", schedule_name)
      data = data.decode()
      try:
        data = json.loads( data)

      except:
           
           data = [ 0 , -3 ]

      if int(data[0]) == 0 :
           return_value = True
      else:
           return_value = False
       
      
      return return_value
  

   def match_time( self, compare, value ):
     return_value = False
     if compare[0] < value[0]:
       return_value = True
     if (compare[0] ==  value[0]) and ( compare[1] <= value[1] ):
       return_value = True
     return return_value

   def determine_start_time( self, start_time,end_time ):
       return_value = False
       temp = datetime.datetime.today()
       st_array = [ temp.hour, temp.minute ]
       if self.match_time( start_time,end_time ) == True:
	         if ( self.match_time( start_time, st_array) and 
	              self.match_time( st_array, end_time )) == True:
	            return_value = True
       else: 
          # this is a wrap around case
          if   self.match_time( start_time,st_array) :
               return_value = True
          if  self.match_time(st_array,end_time):
              return_value = True
       return return_value
     



   def clear_done_flag( self, *arg ):
      dow_array = [ 1,2,3,4,5,6,0]
      dow = datetime.datetime.today().weekday()
      dow = dow_array[dow]
      sprinkler_ctrl = self.app_files.load_file("sprinkler_ctrl.json")
      for  j in sprinkler_ctrl:
          name = j["name"]
          if self.determine_start_time( j["start_time"],j["end_time"]) == False: 
               temp_1 = json.dumps( [0,-1] )
               self.redis_handle.hset( "SCHEDULE_COMPLETED", name,temp_1  ) 
    
  

   def check_for_active_schedule( self, *args):

      temp = datetime.datetime.today()
      dow_array = [ 1,2,3,4,5,6,0]
      dow = datetime.datetime.today().weekday()
      dow = dow_array[dow]
      st_array = [temp.hour,temp.minute]
      rain_day = self.redis_handle.hget("CONTROL_VARIABLES" ,"rain_day" )
      try:
          rain_day = int( rain_day )
      except:
          rain_day = 0
          self.redis_handle.set("CONTROL_VARIABLES", "rain_day", rain_day)
     
      if rain_day != 0:
          return
      sprinkler_ctrl = self.app_files.load_file("sprinkler_ctrl.json")
      for j in sprinkler_ctrl:
          name = j["name"]
          print( "checking schedule",name )
          if j["dow"][dow] != 0 :
	    
            start_time = j["start_time"]
            end_time   = j["end_time"]
    
            if self.determine_start_time( start_time,end_time ):
                 print( "made it past start time",start_time,end_time )
                 if self.check_schedule_flag( name ):
                     print( "queue in schedule ",name )
                     temp = {}
                     temp["command"] =  "QUEUE_SCHEDULE"
                     temp["schedule_name"]  = name
                     temp["step"]           = 0
                     temp["run_time"]       = 0
                     scratch = json.dumps(temp)
                     print("scheduled ",scratch)
                     scratch = str.encode(scratch)
                     scratch = base64.b64encode(scratch)
                     #self.redis_handle.lpush("QUEUES:SPRINKLER:CTRL", scratch )
                     temp = [1,time.time()+60*3600 ]  # +hour prevents a race condition
                     self.redis_handle.hset( "SCHEDULE_COMPLETED",name,json.dumps(temp) ) 



class Ntpd():
   def __init__( self ):
     pass

   def get_time( self, chainFlowHandle, chainObj, parameters, event ):
     os.system("ntpdate -b -s -u pool.ntp.org")


     
if __name__ == "__main__":

   import time
   import farm_template_py3
   import construct_classes_py3
   import io_control_py3.new_instrument_py3
   #from   linux_acquisition import construct_linux_acquisition_class
   #from   linux_acquisition import add_chains

   gm = farm_template_py3.Graph_Management("PI_1","main_remote","LaCima_DataStore") 
   

    
   cimis_email_data    =  gm.match_terminal_relationship( "CIMIS_EMAIL" )[0]
 
 

   delete_cimis_email = Delete_Cimis_Email(cimis_email_data)

   data_store_nodes = gm.find_data_stores()
   io_server_nodes  = gm.find_io_servers()
  
   # find ip and port for redis data store
   data_server_ip   = data_store_nodes[0]["ip"]
   data_server_port = data_store_nodes[0]["port"]
   redis_new_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 12 )

   redis_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 0 )



   io_server_ip     = io_server_nodes[0]["ip"]
   io_server_port   = io_server_nodes[0]["port"]
   # find ip and port for ip server

   instrument  =  io_control_py3.new_instrument_py3.Modbus_Instrument()

   #instrument.set_ip(ip= io_server_ip, port = int(io_server_port)) 
   #linux_monitoring = construct_linux_acquisition_class( redis_new_handle, gm, instrument )


   action       = System_Monitoring( redis_handle )
   sched        = Schedule_Monitoring( redis_handle )
 
   ntpd = Ntpd()

   

 
   #
   # Adding chains
   #
   from py_cf_py3.chain_flow import CF_Base_Interpreter
   cf = CF_Base_Interpreter()



   cf.define_chain("delete_cimis_email_data",True)
   cf.insert_link( "link_1","WaitTod",["*",9,"*","*" ])
   cf.insert_link( "link_2","One_Step",[delete_cimis_email.delete_email_files])
   cf.insert_link( "link_3","WaitTod",["*",10,"*","*" ])
   cf.insert_link( "link_4","Reset",[])  

   cf.define_chain( "plc_auto_mode", True )
   cf.insert_link(  "link_1",  "One_Step", [ action.check_for_active_schedule ] )
   cf.insert_link(  "link_2",  "One_Step", [ sched.check_for_active_schedule ] )
   cf.insert_link(  "link_3",  "WaitEvent",[ "MINUTE_TICK" ] )
   cf.insert_link(  "link_4",  "Reset",[] )
    
   cf.define_chain("clear_done_flag",True)
   cf.insert_link(  "link_1",  "One_Step", [action.clear_done_flag ] )
   cf.insert_link(  "link_2",  "One_Step", [sched.clear_done_flag ] )
   cf.insert_link(  "link_3",  "WaitEvent",[ "MINUTE_TICK" ] )
   cf.insert_link(  "link_4",  "Reset",[] )

   #
   #
   # internet time update
   #
   #
  
   cf.define_chain("ntpd",True)
   cf.insert_link( "link_1","Log",["ntpd"] )
   cf.insert_link(  "link_2",  "One_Step", [ntpd.get_time] )
   cf.insert_link(  "link_3", "Log",["got time"] )
   cf.insert_link(  "link_4",  "WaitEvent",[ "HOUR_TICK" ] )
   cf.insert_link(  "link_5",  "Reset",[] )


   cf.define_chain("linux_test",False)
   cf.insert_link( "linkxx","Log",["test chain start"])
   cf.insert_link( "link_0", "SendEvent",  ["MINUTE_TICK",1] )
   cf.insert_link( "link_1", "WaitEvent",  ["TIME_TICK"] )
   cf.insert_link( "link_2", "SendEvent",    [ "HOUR_TICK",1 ] )
   cf.insert_link( "link_3", "WaitEventCount", ["TIME_TICK",2,0])
   cf.insert_link( "link_4", "SendEvent",    [ "DAY_TICK", 1] )



   #add_chains(cf, linux_monitoring)


 
   cf.execute()

