import json
import time



class RedisRpcServer(object):

    def __init__( self, redis_handle , redis_rpc_queue ):
       self.redis_handle = redis_handle
       self.redis_rpc_queue = redis_rpc_queue
       self.handler = {}
       

    def register_call_back( self, method_name, handler)
        self.handler[method_name] = handler
    
    def start( self ):
        response = self.redis_handle.brpop(self.redis_rpc_queue, 60 )
        if response == None:
            print("no response")
         else:
             channel      = response[0]
             request_json = response[1]
             if request_json[
  def start(self):
    print("Starting RPC server for " + self.list_name)
    while True:
      channel, request = self.client.brpop('fib')
      request = msgpack.unpackb(request, encoding='utf-8')

      print("Working on request: " + request['id'])

      result = getattr(self.klass, request['method'])(*request['params'])

      reply = {
        'jsonrpc': '2.0',
        'result': result,
        'id': request['id']
      }

      self.client.rpush(request['id'], msgpack.packb(reply, use_bin_type=True))
      self.client.expire(request['id'], 30)


RedisRpcServer('redis://localhost:6379', 'fib', Fibonacci()).start()