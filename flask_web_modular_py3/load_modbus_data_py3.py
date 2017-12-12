
import os
import json
import datetime

class Load_Modbus_Data(object):

   def __init__( self, app, auth, request,render_template,redis_new_handle, redis_old_handle, rpc_client, address_list,logging_key ):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.render_template  = render_template
       self.redis_new_handle = redis_new_handle
       self.redis_old_handle = redis_old_handle
       self.rpc_client  = rpc_client
       self.address_list = address_list
       self.logging_key = logging_key
       
       #self.rpc_client =     Redis_Rpc_Client(redis_rpc_handle  , server_dict["redis_rpc_key"])   
       a1 = auth.login_required( self.ping_device )
       app.add_url_rule('/ping_device',"ping_device",a1)
       
       a1 = auth.login_required( self.modbus_current_status )
       app.add_url_rule("/modbus_current_status","modbus_current_status",a1)

       a1 = auth.login_required( self.modbus_basic_status )
       app.add_url_rule("/modbus_basic_status","modbus_basic_status",a1)

       a1 = auth.login_required( self.modbus_message_queue )
       app.add_url_rule("/modbus_message_queue","modbus_message_queue",a1)
       
       a1 = auth.login_required( self.modbus_device_status )
       app.add_url_rule("/modbus_device_status","modbus_device_status",a1)
       
       a1 = auth.login_required( self.ajax_ping_modbus_device )
       app.add_url_rule('/ajax/ping_modbus_device',"ajax_ping_modbus_device",a1,methods=["POST"])

       
          
      

   def ping_device( self ):
       
       return self.render_template("modbus/modbus_ping",address_list = self.address_list)

   def modbus_current_status(self):
       recent_data = json.loads(self.redis_old_handle.get("QUEUES:MODBUS_LOGGING:RECENT_DATA"))
       queue_keys = list(recent_data["queue"].keys())
       
       queue_keys.sort()
       remote_list = list(recent_data["remotes"].keys())
       temp = []
       for i in remote_list:
         temp.append(int(i))
       remote_list = temp
       remote_list.sort()
       temp = []
       for i in remote_list:
          temp.append(str(i))
       remote_list = temp
       now = datetime.datetime.now()
       date_string = now.isoformat()
       print(date_string)
       return self.render_template("modbus/current_conditions",data = recent_data,queue_keys = queue_keys, remote_list = remote_list,date_string=date_string )

   def modbus_basic_status( self ):
       return "SUCCESS"

   def modbus_message_queue( self ):
       return "SUCCESS"   

   def modbus_device_status( self ):
       return "SUCCESS"
       
       
   def ajax_ping_modbus_device(self):
      
      param            = self.request.get_json()
      remote           = param["remote"]
      
      try:
          result           = self.rpc_client.send_rpc_message( "ping_message",remote,timeout=30 )
          if result == True:
               return_value = "ping received for remote: "+remote
          else:
               return_value = "ping NOT received for remote: "+remote
      except:
          print("ping exception")
          return_value = "ping NOT received for remote: "+remote
      return json.dumps(return_value)

