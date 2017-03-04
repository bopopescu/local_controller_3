
#
#  Node configuration for a local controller
#
#
#
#   
import os
from os import listdir
from os.path import isfile, join
import base64
import redis
import json

redis_handle                     = redis.StrictRedis( host = "localhost", port=6379, db = 2 )
if __name__ == "__main__":
   redis_handle.set("REDIS_SERVER_IP","192.168.1.82")
   redis_handle.set("REDIS_SERVER_DB",0)
   redis_handle.set("REDIS_SERVER_PORT",6379)
   redis_handle.set("PASSWORD_SERVER_IP","localhost")
   redis_handle.set("PASSWORD_SERVER_DB",2)
   redis_handle.set("PASSWORD_SERVER_PORT",6379)
   redis_handle.set("IO_SERVER_IP","192.168.1.82")
   redis_handle.set("IO_SERVER_DB",0)
   redis_handle.set("IO_SERVER_PORT",6379)

  
 
  
  
 

