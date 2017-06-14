
import json 
import redis
import base64



class FlowRateFunctions():

   def __init__(self , redis_handle):

       self.redis_handle = redis_handle
       self.flow_rate_sensors = self.get_flow_rate_sensor_names()
       pass
#
#   def get_flow_rate_sensor_names( self, data_file_path = "../system_data_files/global_sensors.json" ):
#       return_data = []
#       json_data=open(data_file_path)
#       data = json.load(json_data)
#       for i in data:
#           temp = []
#           temp.append(i[0])  # sensor name
#           temp.append(i[3])  # conversion rate
#           return_data.append(temp)
#
#       return json.dumps(return_data)

   def get_flow_rate_sensor_names( self, data_file_path = "../system_data_files/global_sensors.json" ):
       return_data = []
       data = self.redis_handle.hget("FILES:SYS","global_sensors.json")
       data = base64.b64decode(data)
       data      = json.loads(data)
   
       for i in data:
      
            temp = []
            temp.append(i[0])  # sensor name
            temp.append(i[3])  # conversion rate
            return_data.append(temp)
 
       return json.dumps(return_data)




   def sel_chart( self,queue):
     
       
       length            =   self.redis_handle.llen(queue)
       json_object       =   self.redis_handle.lrange(queue, 0,length )
       json_object.reverse()
       
       json_string = json.dumps(json_object)

       return json_string

   def strip_chart(self,queue,scale):

       length          = self.redis_handle.llen(queue )
       temp1            = self.redis_handle.lrange(queue, 0,length)
       temp            = [ float(x) * scale for x in temp1] 
       print "length",length
       print "queue",queue
       temp.reverse()
       json_object = {}
       json_object["queue"] = temp    
       json_string = json.dumps(json_object)
       return json_string



