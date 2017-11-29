
import redis
import json
import base64
import time

class AlarmQueue(object):
   def __init__(self,redis_server, time_history_queue = "QUEUES:IRRIGATION:TIME_HISTORY", event_hash = "QUEUES:IRRIGAITION:EVENTS", history = 120):
   
       self.redis = redis_server
       self.time_history_queue = time_history_queue 
       self.event_hash = event_hash
     
       

   def store_past_action_queue( self, event, status ,data = None):
       log_data = {}
       log_data["event"]   = event
       log_data["data"]     = data
       log_data["time" ]    = time.time()
       log_data["status"]   = status
       json_data            = json.dumps(log_data)
      
       self.redis.lpush( self.time_history_queue , json_data)
       self.redis.ltrim( self.time_history_queue ,0, 120 )
       self.redis.hset(self.event_hash,event, log_data["time"] )
       


   def store_alarm_queue( self, event,status, data =None):
       self.store_past_action_queue( self, event, status ,data)
   
   
   def get_time_data( self ):
       temp_data = self.redis.lrange(self.time_history_queue,0,-1)
       return_data = []
       for i in temp_data:
          
          return_data.append(json.loads(i))     
       return return_data
       
       
   def get_events( self ):
       return self.redis.hgetall(self.event_hash)
       
       
   def store_event_queue( self, event, data=None ):
       self.store_past_action_queue(  event, status="GREEN" ,data=data )
  
   def update_time_stamp( self,*args ):
         self.redis.hset( "CONTROL_VARIABLES", "sprinkler_time_stamp", time.time() )
         
       

if __name__ == "__main__":
   import redis
   redis                        = redis.StrictRedis( host = "192.168.1.84", port=6379, db = 0 , decode_responses=True)

   alarm_queue = AlarmQueue(redis)
