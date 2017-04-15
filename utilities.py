# 
#
# File: utilities.py
#
#
#
#


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
import copy
import load_files
import rabbit_cloud_status_publish

from   eto.eto import *
from   eto.cimis_request import *
import load_files



#
#
#  This Class Deletes Legacy cimis emails sent to lacima ranch
#  Emails are not used as an api key now is used to access data
#
#
#



class Delete_Cimis_Email():

   def __init__(self,  email_data   ):
     
       self.email_data   = email_data
 


   def delete_email_files( self,chainFlowHandle, chainOjb, parameters, event ):  
       #print "make it here"
       if self.email_data != None: 
           IMAP_SERVER = 'imap.gmail.com'
           IMAP_PORT = '993'
           #print self.email_data
           imap_username = self.email_data["imap_username"] 
           imap_password = self.email_data["imap_password"] 
           self.imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
           self.imap.login(imap_username, imap_password)
           self.imap.select('Inbox')
           status, data = self.imap.search(None, 'ALL')
           count = sum(1 for num in data[0].split())
           print "count",count
           if count > 0 :
              self.imap.select('Inbox')
              status, data = self.imap.search(None, 'ALL')
              for num in data[0].split():
                  self.imap.store(num, '+FLAGS', r'\Deleted')
              self.imap.expunge()


     
if __name__ == "__main__":

   import time
   import construct_graph 
   import io_control.construct_classes
   import io_control.new_instrument

   graph_management = construct_graph.Graph_Management("PI_1","main_remote","LaCima_DataStore") 
   data_store_nodes = graph_management.find_data_stores()  
   data_values = data_store_nodes.values()
   # find ip and port for redis data store
   data_server_ip = data_values[0]["ip"]
   data_server_port = data_values[0]["port"]
   

    
   cimis_email_data    =  graph_management.match_relationship( "CIMIS_EMAIL", json_flag = True )[0]
 
 

   delete_cimis_email = Delete_Cimis_Email(cimis_email_data)
 
   #
   # Adding chains
   #
   cf = py_cf.CF_Interpreter()
   cf.define_chain("delete_cimis_email_data",True)
   cf.insert_link( "link_1","WaitTod",["*",9,"*","*" ])
   cf.insert_link( "link_2","One_Step",[delete_cimis_email.delete_email_files])
   cf.insert_link( "link_3","WaitTod",["*",10,"*","*" ])
   cf.insert_link( "link_4","Reset",[])  


   cf_environ = py_cf.Execute_Cf_Environment( cf )
   cf_environ.execute()



