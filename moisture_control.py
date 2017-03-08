# external control 
import datetime
import time
import string
import urllib2
import math
import redis
import base64
import json

import py_cf
import os

import load_files




class Moisture_Control():
   def __init__(self, redis_handle  , plc_address , psoc_moisture): 
       self.redis_handle           = redis_handle
       self.plc_address     = plc_address
       self.psoc_moisture   = psoc_moisture
       self.redis_handle.hset("MOISTURE_CONTROL","MANUAL_UPDATE",0 )

   def update_moisture_readings( self,chainFlowHandle, chainOjb, parameters, event ):
       time_stamp = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(time.time()))
       print "time_stamp",time_stamp
       self.redis_handle.hset("MOISTURE_CONTROL","TIME_STAMP",time.time())
       try:
         print "updating moisture reading"
         self.psoc_moisture.check_one_wire_presence( self.plc_address )
         time.sleep(.3)
         self.psoc_moisture.make_soil_temperature( self.plc_address )
         time.sleep(.3)
         self.psoc_moisture.make_air_temp_humidity( self.plc_address )
         time.sleep(.3)
         temp = self.psoc_moisture.check_status( self.plc_address )
         psoc_moisture.force_moisture_reading(40)
         time.sleep(.3)

         
         self.redis_handle.hset("MOISTURE_CONTROL",'ONE_WIRE_DEVICE_FOUND',temp['ONE_WIRE_DEVICE_FOUND'] )
         
         temp =  self.psoc_moisture.read_moisture_control( self.plc_address )
         print "temp", self.psoc_moisture.read_moisture_resistive_data( self.plc_address )
         self.redis_handle.hset("MOISTURE_CONTROL",'AIR_HUMIDITY_FLOAT',temp["AIR_HUMIDITY_FLOAT"])
         
         self.redis_handle.hset("MOISTURE_CONTROL",'MOISTURE_SOIL_TEMP_FLOAT',temp["MOISTURE_SOIL_TEMP_FLOAT"])
         self.redis_handle.hset("MOISTURE_CONTROL",'AIR_TEMP_FLOAT',temp["AIR_TEMP_FLOAT"] )
         
         self.redis_handle.hset("MOISTURE_CONTROL","MOISTURE_CONFIGURATION",json.dumps( self.psoc_moisture.read_moisture_configuration( self.plc_address )))
         self.redis_handle.hset("MOISTURE_CONTROL","MOISTURE_DATA",json.dumps(self.psoc_moisture.read_moisture_data( self.plc_address ) ))
         self.redis_handle.hset("MOISTURE_CONTROL","MOISTURE_RESISTIVE_DATA", json.dumps(self.psoc_moisture.read_moisture_resistive_data( self.plc_address )))
         self.redis_handle.hset("MOISTURE_CONTROL","READ_STATUS", "Communication was successful at "+time_stamp)
          
       except:
          print "exception handler"
          self.redis_handle.hset("MOISTURE_CONTROL","READ_STATUS","Communications problems with moisture plc at "+time_stamp)
       print self.redis_handle.hgetall("MOISTURE_CONTROL")
       return "CONTINUE"


   def check_update_flag( self,chainFlowHandle, chainOjb, parameters, event ):

       if event == "INIT":
         return "CONTINUE"

       update_flag = self.redis_handle.hget("MOISTURE_CONTROL","MANUAL_UPDATE")
       update_flag = int(update_flag)
       
       if update_flag == 0:
           return "RESET"
       else:
           print "update flag is not zero"
           self.redis_handle.hset("MOISTURE_CONTROL","MANUAL_UPDATE",0)
           return "DISABLE"


     
if __name__ == "__main__":
  
  redis_handle = redis.StrictRedis( host = '192.168.1.82', port=6379, db = 0 )
  import moisture.new_instrument_network
  import moisture.psoc_4m_moisture_sensor_network 
  import time
  new_instrument  =  moisture.new_instrument_network.new_instrument_network()
  new_instrument.set_ip(ip= "192.168.1.82", port = 5005)       
  psoc_moisture = moisture.psoc_4m_moisture_sensor_network.PSOC_4M_MOISTURE_UNIT( new_instrument )

  moisture = Moisture_Control( redis_handle, 40, psoc_moisture )
  moisture.update_moisture_readings(None,None,None, None ) #populate data
  #
  # Adding chains
  #
  cf = py_cf.CF_Interpreter()
  

  cf.define_chain("update_moisture_readings",True)
  cf.insert_link( "link_1", "WaitEvent",    [ "HOUR_TICK" ] )
  cf.insert_link( "link_2", "One_Step",     [  moisture.update_moisture_readings ] )
  cf.insert_link( "link_3", "Reset", [] )


  cf.define_chain("check_for_moisture_update",True)
  cf.insert_link( "link_1", "WaitEvent",    [ "TIME_TICK" ] )
  cf.insert_link( "link_2", "Code",         [ moisture.check_update_flag ] )
  cf.insert_link( "link_3", "One_Step",      [ moisture.update_moisture_readings ] )
  cf.insert_link( "link_4", "Reset", [] )




 
 
 

#  cf.define_chain("watch_dog_thread",True)
#  cf.insert_link( "link_1","WaitTod",["*","*","*",30 ])
#  cf.insert_link( "link_2","One_Step",[ wc.pat_wd ])
#  cf.insert_link( "link_3","WaitTod",["*","*","*",55 ])
#  cf.insert_link( "link_4","Reset",[])  


  #
  # Executing chains
  #
  cf_environ = py_cf.Execute_Cf_Environment( cf )
  cf_environ.execute()



