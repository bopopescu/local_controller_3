

class IO_Control(object):

   def __init__(self,  graph_management, construct_class, redis_old_handle, redis_new_handle,new_instrument ):
       self.gm              = graph_management
       self.construct_class = construct_class
       self.find_class      = construct_class.find_class
       self.new_instrument  = new_instrument
       temp_controllers     = self.gm.match_terminal_relationship(  "REMOTE_UNIT")
       indexed_controllers  = {}
       self.ir_ctrl         = [] #irrigation controllers
       indexed_controllers = self.gm.to_dictionary(temp_controllers,"name")
       for element in temp_controllers:
           #indexed_controllers[element["name"]] = element
           
           if "irrigation" in element["function"]:
              self.ir_ctrl.append(element)

       self.mv_list = self.gm.match_terminal_relationship(  "MASTER_VALVE_CONTROLLER")
       for i in self.mv_list:
           remote = i["remote"]
           element = indexed_controllers[remote]
           
           
           if "flow_meter"  in indexed_controllers[remote]["function"]:
                pass
           else:
               raise ValueError("Remote does not support MASTER VALVE ")

       self.current_device = self.gm.match_terminal_relationship( "CURRENT_DEVICE" )[0]
       remote = self.current_device["remote"]
       if "valve_current"  in indexed_controllers[remote]["function"]:
           pass
       else:
           raise ValueError("Remote does not support MASTER VALVE ")

       temp_data = self.gm.match_terminal_relationship("IRRIGATION_DATA_ELEMENT" )
       self.ir_data = self.gm.to_dictionary(temp_data,"name")
       print(self.ir_data.keys())
 

   def measure_current( self,*args):
       controller = self.ir_ctrl[self.current_device["remote"]]
       action_class = find_class( controller["type"] )
       register     = self.current_device["register"]
       conversion   = self.current_device["conversion"]
       current      = action_class.measure_analog(  controller["modbus_address"], [register, conversion ] )
       redis_dict = self.ir_data["CURRENT"]["dict"]
       redis_key = self.ir_data["CURRENT"]["dict"]
       self.redis_old_handle.hset(redis_dict,"redis_key","OFF")
       
     

   def disable_all_sprinklers( self,*arg ):
      
       for i,item in self.irrigation_controllers.items():
           action_class = find_class(item["type"])
           action_class.disable_all_sprinklers( item["modbus_address"], [] )

              
 
   def turn_on_master_valves( self,*arg ):
       redis_dict = self.ir_data["MASTER_VALVE"]["dict"]
       redis_key = self.ir_data["MASTER_VALVE"]["key"]
       self.redis_old_handle.hset(redis_dict,"redis_key","ON")
       for i,item in self.mv_list.items():
           action_class = find_class(item["type"])
           action_class.disable_all_sprinklers( item["modbus_address"], [] )
           action_class.turn_on_valves( controller["modbus_address"], [item["master_valve"]] )
            
   def turn_off_master_valves( self,*arg ):
       redis_dict = self.ir_data["MASTER_VALVE"]["dict"]
       redis_key = self.ir_data["MASTER_VALVE"]["key"]
       self.redis_old_handle.hset(redis_dict,"redis_key","OFF")
       for i,item in self.mv_list.items():
            controller = self.ir_ctrl[item["remote"]]
            action_class = find_class( controller["type"] )
            action_class.turn_off_valves(  controller["modbus_address"], [item["master_valve"]] )


   def turn_on_cleaning_valves( self,*arg ):
       for i,item in self.mv_list.items():
            controller = self.ir_ctrl[item["remote"]]
            action_class = find_class( controller["type"] )
            action_class.turn_on_valves(  controller["modbus_address"], [item["cleaning_valve"]] )
            
   def turn_off_cleaning_valves( self,*arg ):
       for i,item in self.mv_list.items():
            controller = self.ir_ctrl[item["remote"]]
            action_class = find_class( controller["type"] )
            action_class.turn_off_valves( controller["modbus_address"], [item["cleaning_valve"]] )
    

 
 
   #
   #  Clearing Duration counter is done through a falling edge
   #  going from 1 to 0 generates the edge
   def clear_duration_counters( self,*arg ):
       for i,item in self.irrigation_controllers.items():
           action_class = find_class(item["type"])
           action_class.clear_duration_counters( item["modbus_address"], [] )


   def load_duration_counters( self, time_duration ,*arg):
       for i,item in self.irrigation_controllers.items():
           action_class = find_class(item["type"])
           action_class.load_duration_counters( item["modbus_address"], [time_duration] )

               

   def turn_on_valve( self ,io_setup ):
       # io_setup is a list of dict { "remote":xx , "bits":[1,2,3,4] }

       for i in io_setup:      
           remote        = i["remote"]
           bits          = i["bits"]  # list of outputs on remote to turn off
           controller     = self.ir_ctrl[item["remote"]]
           action_class   = find_class( controller["type"] )
           action_class.turn_on_valves(  controller["modbus_address"], bits)



      



 
