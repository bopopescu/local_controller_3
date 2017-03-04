
import time
import json
import base64
import redis
import sys

class Cloud_Event_Queue():
   def __init__(self,redis):
        self.redis = redis

   def store_event_queue( self, event, data,status ="RED" ):
          log_data = {}
          log_data["event"] = event
          log_data["data"]  = data
          log_data["time"]  = time.time()
          log_data['status'] = status
          json_data = json.dumps(log_data)
          json_data = base64.b64encode(json_data)
          self.redis.lpush( "QUEUES:CLOUD_ALARM_QUEUE", json_data)
          self.redis.ltrim(  "QUEUES:CLOUD_ALARM_QUEUE", 0,800)
          self.redis.lpush( "QUEUES:SYSTEM:PAST_ACTIONS", json_data)
          self.redis.ltrim(  "QUEUES:SYSTEM:PAST_ACTIONS", 0,800)
          

if __name__ == "__main__":
   redis_config = redis.StrictRedis(host='localhost', port=6379, db=2)
   redis_password_ip = redis_config.get("PASSWORD_SERVER_IP")
   redis_password_db = redis_config.get("PASSWORD_SERVER_DB")
   redis_password_port = redis_config.get("PASSWORD_SERVER_PORT")
   redis_handle        = redis.StrictRedis( redis_password_ip, 6379, redis_password_db )
   cloud_event_queue = Cloud_Event_Queue( redis_handle )
   event   =  sys.argv[1]
   process =  sys.argv[2]
   #print "event",event,"process",process
   data = { "action":"reboot" ,"process":process}
   cloud_event_queue.store_event_queue( event,data )
   redis_handle.hincrby("CONTROLLER_STATUS", "system_resets")    
