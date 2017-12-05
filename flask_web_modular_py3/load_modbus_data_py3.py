
import os
import json
from   redis_support_py3.redis_rpc_client_py3  import Redis_Rpc_Client
class Load_Modbus_Data(object):

   def __init__( self, app, auth, request,render_template,redis_new_handle, gm ):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.render_template  = render_template
       self.redis_new_handle = redis_new_handle
       self.gm         = gm

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
       app.add_url_rule('/ajax/ping_modbus_device',"ajax_ping_modbus_device",a1)

       
       # find remote devices
       search_nodes =    gm.match_relationship_list ( [["UDP_IO_SERVER",None]], starting_set = None, property_values = None, fetch_values = False )
      
       remote_lists = gm.match_terminal_relationship("REMOTE_UNIT",starting_set = search_nodes)
       self.address_list = []
       for i in remote_lists:
          self.address_list.append(i["modbus_address"])
      

   def ping_device( self ):
       return self.render_template("modbus/modbus_ping",address_list = self.address_list)

   def modbus_current_status(self):
       return "SUCCESS"

   def modbus_basic_status( self ):
       return "SUCCESS"

   def modbus_message_queue( self ):
       return "SUCCESS"   

   def modbus_device_status( self ):
       return "SUCCESS"
       
       
   def ajax_ping_modbus_device(self):
       return self.rpc_client.send_rpc_message("ping_message" ,json.dumps() )