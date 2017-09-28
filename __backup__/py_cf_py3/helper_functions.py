class Helper_Functions:

   def __init__(self):
       pass

   #
   #  Return code functions
   #
   def terminate( self ):
      insert_link( "Terminate", [] )

   def halt(self ):
       insert_link("Halt",[] )

   def reset( self ):
       insert_link("Reset",[] )

   def chain_flow_reset( self ): 
       insert_link("Reset_Chain_Flow",[])
       


   #
   #   Manipulate Chains
   #
   def enable_chains( self, list_of_chains ):
       insert_link("Enable_Chain",[list_of_chains] )

   def disable_chains( self, list_of_chains ):
       insert_link("Disable_Chain",[list_of_chains] )

   def suspend_chains( self, list_of_chains ):
       insert_link("Suspend_Chain",[list_of_chains] )

   def resume_chains( self, list_of_chains ):
       insert_link("Resume_Chain",[list_of_chains] )

   #
   #  debug function
   #
   def log( self, debug_message ):
       insert_link( "Log",[ debug_message ] )

   #
   #  One Time Functions
   #
   def one_step( self, function,*params ):
       list_data = [function]
       list_data.extends(*params)
       insert_link("One_Step",list_data )
 
   #
   # Event Functions
   #  
   def send_event( self, event, event_data = "" ):
       insert_link("Send_Event",[event,event_data] )
       

   #
   #   Opcode which acts on an event
   #

   def check_event( self, function, event, *params ):
       list_data = [ function, event ]
       list_data.extends(*params)
       insert_link("Check_Event",list_data)

   #
   #   user function with full return code flexiability
   #
   def code( self, function, *params ):
       list_data = [ function ]
       list_data.extends(*params)
       insert_link("Code",list_data )



   #
   #   Wait  Functions
   #

   def wait_tod( self, dow="*",hour="*",minute="*",second="*" ):
       insert_link("Wait_Tod",[dow,hour,minute,second] )

   def wait_tod_ge( self, dow="*",hour="*",minute="*",second="*" ):
       insert_link("Wait_Tod_GE",[dow,hour,minute,second] )

   def wait_tod_le( self,dow="*",hour="*",minute="*",second="*" ):
       insert_link("Wait_Tod_LE",[dow,hour,minute,second] )

   def wait_event_count( self,event="TimeTick", count = 1 ):
       insert_link("Wait_Event_Count",[event, count] )

   def wait_function( self, fn ,*params):
       list_data = [fn]
       list_data.extend(*params)
       insert_link("Wait_Fn", list_data)


   #
   #   Verify Reset  Functions
   #

   def verify_tod_reset( self, dow="*",hour="*",minute="*",second="*", reset_event = None ):
       insert_link("Verify_Tod",[dow,hour,minute,second,reset_event, True] )

   def verify_tod_ge_reset( self, dow="*",hour="*",minute="*",second="*",reset_event = None ):
       insert_link("Verify_Tod_GE",[dow,hour,minute,second,reset_event,True] )

   def verify_tod_le_reset( self,dow="*",hour="*",minute="*",second="*",reset_event = None ):
       insert_link("Verify_Tod_LE",[dow,hour,minute,second,reset_event,True] )

   def verify_not_event_count_reset( self,event="TimeTick", count = 1, reset_event = None ):
       insert_link("Verify_Not_Event_Count",[event, count, reset_event,True] )

   def verify_function_reset( self, fn ,reset_event , *params):
       list_data = [fn, reset_event, reset_flag,True]
       list_data.extend(*params)
       insert_link("Verify_Fn", list_data)

   #
   #   Verify Terminate  Functions
   #
   def verify_tod_terminate( self, dow="*",hour="*",minute="*",second="*", reset_event = None ):
       insert_link("Verify_Tod",[dow,hour,minute,second,reset_event, False] )

   def verify_tod_ge_terminate( self, dow="*",hour="*",minute="*",second="*",reset_event = None ):
       insert_link("Verify_Tod_GE",[dow,hour,minute,second,reset_event,False] )

   def verify_tod_le_terminate( self,dow="*",hour="*",minute="*",second="*",reset_event = None ):
       insert_link("Verify_Tod_LE",[dow,hour,minute,second,reset_event,False] )

   def verify_not_event_count_terminate( self,event="TimeTick", count = 1, reset_event = None ):
       insert_link("Verify_Not_Event_Count",[event, count, reset_event,False] )

   def verify_function_terminate( self, fn ,reset_event , *params):
       list_data = [fn, reset_event, reset_flag,False]
       list_data.extend(*params)
       insert_link("Verify_Fn", list_data)



if __name__ == "__main__":
   pass
   
   


 