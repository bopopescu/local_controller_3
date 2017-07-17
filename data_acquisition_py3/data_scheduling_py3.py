# 
#
# File: utilities.py
#
#
#
#


#
#
# File: data_acquisition.py
# Class for monitoring data acquisition
#
#
import time
import json


class Data_Acquisition(object):

   def __init__(self):
       pass

   def process_fifteen_second_data( self, chainFlowHandle,chainOjb, parameters, event):
       print ("received 15 second tick")
       self.common_process( self.fifteen_list, self.fifteen_store )
       return "CONTINUE"

   def process_minute_data( self,chainFlowHandle, chainOjb, parameters, event ):
       print ("received minute_tick")
       self.common_process( self.minute_list, self.minute_store )
       return "CONTINUE"

   def process_hour_data( self,chainFlowHandle, chainOjb, parameters, event ):
       print ("received hour tick")
       self.common_process( self.hour_list , self.hour_store)
  
       return "CONTINUE"

   def process_daily_data( self,chainFlowHandle, chainOjb, parameters, event ):
       print ("received day tick")
       self.common_process( self.daily_list , self.daily_store )
       return "CONTINUE"

   def common_process( self, data_list , store_element ):  
       if len(data_list) == 0:
          return
       
       print( "data_list", store_element['measurement'] )


       data_dict = {}
       for i in data_list:
           print(i)
           temp_data =   self.slave_interface( i)
           data_dict[i["name"]] = temp_data
       data_dict["namespace"] = store_element["namespace"]
       data_dict["time_stamp"] = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(time.time()))
 
       data_json           = json.dumps(data_dict)
       redis_key           = store_element["measurement"]
       redis_array_length  = store_element["length"]
       print( "redis_key",redis_key,redis_array_length)

       self.redis_handle.lpush(redis_key,data_json)
       self.redis_handle.ltrim(redis_key,0,redis_array_length)
       print( "print array length", self.redis_handle.llen(redis_key))
       # send data to influxdb
       self.status_queue_class.queue_message(store_element["routing_key"], data_dict )

   def execute_init_tags( self, data_list ):
        for i in data_list:
           if "init_tag" in i == True:
               self.gm.execute_cb_handlers( i["init_tag"][0], None , i["init_tag"])

   def slave_interface( self, element_descriptor ):
    
       action_function = self.load_slave_element( element_descriptor )
       if action_function != None:
            # find modbus address
            modbus_address = self.slave_dict[element_descriptor["modbus_remote"]]["modbus_address"]
            return_value = action_function( modbus_address, element_descriptor["parameters"])
       else:
            return_value = None     
       if "exec_tag" in element_descriptor:
              exec_tag = element_descriptor["exec_tag"]  
              return_value = self.gm.execute_cb_handlers( exec_tag[0], return_value,exec_tag )

       else:
            pass
       return return_value
 
   def load_slave_element(self, list_item):
       return_value = None
       
       remote = list_item["modbus_remote"]
       if remote in self.slave_dict:
           slave_element = self.slave_dict[remote]
           slave_class   = slave_element["class"]
           m_tags = slave_class.m_tags
           if list_item["m_tag"] in m_tags:
              return_value = m_tags[list_item["m_tag"]]

       return return_value
     
   
   def verify_slave_tags( self):

      for i in self.daily_list:
         self.verify_slave_element(i)

      for i in self.hour_list:
         self.verify_slave_element(i)

      for i in self.minute_list:
         self.verify_slave_element(i)
      for i in self.fifteen_list:
         self.verify_slave_element(i)


   def verify_slave_element(self, list_item):

       try:
           remote = list_item["modbus_remote"]

           if remote != "skip_controller":
                slave_element = self.slave_dict[remote]
                slave_class   = slave_element["class"]
                m_tags        = slave_class.m_tags
                m_tag_function = m_tags[list_item["m_tag"]]
           if "init_tag" in list_item:
              init_tag = list_item["init_tag"][0]

              if self.gm.verify_handler( init_tag ) == False:
                  raise ValueError("Bad init tag "+list_item["init_tag"])     
           if "exec_tag" in list_item:
              exec_tag = list_item["exec_tag"][0]

              if self.gm.verify_handler( exec_tag ) == False:
                  raise ValueError("Bad exec tag "+list_item["exec_tag"]  )   

       except:
           print( "list_item",list_item) 
           
           raise

def add_chains( cf,data_acquisition ):


   cf.define_chain("fifteen_second_list",True)
   cf.insert_link( "link_1","One_Step",[data_acquisition.process_fifteen_second_data])
   cf.insert_link( "link_2", "WaitEventCount", ["TIME_TICK",15,0])
   cf.insert_link( "link_3","Reset",[])  



   cf.define_chain("minute_list",True)
   cf.insert_link( "link_1","WaitEvent",["MINUTE_TICK" ])
   cf.insert_link( "link_2","One_Step",[data_acquisition.process_minute_data])
   cf.insert_link( "link_3","Reset",[])  


   cf.define_chain("hour_list",True)
   cf.insert_link( "link_1","WaitEvent",["HOUR_TICK" ])
   cf.insert_link( "link_2","One_Step",[data_acquisition.process_hour_data])
   cf.insert_link( "link_3","Reset",[])  

   cf.define_chain("daily_list",True)
   cf.insert_link( "link_1","WaitEvent",["DAY_TICK" ])
   cf.insert_link( "link_2","One_Step",[data_acquisition.process_daily_data])
   cf.insert_link( "link_3","Reset",[])  

def construct_class( redis_handle,
                     gm,instrument,
                     remote_classes,
                     fifteen_store,
                     minute_store,
                     hour_store,
                     daily_store,
                     fifteen_list,
                     minute_list,
                     hour_list,
                     daily_list, 
                     status_queue_class):

 
   #
   # Adding in graph call back handlers
   #
   #
   #

   status_stores = list(gm.match_terminal_relationship("CLOUD_STATUS_STORE"))
   
   queue_name    = status_stores[0]["queue_name"]

   

   slave_nodes  = list(gm.match_terminal_relationship(  "REMOTE_UNIT"))
   slave_dict    = {}
   for i in slave_nodes:
     class_inst     = remote_classes.find_class( i["type"] )
     slave_dict[i["name"]] = { "modbus_address": i["modbus_address"], "type":i["type"], "class":class_inst }
 

   
  
   
   data_acquisition = Data_Acquisition(  )
   data_acquisition.redis_handle            = redis_handle
   data_acquisition.gm                      = gm
   data_acquisition.minute_list             = minute_list
   data_acquisition.hour_list               = hour_list
   data_acquisition.daily_list              = daily_list
   data_acquisition.minute_store            = minute_store
   data_acquisition.hour_store              = hour_store
   data_acquisition.daily_store             = daily_store
   data_acquisition.instrument              = instrument
   data_acquisition.remote_classes          = remote_classes
   data_acquisition.status_queue_class      = status_queue_class
   data_acquisition.slave_dict              = slave_dict
   data_acquisition.fifteen_store           = fifteen_store
   data_acquisition.fifteen_list            = fifteen_list

   #
   #
   #  Verifying graph vs slave nodes
   #
   #
   #
   #
   data_acquisition.verify_slave_tags()
   data_acquisition.execute_init_tags( minute_list )
   data_acquisition.execute_init_tags( hour_list   )
   data_acquisition.execute_init_tags( daily_list )
   #data_acquisition.execute_init_tags( fifteen_list )


   #data_acquisition.process_hour_data( None, None,None,None )
   #data_acquisition.process_minute_data( None, None,None,None )
   #data_acquisition.process_daily_data( None,None,None,None )
   #data_acquisition.process_hour_data( None, None,None,None )
   #data_acquisition.process_minute_data( None, None,None,None )
   #data_acquisition.process_daily_data( None,None,None,None )
   return data_acquisition
