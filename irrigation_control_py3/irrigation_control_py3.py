  cf = py_cf.CF_Interpreter()

   cf.define_chain("reboot_message", True)  #tested
   cf.insert_link( "link_1",  "One_Step", [  clear_redis_set_keys ] )
   cf.insert_link( "link_2",  "One_Step", [ clear_redis_clear_keys ] )
   cf.insert_link( "link_2",  "One_Step",   [ plc_watch_dog.read_mode ] )
   cf.insert_link( "link_3",  "One_Step",   [ plc_watch_dog.read_mode_switch ] ) 
   cf.insert_link( "link_3",  "One_Step", [ irrigation_io_control.disable_all_sprinklers ] )
   cf.insert_link( "link_4",  "One_Step" ,[ check_for_uncompleted_sprinkler_element ] )
   cf.insert_link( "link_5",  "Terminate",  [] )




   cf.define_chain("update_time_stamp", True) #tested
   cf.insert_link( "link_1",  "WaitTime",    [10,0,0,0] )
   cf.insert_link( "link_3",  "One_Step",    [ monitor.update_time_stamp ] )
   cf.insert_link( "link_4",  "Reset",       [] )

   cf.define_chain("plc_watch_dog", True ) #TBD
   #cf.insert_link( "link_1",  "Log",        ["plc watch dog thread"] )
   #cf.insert_link( "link_2",  "One_Step",   [ plc_watch_dog.read_mode ] )
   #cf.insert_link( "link_3",  "One_Step",   [ plc_watch_dog.read_mode_switch ] ) 
   cf.insert_link( "link_4",  "One_Step",   [ plc_watch_dog.read_wd_flag  ]      )
   cf.insert_link( "link_5",  "One_Step",   [ plc_watch_dog.write_wd_flag ]      )
   cf.insert_link( "link_1", "WaitTime",    [ 30,0,0,0] ) # wait 1 seconds
   cf.insert_link( "link_7",  "Reset",    [] )

   cf.define_chain( "monitor_well_pressure", True ) #tested
   cf.insert_link( "link_1", "WaitTime", [ 1,0,0,0] ) # wait 1 seconds
   cf.insert_link( "link_2", "One_Step", [ sprinkler_control.dispatch_sprinkler_mode ] ) 
   cf.insert_link( "link_3", "Reset",    [] )
   

   cf.define_chain( "plc_monitor_control_queue", True ) #tested
   cf.insert_link( "link_1", "WaitTime", [ 1,0,0,0] ) # wait 1 seconds
   cf.insert_link( "link_2", "One_Step", [ sprinkler_control.dispatch_sprinkler_mode ] ) 
   cf.insert_link( "link_3", "Reset",    [] )
