

class SprinklerQueueControl():
   def __init__(self,alarm_queue,redis):
       self.alarm_queue = alarm_queue
       self.redis       = redis

   #
   # This function takes data from the IRRIGATION QUEUE And Transferrs it to the IRRIGATION_CELL_QUEUE
   # IRRIGATION_CELL_QUEUE only has one element in it
   #
   def load_irrigation_cell(self,chainFlowHandle, chainObj, parameters,event ): 
       #print "load irrigation cell ######################################################################"
       ## if queue is empty the return
       ## this is for resuming an operation
       length =   self.redis.llen("QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE" )
       #print "made it here  cell ", length
       if length > 0:
           return "RESET" 

       length = self.redis.llen("QUEUES:SPRINKLER:IRRIGATION_QUEUE")
       #print "length  queue  ",length
       if length == 0:
           return "RESET"
       if self.redis.hget("CONTROL_VARIABLES","SUSPEND") == "ON":
           return "RESET"

 

       compact_data = self.redis.rpop(  "QUEUES:SPRINKLER:IRRIGATION_QUEUE" )
       json_string = base64.b64decode(compact_data)
       json_object = json.loads(json_string)

      
       
       if json_object["type"] == "RESISTANCE_CHECK":
           chainFlowHandle.enable_chain_base( ["resistance_check"])
           self.redis.hset("CONTROL_VARIABLES","SUSPEND","ON")
           return "RESET"
       
       
       if json_object["type"] == "CHECK_OFF":
           chainFlowHandle.enable_chain_base( ["check_off_chain"])
           self.redis.hset("CONTROL_VARIABLES","SUSPEND","ON")
           return "RESET"

       if json_object["type"] == "CLEAN_FILTER":
           chainFlowHandle.enable_chain_base( ["clean_filter_action_chain"])
           self.redis.hset("CONTROL_VARIABLES","SUSPEND","ON")
           return "RESET"
 
       if json_object["type"] == "IRRIGATION_STEP":
           #print "irrigation step"
           self.redis.lpush( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE", compact_data )
       '''    
       if json_object["type"] == "START_SCHEDULE" :
           self.redis.set( "schedule_step_number", json_object["step_number"] ) 
           self.store_event_queue( "irrigation_schedule_start", json_object )
  
       if json_object["type"] == "END_SCHEDULE" :
           self.store_event_queue( "irrigation_schedule_stop", json_object )
       '''
       #print "load irrigation cell   CONTINUE"
       return "DISABLE"





class SprinklerControl():
   def __init__(self, irrigation_control,alarm_queue,redis):
       self.irrigation_control                    = irrigation_control
       self.alarm_queue                           = alarm_queue
       self.redis                                 = redis
       self.commands = {}
       self.commands["OFFLINE"]                   = self.go_offline          
       self.commands["QUEUE_SCHEDULE"]            = self.queue_schedule
       self.commands["QUEUE_SCHEDULE_STEP"]       = self.queue_schedule_step     
       self.commands["QUEUE_SCHEDULE_STEP_TIME"]  = self.queue_schedule_step_time
       self.commands["RESTART_PROGRAM"]           = self.restart_program         #tested   
       self.commands["NATIVE_SCHEDULE"]          = self.queue_schedule_step_time      
       self.commands["NATIVE_SPRINKLER"]          = self.direct_valve_control       
       self.commands["CLEAN_FILTER"]              = self.clean_filter            #tested    
       self.commands["OPEN_MASTER_VALVE"]         = self.open_master_valve       #tested     
       self.commands["CLOSE_MASTER_VALVE"]        = self.close_master_valve      #tested    
       self.commands["RESET_SYSTEM"]              = self.reset_system            #tested    
       self.commands["CHECK_OFF"]                 = self.check_off               #tested          
       self.commands["SUSPEND"]                   = self.suspend                 #tested   
       self.commands["RESUME"  ]                  = self.resume                  #tested    
       self.commands["SKIP_STATION"]              = self.skip_station     
       self.commands["RESISTANCE_CHECK"]          = self.resistance_check           
       self.app_files                              =  load_files.APP_FILES(redis)

   def dispatch_sprinkler_mode(self,chainFlowHandle, chainObj, parameters,event):


           #try: 
               length = self.redis.llen( "QUEUES:SPRINKLER:CTRL")
               #print length
               if length > 0:
                  data = self.redis.rpop("QUEUES:SPRINKLER:CTRL") 
                  data = base64.b64decode(data)
                  object_data = json.loads(data )
                  #print object_data["command"]
                  print "object_data",object_data
                  if self.commands.has_key( object_data["command"] ) :
                       self.commands[object_data["command"]]( object_data,chainFlowHandle, chainObj, parameters,event )
                  else:
                      self.alarm_queue.store_past_action_queue("Bad Irrigation Command","RED",object_data  )
                      raise
           #except:
               #print "exception in dispatch mode"
               #quit()
      


   def suspend( self, *args ):
       self.alarm_queue.store_past_action_queue("SUSPEND_OPERATION","YELLOW"  )
       self.irrigation_control.turn_off_master_valves()
       self.irrigation_control.disable_all_sprinklers()
       self.redis.hset("CONTROL_VARIABLES","SUSPEND","ON")

   def resume( self, *args ):
       self.alarm_queue.store_past_action_queue("RESUME_OPERATION","GREEN"  )
       self.redis.hset("CONTROL_VARIABLES","SUSPEND","OFF")

   def skip_station( self, *args ):
       self.alarm_queue.store_past_action_queue("SKIP_STATION","YELLOW" ,{"skip: on"} )
       self.redis.hset("CONTROL_VARIABLES","SKIP_STATION","ON" )


   def resistance_check( self, object_data, chainFlowHandle, chainObj, parameters, event ):
        json_object = {}
        json_object["type"]   = "RESISTANCE_CHECK"
        json_string = json.dumps( json_object)
        compact_data = base64.b64encode(json_string)
        self.redis.lpush(  "QUEUES:SPRINKLER:IRRIGATION_QUEUE", compact_data )
        alarm_queue.store_past_action_queue( "RESISTANCE_CHECK", "GREEN",  { "action":"start" } )        


   def check_off( self,object_data,chainFlowHandle, chainObj, parameters,event ):
        json_object = {}
        json_object["type"]            = "CHECK_OFF"
        json_string = json.dumps( json_object)
        compact_data = base64.b64encode(json_string)
        self.redis.lpush(  "QUEUES:SPRINKLER:IRRIGATION_QUEUE", compact_data )
        alarm_queue.store_past_action_queue( "CHECK_OFF", "GREEN",  { "action":"start" } )        

   def clean_filter( self, object_data,chainFlowHandle, chainObj, parameters,event ):
        json_object = {}
        json_object["type"]  = "CLEAN_FILTER"
        json_string = json.dumps( json_object)
        compact_data = base64.b64encode(json_string)
        self.redis.lpush(  "QUEUES:SPRINKLER:IRRIGATION_QUEUE", compact_data )
        alarm_queue.store_past_action_queue( "CLEAN_FILTER", "GREEN",  { "action":"start" } )        

  
 
   def go_offline( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       self.alarm_queue.store_past_action_queue("OFFLINE","RED"  )
       self.redis.hset("CONTROL_VARIABLES","sprinkler_ctrl_mode","OFFLINE")
       self.irrigation_control.turn_off_master_valves()
       self.irrigation_control.disable_all_sprinklers()
       self.clear_redis_sprinkler_data()
       self.clear_redis_irrigate_queue()
       self.redis.hset( "CONTROL_VARIABLES","schedule_name","OFFLINE")
       self.redis.hset( "CONTROL_VARIABLES","current_log_object",  None )
       self.redis.hset( "CONTROL_VARIABLES","flow_log_object", None )          ### not sure of
       self.redis.hset( "CONTROL_VARIABLES","SUSPEND","ON")
       chainFlowHandle.disable_chain_base( ["monitor_irrigation_job_queue","monitor_irrigation_cell"])
       chainFlowHandle.enable_chain_base( ["monitor_irrigation_job_queue"])
  
   def queue_schedule( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       
       self.schedule_name =  object_data["schedule_name"]
       self.load_auto_schedule(self.schedule_name)
       #self.redis.hset("CONTROL_VARIABLES","SUSPEND","OFF")  
       self.redis.hset("CONTROL_VARIABLES","SKIP_STATION","OFF") 
       self.alarm_queue.store_past_action_queue("QUEUE_SCHEDULE","GREEN",{ "schedule":self.schedule_name } ) 
    
   
   def queue_schedule_step( self,  object_data,chainFlowHandle, chainObj, parameters,event ):
       
       self.schedule_name =  object_data["schedule_name"]
       self.schedule_step =  object_data["step"]
       self.schedule_step =   int(self.schedule_step)
       self.alarm_queue.store_past_action_queue("QUEUE_SCHEDULE_STEP","GREEN",{ "schedule":self.schedule_name,"step":self.schedule_step } )
       #print "queue_schedule",self.schedule_name,self.schedule_step
       self.load_step_data( self.schedule_name, self.schedule_step ,None,True ) 
       #self.redis.hset("CONTROL_VARIABLES","SUSPEND","OFF")
       self.redis.hset("CONTROL_VARIABLES","SKIP_STATION","OFF")  
    

 
   def queue_schedule_step_time( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       self.schedule_name              = object_data["schedule_name"]
       self.schedule_step        =  object_data["step"]
       self.schedule_step_time   =  object_data["run_time"]
       self.alarm_queue.store_past_action_queue("DIAGNOSTICS_SCHEDULE_STEP_TIME","YELLOW" , {"schedule_name":self.schedule_name, "schedule_step":self.schedule_step,"schedule_time":self.schedule_step_time})
       self.schedule_step             = int(self.schedule_step)
       self.schedule_step_time        = int(self.schedule_step_time)  
       self.irrigation_control.turn_off_master_valves()
       self.irrigation_control.disable_all_sprinklers()
       self.clear_redis_sprinkler_data()
       self.clear_redis_irrigate_queue()

 
       self.load_step_data( self.schedule_name, self.schedule_step, self.schedule_step_time,False ) 
       self.redis.hset("CONTROL_VARIABLES","SUSPEND","OFF")
       self.redis.hset("CONTROL_VARIABLES","SKIP_STATION","OFF")  
       
    
     

   def direct_valve_control( self,  object_data,chainFlowHandle, chainObj, parameters,event ):      
       remote                = object_data["controller"] 
       pin                   = object_data["pin"]         
       schedule_step_time    = object_data["run_time"]  
       
       pin = int(pin)
       schedule_step_time = int(schedule_step_time) 
       self.alarm_queue.store_past_action_queue("DIRECT_VALVE_CONTROL","YELLOW" ,{"remote":remote,"pin":pin,"time":schedule_step_time }) 
       #print "made it here",object_data
       self.irrigation_control.turn_off_master_valves()
       self.irrigation_control.disable_all_sprinklers()
       self.clear_redis_sprinkler_data()
       self.clear_redis_irrigate_queue()
       #print "direct_valve_control",remote,pin,schedule_step_time
       self.load_native_data( remote,pin,schedule_step_time)
       self.redis.hset("CONTROL_VARIABLES","SUSPEND","OFF")
       self.redis.hset("CONTROL_VARIABLES","SKIP_STATION","OFF")  
 
       


   def open_master_valve( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       self.alarm_queue.store_past_action_queue("OPEN_MASTER_VALVE","YELLOW" )
       self.irrigation_control.turn_on_master_valves()
       chainFlowHandle.enable_chain_base([ "monitor_master_on_web"])

     
  
   def close_master_valve( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       self.alarm_queue.store_past_action_queue("CLOSE_MASTER_VALVE","GREEN"  )
       chainFlowHandle.disable_chain_base( ["manual_master_valve_on_chain"])
       chainFlowHandle.disable_chain_base( ["monitor_master_on_web"])
       self.irrigation_control.turn_off_master_valves()
      
    
 


   def  reset_system( self, *args ):
      self.alarm_queue.store_past_action_queue("REBOOT","RED"  )
      self.redis.hset( "CONTROL_VARIABLES","sprinkler_ctrl_mode","RESET_SYSTEM")
      os.system("reboot")  


   def restart_program( self, *args ):
       self.alarm_queue.store_past_action_queue("RESTART","RED"  )
       self.redis.hset( "CONTROL_VARIABLES","sprinkler_ctrl_mode","RESTART_PROGRAM")
       quit()
       

   def clear_redis_irrigate_queue( self,*args ):
       #print "clearing irrigate queue"
       self.redis.delete( "QUEUES:SPRINKLER:IRRIGATION_QUEUE" )
       self.redis.delete( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE")


   def clear_redis_sprinkler_data(self):
       self.redis.hset("CONTROL_VARIABLES", "sprinkler_ctrl_mode","OFFLINE")
       self.redis.hset( "CONTROL_VARIABLES","schedule_name","offline" )
       self.redis.hset("CONTROL_VARIABLES", "schedule_step_number",0 )
       self.redis.hset("CONTROL_VARIABLES", "schedule_step",0 )
       self.redis.hset("CONTROL_VARIABLES", "schedule_time_count",0 )
       self.redis.hset( "CONTROL_VARIABLES","schedule_time_max",0 )


   def load_auto_schedule( self, schedule_name):
       schedule_control = self.get_json_data( schedule_name )
       step_number      = len( schedule_control["schedule"] )
       ###
       ### load schedule start
       ###
       ###
       #json_object = {}
       #json_object["type"]            = "START_SCHEDULE"
       #json_object["schedule_name"]   =  schedule_name
       #json_object["step_number"]     =  step_number
       #json_string = json.dumps( json_object)
       #self.redis.lpush( "QUEUES:SPRINKLER:IRRIGATION_QUEUE", json_string )
       ###
       ### load step data
       ###
       ###
       for i in range(1,step_number+1):
           self.load_step_data( schedule_name, i ,None,True )
       ###
       ### load schedule end
       ###
       ###
       #json_object = {}
       #json_object["type"]            = "END_SCHEDULE"
       #json_object["schedule_name"]   =  schedule_name
       #json_object["step_number"]     =  step_number
       #json_string = json.dumps( json_object)
       #self.redis.lpush( "QUEUES:SPRINKLER:IRRIGATION_QUEUE", json_string  )
     
  





   # note schedule_step_time can be None then use what is in the schedule
   def load_step_data( self, schedule_name, schedule_step,  schedule_step_time ,eto_flag ):
       #print "load step data schedule name ----------------->",schedule_name, schedule_step, schedule_step_time 
         
       temp = self.get_schedule_data( schedule_name, schedule_step)
       if temp != None :
           schedule_io = temp[0]
           schedule_time = temp[1]
           if  schedule_step_time == None:
               schedule_step_time = schedule_time
           json_object = {}
           json_object["type"]            = "IRRIGATION_STEP"
           json_object["schedule_name"]   =  schedule_name
           json_object["step"]            =  schedule_step
           json_object["io_setup"]        =  schedule_io
           json_object["run_time"]        =  schedule_step_time
           json_object["elasped_time"]    =  0
           json_object["eto_enable"]      =  eto_flag
           json_string = json.dumps( json_object)
           compact_data = base64.b64encode(json_string)
           #print "load step data ===== step data is queued"
           self.redis.lpush(  "QUEUES:SPRINKLER:IRRIGATION_QUEUE", compact_data )
          
       else:
           self.store_event_queue( "non_existant_schedule", json_object )
           raise  # non schedule



   # this is for loading user specified data
   def load_native_data( self, remote,bit,time ):
       json_object = {}
       json_object["type"]            =  "IRRIGATION_STEP"
       json_object["schedule_name"]   =  "MANUAL"
       json_object["step"]            =  1
       json_object["io_setup"]        =  [{ "remote":remote, "bits":[bit] }]
       json_object["run_time"]        =  time
       json_object["elasped_time"]    =  0
       json_object["eto_enable"]      =  False
       json_string = json.dumps( json_object)    
       compact_data = base64.b64encode(json_string)
       #print "native load",json_string
       self.redis.lpush( "QUEUES:SPRINKLER:IRRIGATION_QUEUE", compact_data)
       #print self.redis.llen("QUEUES:SPRINKLER:IRRIGATION_QUEUE")


   def get_schedule_data( self, schedule_name, schedule_step):
       schedule_control = self.get_json_data( schedule_name )

       if schedule_control != None:
           io_control = schedule_control["schedule"][schedule_step -1] 
           m               = io_control[0]
           schedule_time   = m[2]
           # format io_control
           new_io_control = []
           for i in io_control:
         
              temp = { }
              temp["remote"] = i[0]
              temp["bits"]  =  i[1]
              new_io_control.append(temp)
           return [ new_io_control, schedule_time ]
       return None
 
   def get_json_data( self, schedule_name ):
       #print("get json data ",schedule_name)
       sprinkler_ctrl = self.app_files.load_file("sprinkler_ctrl.json")
    
       for j in sprinkler_ctrl :  
           if j["name"] == schedule_name:
               json_data=open("app_data_files/"+j["link"]) 
               json_data = json.load(json_data)
               #print "json data",json_data
               return json_data    
       return None
      



if __name__ == "__main__":
   pass