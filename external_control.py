# external control 
import datetime
import time
import string
import urllib2
import math
import redis
import base64
import json
import eto
import py_cf
import os
import eto
from   eto.eto import *
from   eto.cimis_request import *
import load_files


from cloud_event_queue import Cloud_Event_Queue
from watch_dog         import Watch_Dog_Client

class Eto_Management():
   def __init__(self, redis  , access_codes ):
       self.cloud_queue = Cloud_Event_Queue(redis) 
       self.redis = redis
       self.alt = 2400
       self.eto = ETO(2400,access_codes)
       self.access_codes = access_codes
       
   def verify_eto_resource_updated( self, *args ):
       if self.redis.hget("CONTROL_VARIABLES","ETO_RESOURCE_UPDATED") == "TRUE" :
          returnValue = "RESET"  
       else:
          returnValue = "DISABLE"
       print "verify eto resuorce",returnValue

       return returnValue

   def verify_empty_queue( self, *args ):
       if self.redis.llen( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE" ) != 0 :
          
          returnValue = "RESET"  
       elif self.redis.llen("QUEUES:SPRINKLER:IRRIGATION_QUEUE") != 0 :
          returnValue = "RESET"
       else:
          returnValue = "DISABLE"
       print "verify empty queue",returnValue
       return returnValue



   def calculate_daily_eto( self, *args ):
        results = self.eto.integrate_eto_data( )
        print "results",results
        self.redis.hset("CONTROL_VARIABLES","ETO",results[0]["eto"] )
        self.redis.hset("CONTROL_VARIABLES","RAIN",results[0]["rain"])
        self.redis.hset("CONTROL_VARIABLES","ETO_DATA",results[1])
        self.redis.hset("CONTROL_VARIABLES","RAIN_DATA",results[2])        
         
       
        self.update_sprinklers_time_bins_new( results[0]["eto"] )
        self.redis.hset("CONTROL_VARIABLES","ETO_RESOURCE_UPDATED","TRUE") 
  
   def clear_flag( self,chainFlowHandle, chainObj, parameters, event ):
        self.redis.hset("CONTROL_VARIABLES","ETO_RESOURCE_UPDATED","FALSE")



  
   def update_sprinklers_time_bins_new( self, eto_data ): 
        value = self.redis.hget("CONTROL_VARIABLES","ETO_RESOURCE_UPDATED")
        if value == "TRUE":
           return
        print "made it here"
        self.cloud_queue.store_event_queue( "store_eto", eto_data,status = "GREEN") 
        keys = self.redis.hkeys( "ETO_RESOURCE" )
        for j in keys:
	     try:
               temp = self.redis.hget( "ETO_RESOURCE", j )
               temp = float(temp)             
             except: 
	       temp = 0
             temp = temp + eto_data
             if temp > .3 :
               temp = .3
             self.redis.hset( "ETO_RESOURCE",j, temp )
 
        #self.redis.hset("CONTROL_VARIABLES","ETO_RESOURCE_UPDATED","TRUE") 
 

          
   def delete_email_files( self,chainFlowHandle, chainOjb, parameters, event ):  
       print( str(datetime.datetime.now())+"\n")
       print("deleteing emails \n")
       imap_username = 'lacima.ranch@gmail.com'
       imap_password = 'Gr1234gfd'
       delete_cimis_email( imap_username, imap_password )

class System_Monitoring():
   def __init__(self, redis ):
     self.redis         = redis
     self.app_files    =  load_files.APP_FILES(redis)



    
   def check_schedule_flag( self, schedule_name ):
      
      data =  self.redis.hget("SYSTEM_COMPLETED", schedule_name)
 
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
               self.redis.hset( "SYSTEM_COMPLETED", name,temp_1  ) 
    
  

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
          print "checking schedule",name
          if j["dow"][dow] != 0 :
	    
            start_time = j["start_time"]
            end_time   = j["end_time"]
    
            if self.determine_start_time( start_time,end_time ):
                 print "made it past start time",start_time,end_time
                 if self.check_schedule_flag( name ):
                     print "queue in schedule ",name
                     temp = {}
                     temp["command"]        = command
                     temp["schedule_name"]  = name
                     temp["step"]           = 0
                     temp["run_time"]       = 0
                     scratch = json.dumps(temp)
                     self.redis.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
                     temp = [1,time.time()+60*3600 ]  # +hour prevents a race condition
                     self.redis.hset( "SYSTEM_COMPLETED",name,json.dumps(temp) ) 



  
class Schedule_Monitoring():
   def __init__(self, redis ):
     self.redis         = redis
     self.app_files    =  load_files.APP_FILES(redis)



    
   def check_schedule_flag( self, schedule_name ):
      
      data =  self.redis.hget("SCHEDULE_COMPLETED", schedule_name)
 
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
               self.redis.hset( "SCHEDULE_COMPLETED", name,temp_1  ) 
    
  

   def check_for_active_schedule( self, *args):

      temp = datetime.datetime.today()
      dow_array = [ 1,2,3,4,5,6,0]
      dow = datetime.datetime.today().weekday()
      dow = dow_array[dow]
      st_array = [temp.hour,temp.minute]
      rain_day = self.redis.hget("CONTROL_VARIABLES" ,"rain_day" )
      try:
       rain_day = int( rain_day )
      except:
       rain_day = 0
       self.redis.set("CONTROL_VARIABLES", "rain_day", rain_day)
     
      if rain_day != 0:
	return
      sprinkler_ctrl = self.app_files.load_file("sprinkler_ctrl.json")
      for j in sprinkler_ctrl:
	  name = j["name"]
          print "checking schedule",name
          if j["dow"][dow] != 0 :
	    
            start_time = j["start_time"]
            end_time   = j["end_time"]
    
            if self.determine_start_time( start_time,end_time ):
                 print "made it past start time",start_time,end_time
                 if self.check_schedule_flag( name ):
                     print "queue in schedule ",name
                     temp = {}
                     temp["command"] =  "QUEUE_SCHEDULE"
                     temp["schedule_name"]  = name
                     temp["step"]           = 0
                     temp["run_time"]       = 0
                     scratch = json.dumps(temp)
                     self.redis.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
                     temp = [1,time.time()+60*3600 ]  # +hour prevents a race condition
                     self.redis.hset( "SCHEDULE_COMPLETED",name,json.dumps(temp) ) 



class Ntpd():
   def __init__( self ):
     pass

   def get_time( self, chainFlowHandle, chainObj, parameters, event ):
     os.system("ntpdate -b -s -u pool.ntp.org")

class PI_Internal_Temperature():
   def __init__( self, redis ):
       self.redis = redis

   def processor_temp(self,*args):
      temp = os.popen("vcgencmd measure_temp").readline()
      temp = temp.replace("temp=","").replace("'C\n","")
      temp = float(temp)
      temp = (9.0/5.0*temp)+32.
      self.redis.hset("CONTROLLER_STATUS","temperature",temp)
      temp = json.dumps( { "description":"main controller","data":{ "tempF":temp} } )
      
      print "pi temperature is ",temp

     
if __name__ == "__main__":
  redis_config = redis.StrictRedis(host='localhost', port=6379, db=2)
  redis_host  = redis_config.get("REDIS_SERVER_IP")
  redis_port  = redis_config.get("REDIS_SERVER_PORT")
  redis_db    = redis_config.get("REDIS_SERVER_DB")
  redis_handle = redis.StrictRedis( redis_host, redis_port, redis_db )
  action       = System_Monitoring( redis_handle )
  sched        = Schedule_Monitoring( redis_handle )
  sys_files    = load_files.SYS_FILES(redis_handle)
  access_data  = sys_files.load_file( "eto_api_setup.json")
  etm = Eto_Management( redis_handle, access_data )
  print( "made it here on startup")
  ntpd = Ntpd()
  pi_temp = PI_Internal_Temperature( redis_handle )
  wc = Watch_Dog_Client(redis_handle, "extern_ctrl","external control")
  wc.pat_wd(  )
  #
  # Adding chains
  #
  cf = py_cf.CF_Interpreter()
  

  cf.define_chain("get_current_eto",True)
  cf.insert_link( "link_1", "WaitEvent",    [ "MINUTE_TICK" ] )
  cf.insert_link( "link_2", "One_Step",     [ pi_temp.processor_temp ] )
  cf.insert_link( "link_3", "Code",         [ etm.verify_eto_resource_updated ] )
  cf.insert_link( "link_4", "Code",         [ etm.verify_empty_queue ] )
  cf.insert_link( "link_5", "One_Step",     [ etm.calculate_daily_eto ] )
  cf.insert_link( "link_6", "Reset", [] )


  #cf.define_chain("delete_cimis_email_data",True)
 
  #cf.insert_link( "link_1","WaitTod",["*",9,"*","*" ])
  #cf.insert_link( "link_2","One_Step",[etm.clear_flag])
  #cf.insert_link( "link_3","One_Step",[etm.delete_email_files])
  #cf.insert_link( "link_4","WaitTod",["*",10,"*","*" ])
  #cf.insert_link( "link_5","Reset",[])  


  cf.define_chain( "plc_auto_mode", True )
  cf.insert_link(  "link_2",  "One_Step", [ action.check_for_active_schedule ] )
  cf.insert_link(  "link_1",  "One_Step", [ sched.check_for_active_schedule ] )
  cf.insert_link(  "link_2",  "WaitEvent",[ "MINUTE_TICK" ] )
  cf.insert_link(  "link_3",  "Reset",[] )
    
  cf.define_chain("clear_done_flag",True)
  cf.insert_link(  "link_2",  "One_Step", [action.clear_done_flag ] )
  cf.insert_link(  "link_2",  "One_Step", [sched.clear_done_flag ] )
  cf.insert_link(  "link_1",  "WaitEvent",[ "MINUTE_TICK" ] )
  cf.insert_link(  "link_3",  "Reset",[] )




#  cf.define_chain("new_day_house_keeping",False)
#  cf.insert_link( "link_1","WaitTod",["*",12,"*","*" ])
#  cf.insert_link( "link_2","One_Step",[etm.do_house_keeping])
#  cf.insert_link( "link_3","WaitTod",["*",13,"*","*" ])
#  cf.insert_link( "link_4","Reset",[])
#
#  cf.define_chain("get_current_eto",False)
#  cf.insert_link( "link_1", "WaitTod", ["*",12, 20,"*" ] )
#  cf.insert_link( "link_2", "One_Step", [etm.calculate_current_eto ] )
#  cf.insert_link( "link_3", "One_Step", [etm.calculate_daily_eto ] )
#  cf.insert_link( "link_4", "WaitTod", ["*",13,50,"*" ] )
#  cf.insert_link( "link_5", "Reset", [] )
# 
 
 

#
#
# internet time update
#
#
  
  cf.define_chain("ntpd",True)
  cf.insert_link( "link_9","Log",["ntpd"] )
  cf.insert_link(  "link_1",  "One_Step", [ntpd.get_time] )
  cf.insert_link(  "link_10", "Log",["got time"] )
  cf.insert_link(  "link_2",  "WaitEvent",[ "HOUR_TICK" ] )
  cf.insert_link(  "link_3",  "Reset",[] )
#
#
# update clocks from internet
#
#

  cf.define_chain("watch_dog_thread",True)
  cf.insert_link( "link_1","WaitTod",["*","*","*",30 ])
  cf.insert_link( "link_2","One_Step",[ wc.pat_wd ])
  cf.insert_link( "link_3","WaitTod",["*","*","*",55 ])
  cf.insert_link( "link_4","Reset",[])  


  #
  # Executing chains
  #
  cf_environ = py_cf.Execute_Cf_Environment( cf )
  cf_environ.execute()



