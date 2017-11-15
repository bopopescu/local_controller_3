import uuid
import json
import time


class Redis_Rpc_Server(object):

    def __init__( self, redis_handle , redis_rpc_queue ):
       self.redis_handle = redis_handle
       self.redis_rpc_queue = redis_rpc_queue
       self.handler = {}
       

    def register_call_back( self, method_name, handler):
        self.handler[method_name] = handler
    
    def start( self ):
        while True:
            try:
               input_json = self.redis_handle.rpop(self.redis_rpc_queue)
               
               if input_json == None:
                    #print("no response")
                    pass
               else:
                   input = json.loads(input_json)
                   self.process_message(  input )
                       
            except:
                 pass         
            time.sleep(.5)
                
 
    def process_message( self, input):

        id      = input["id"]
        method  =  input["method"]
        params  = input["params"]
        response = self.handler[method](params)
       
        self.redis_handle.lpush( id, json.dumps(response))        
        self.redis_handle.expire(id, 30)
 
if __name__ == "__main__":
    def echo_handler(  parameters ):
        return parameters
    
    import redis
    redis_handle = redis.StrictRedis("127.0.0.1", 6379 ,5,decode_responses = True )
    redis_rpc_server = Redis_Rpc_Server( redis_handle, "redis_rpc_server")
    redis_rpc_server.register_call_back( "echo",echo_handler )
    redis_rpc_server.start()
        
