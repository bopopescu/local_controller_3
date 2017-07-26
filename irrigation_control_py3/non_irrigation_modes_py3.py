

class non_irrigation_modes(object):

   def __init__( self ,io_control,app_files,sys_files, action_queue ):
       self.io_control = io_control
       self.app_files  = app_files
       self.sys_files  = sys_files
       self.action_queue  = action_queue

   def assemble_relevant_valves(self, *args):
       remote_dictionary = set()
       pin_dictionary    = set()
       dictionary        = {}
       
       
       print "assemble relevant valves"
       self.redis_handle.delete(  "QUEUES:SPRINKLER:RESISTANCE_CHECK_QUEUE" )
       sprinkler_ctrl = self.app_files.load_file("sprinkler_ctrl.json")

       for j in sprinkler_ctrl:
           schedule = j["name"]
           json_data  =self.app_files.load_file(j["link"]) 
           for i in json_data["schedule"]:
             for k in i:
                remote = k[0]
                pin    = str(k[1][0])
                self.update_entry( remote_dictionary, pin_dictionary, remote,pin, schedule ,  dictionary )

       master_valve = self.sys_files.load_file("master_valve_setup.json")

       for j in master_valve:
          remote = j[0]
          pin    = str(j[1][0])
          self.update_entry( remote_dictionary, pin_dictionary, remote,pin, schedule ,  dictionary )         
	         remote = j[2]
          pin    = str(j[3][0])
          self.update_entry( remote_dictionary, pin_dictionary, remote,pin, schedule ,  dictionary )  
          json_string = json.dumps(dictionary)         
          queue_object = base64.b64encode(json_string)
          self.redis_handle.set(  "SPRINKLER_RESISTANCE_DICTIONARY",queue_object)
               
   def add_resistance_entry( self, remote_dictionary,  pin_dictionary, remote, pin ):
       if ( remote not in remote_dictionary ) or ( pin not in pin_dictionary ):
               remote_dictionary.union( remote)
               pin_dictionary.union(pin)
               json_object = [ remote,pin]
               json_string = json.dumps(json_object)
               print "json_string",json_string
               queue_object = base64.b64encode(json_string)
               self.redis_handle.lpush(  "QUEUES:SPRINKLER:RESISTANCE_CHECK_QUEUE",queue_object )


   def update_entry( self,remote_dictionary, pin_dictionary, remote,pin, schedule ,  dictionary ):
       if dictionary.has_key( remote ) == False:
           dictionary[remote] = {}
       if dictionary[remote].has_key( pin ) == False:
           dictionary[remote][pin] = list(set())
       dictionary[remote][pin] = set( dictionary[remote][pin])
       dictionary[remote][pin].union(schedule) 
       dictionary[remote][pin] = list( dictionary[remote][pin])
       self.add_resistance_entry( remote_dictionary, pin_dictionary, remote, pin )

            

   def test_individual_valves( self,  chainFlowHandle,chainObj,parameters,event ):
   
       returnValue = "HALT"
      
       if event["name"] == "INIT" :
          parameters[1] = 0  # state variable

       else:
           if event["name"] == "TIME_TICK":
               if parameters[1] == 0:
               if self.redis_handle.llen(  "QUEUES:SPRINKLER:RESISTANCE_CHECK_QUEUE" ) == 0:
                  returnValue = "DISABLE"
               else:
                  compact_data = self.redis_handle.rpop(  "QUEUES:SPRINKLER:RESISTANCE_CHECK_QUEUE" )
                  json_string = base64.b64decode(compact_data)
                  json_object = json.loads(json_string)
                  print "json object",json_object
                  io_control.disable_all_sprinklers()
                  io_control.load_duration_counters( 1  ) #  1 minute
                  io_control.turn_on_valve(  [{"remote": json_object[0], "bits":[int(json_object[1])]}] ) #  {"remote":xxxx,"bits":[] } 
                  parameters[1] = 1
                  parameters[2] = json_object[0]
                  parameters[3] = json_object[1]
           else:
               io_control.measure_current()
               try:
                  coil_current = float( self.redis_handle.hget( "CONTROL_VARIABLES","coil_current" ))
                  print "coil current",coil_current
                  queue = "log_data:resistance_log:"+parameters[2]+":"+parameters[3]
                  self.redis_handle.lpush(queue, coil_current )  # necessary for web server
                  self.redis_handle.ltrim(queue,0,10)
                  queue = "log_data:resistance_log_cloud:"+parameters[2]+":"+parameters[3]
                  self.redis_handle.lpush(queue, json.dumps( { "current": coil_current, "time":time.time()} ))  #necessary for cloud
                  self.redis_io.ltrim(queue,0,10)

               except:
                   raise #should not happen
               io_control.disable_all_sprinklers()
               parameters[1] = 0
 
       return returnValue

   def clear_cleaning_sum(self, *args):
       self.redis_handle.hset("CONTROL_VARIABLES","cleaning_sum",0)

   def log_clean_filter( self,*args):
        self.self.redis_handle.hset ###?
        #self.action_queue.store_past_action_queue("CLEAN_FILTER","GREEN"  )
        self.redis_handle.hset("CONTROLLER_STATUS","clean_filter",time.time() )


   def check_well_pressure( self, *args):
       return "HALT"  #TBD at this  point
      
 
   def check_off (self, *args ):
        temp = float(self.redis_handle.hget( "CONTROL_VARIABLES","global_flow_sensor_corrected" ))
        self.redis_handle.hset("CONTROLLER_STATUS", "check_off",temp )
        if temp   > 1.:
           #self.action_queue.store_past_action_queue( "CHECK_OFF", "RED",  { "action":"bad","flow_rate":temp } )           
           return_value = "DISABLE"
        else:
           self.redis_handle.hset("CONTROL_VARIABLES","SUSPEND","OFF")
           self.redis_handle.hset("ALARMS","check_off",False)
           #self.action_queue.store_past_action_queue( "CHECK_OFF", "GREEN",  { "action":"good","flow_rate":temp } )
           return_value = "DISABLE"
        return return_value
 

   def construct_chains( self ):

       cf.define_chain("clean_filter_action_chain", False)  #tested
       cf.insert_link( "link_1",   "Log",              ["Clean Step 1"] )

       cf.insert_link( "link_3",   "One_Step",         [ io_control.disable_all_sprinklers ] )
       cf.insert_link( "link_4",   "One_Step",         [ io_control.turn_off_cleaning_valves ] )# turn off cleaning valve
       cf.insert_link( "link_5",   "One_Step",         [ io_control.turn_on_master_valves ] )# turn turn on master valve
       cf.insert_link( "link_6",   "WaitTime",         [120,0,0,0] )
       cf.insert_link( "link_1",   "Log",              ["Clean Step 3"] )
       cf.insert_link( "link_7",   "One_Step",         [ io_control.turn_on_cleaning_valves ] )# turn on cleaning valve
       cf.insert_link( "link_8",   "One_Step",         [ io_control.turn_off_master_valves ] )# turn turn off master valve
       cf.insert_link( "link_9",   "WaitTime",         [30,0,0,0] ) 
       cf.insert_link( "link_1",   "Log",              ["Clean Step 4"] ) 
       cf.insert_link( "link_10",  "One_Step",         [ io_control.turn_on_master_valves ] )# turn turn on master valve
       cf.insert_link( "link_11",  "WaitTime",         [10,0,0,0] )
       cf.insert_link( "link_1",   "Log",              ["Clean Step 5"] )
       cf.insert_link( "link_12",  "One_Step",         [ io_control.turn_off_cleaning_valves ] )# turn turn off master valve
       cf.insert_link( "link_13",  "One_Step",         [ io_control.turn_off_master_valves ] )# turn turn off cleaning valve
       cf.insert_link( "link_14",  "One_Step",         [ io_control.disable_all_sprinklers ] )
       cf.insert_link( "link_15",  "One_Step",         [ self.clear_cleaning_sum ] )
       cf.insert_link( "link_17",  "One_Step",         [ self.log_clean_filter ] )
       cf.insert_link( "link_17",  "Terminate",        [] )

       cf.define_chain("well_pressure_recovery", False ) #Tested
       cf.insert_link( "link_1",   "WaitTime",        [ 15,0,0,0]) # wait 15 second
       cf.insert_link( "link_2",   "Code",           [ self.check_well_pressure ] )
       cf.insert_link( "link_7",   "Enable_Chain",   ["well_pressure_recovery_wait" ] )
       cf.insert_link( "link_10",  "Terminate",     [] )

       cf.define_chain("well_pressure_recovery_wait", False ) #Tested
       cf.insert_link( "link_3",   "WaitTime",       [0,20,0,0] )  # 20 minute wait
       cf.insert_link( "link_9",  "SendEvent",      ["RELEASE_IRRIGATION_CONTROL"] )
       cf.insert_link( "link_10",  "Terminate",     [] )
   
       cf.define_chain("check_off_chain", False ) #tested
       cf.insert_link( "link_1",   "Log",           ["check off is active"] )
       cf.insert_link( "link_2",   "One_Step",      [ io_control.disable_all_sprinklers ] )
       cf.insert_link( "link_3",   "WaitTime",      [30,0,0,0] )
       cf.insert_link( "link_4",   "One_Step",      [ io_control.turn_on_master_valves ] )# turn turn on master valve
       cf.insert_link( "link_5",   "One_Step",      [ io_control.turn_off_cleaning_valves ] )# turn turn off master valve
       cf.insert_link( "link_6",   "WaitTime",      [300,0,0,0] ) 
       cf.insert_link( "link_7",   "Code",          [ self.check_off ] )
       cf.insert_link( "link_8",   "One_Step",      [ io_control.turn_off_master_valves ] )# turn turn on master valve
       cf.insert_link( "link_9",  "SendEvent",      ["RELEASE_IRRIGATION_CONTROL"] ) 
       cf.insert_link( "link_10",  "Terminate",     [] )


       cf.define_chain("resistance_check",False) #not tested
       cf.insert_link( "link_1",  "Log",            ["resistance check"] )
 
       cf.insert_link( "link_3",  "One_Step",       [ self.assemble_relevant_valves ] )
       cf.insert_link( "link_4",  "Code",           [ self.test_individual_valves,0,0,0 ] )
       cf.insert_link( "link_5",  "SendEvent",      ["RELEASE_IRRIGATION_CONTROL"] ) 
       cf.insert_link( "link_17", "Terminate",        [] )



