# 
#
# File: eto.py
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


from cloud_event_queue import Cloud_Event_Queue
#from watch_dog         import Watch_Dog_Client

ONE_DAY = 24*3600


class Eto_Management(object):
   def __init__( self, redis_handle,eto_default, status_queue_class, eto_sources, eto_data_stores,rain_sources,rain_data_stores,eto_integrated, rain_integrated,eto_calc ):
        self.eto_default                   = eto_default
        self.redis_handle                  = redis_handle
        self.status_queue_class            = status_queue_class
        self.eto_sources                   = eto_sources
        self.eto_data_stores               = eto_data_stores
        self.rain_sources                  = rain_sources
        self.rain_data_stores              = rain_data_stores
        self.eto_calculators               = eto_calc
        self.redis_old                     = redis.StrictRedis( host = '192.168.1.82', port=6379, db = 0 )
        self.eto_update                    = False


   def check_for_eto_update( self, chainFlowHandle, chainObj, parameters, event ):
       if self.eto_update == False:
           self.update_all_bins( self, self.eto_default)
           #### send alert message 


       self.eto_update = False
       return DISABLE
       

   def generate_new_sources( self, chainFlowHandle, chainObj, parameters, event ):
       print "generate_new_sources"
       if event == "INIT":
         return "CONTINUE"
       for i in self.eto_sources:
           data_store = i["measurement"]
           self.redis_handle.lpush(data_store, "EMPTY")

       for i in self.rain_sources:
           data_store = i["measurement"]
           self.redis_handle.lpush(data_store, "EMPTY")
       return "DISABLE"  

   def make_measurement( self, chainFlowHandle, chainOjb, parameters, event ):

       if event == "INIT":
         return "CONTINUE"

       print "make measurements"
       return_value = "DISABLE"
       count = 0
       for i in self.eto_sources:
           #print i
           data_store = i["measurement"]
           data_value = redis_handle.lindex( data_store,0)
           #print "data_value",data_value,type(data_value),type(str())
           if str(data_value) == "EMPTY":
               flag, data = self.eto_calculators.eto_calc( i )
               #print "flag - data",flag,data
               if flag == True:
                   count = count + 1
                   redis_handle.lset( data_store, 0, json.dumps(data))
               else:
                   print "False ETO",i
           else:
               count = count + 1
       for i in self.rain_sources :
           data_store = i["measurement"]
           data_value = redis_handle.lindex( data_store,0)
           print "data_value",data_value,type(data_value),type(str())
           if str(data_value) == "EMPTY":
               flag, data = self.eto_calculators.rain_calc( i )
               if flag == True:
                   redis_handle.lset( data_store, 0, json.dumps(data ))
               else:
                   print "False RAIN",i          
                
       
       
       #print "count",count
       if count >= 2:
           eto_data = self.integrate_data()
          
           self.update_all_bins( eto_data)
           #### send data to cloud
           return_value = "TERMINATE"
       #print "return_value",return_value
       return return_value             

   def integrate_data( self ):
       pass

   def update_all_bins( self, eto_data):
       #self.update_eto_bins(eto_data)
       #self.update_eto_old_bins(eto_data)
       #### send data to cloud
       pass


   def update_eto_bins_new( self, eto_data ):
       pass


   def update_sprinklers_time_bins_old( self, eto_data ): 
        keys = self.redis.hkeys( "ETO_RESOURCE" )
        for j in keys:
	     try:
               temp = self.redis.hget( "ETO_RESOURCE", j )
               temp = float(temp)             
             except: 
	       temp = 0
             temp = temp + eto_data
             self.redis.hset( "ETO_RESOURCE",j, temp )

   def update_eto_bins(self, chainFlowHandle, chainOjb, parameters, event ):
       if event == "INIT":
         return "CONTINUE"


       return_value = "CONTINE"
       return return_value
      
   #
   #
   #  
   #
   def print_result_1( self, chainFlowHandle, chainOjb, parameters, event ):
       if event == "INIT":
         return "CONTINUE"

       print "reading data store"
       return_value = "CONTINE"
       count = 0
       for i in self.eto_sources:
           data_store = i["measurement"]
           data_value = redis_handle.lindex( data_store,0)
           print i["name"],data_store,data_value
           print redis_handle.llen(data_store)
           redis_handle.lpop(data_store)
           redis_handle.delete(data_store)
 
       for i in self.rain_sources :
           data_store = i["measurement"]
           data_value = redis_handle.lindex( data_store,0)
           print i["name"],data_store,data_value
           print redis_handle.llen(data_store)
           redis_handle.lpop(data_store)
           redis_handle.delete(data_store)

class ETO_Calculators( object ):
 
   def __init__( self, redis_handle ):


       self.redis_handle = redis_handle
       self.eto_handlers  = {}
       self.eto_handlers["CIMIS_SATELLITE_ETO"] = self.cimis_satellite
       self.eto_handlers["CIMIS_ETO"]   = self.cimis_eto
       self.eto_handlers["SRUC1_ETO"]   = self.sruc1_eto
       self.eto_handlers["HYBRID_SITE"] = self.hybrid_eto

       self.rain_handlers  = {}
       self.rain_handlers["CIMIS_RAIN"] = self.cimis_rain
       self.rain_handlers["SRUC1_RAIN"] = self.sruc1_rain



   def eto_calc( self, eto_source ):
      #print "made it eto_calc",eto_source["measurement_tag"]
    
      try:

         if self.eto_handlers.has_key( eto_source["measurement_tag"] ):
             
             result = self.eto_handlers[eto_source["measurement_tag"]]( eto_source)
             print "eto_calc",result
             return True, result
         else:
             print "handler is bad"
             raise ValueError("non existance handler")
      except:
         
         return False, 0.0

  

      return False,0

   def rain_calc(self, rain_source ):
       try:
         if self.rain_handlers.has_key( rain_source["measurement_tag"] ):
             result = self.rain_handlers[rain_source["measurement_tag"]]( rain_source)
             print "rain_calc",result
             return True, result
         else:
             raise ValueError("non existance handler")
       except:
         raise
         return False, 0.0
   #
   #  ETO Calculation handlers
   # 

   def cimis_satellite( self, eto_data ):
       spatial                = CIMIS_SPATIAL(eto_data )
       result                 = spatial.get_eto( time  = time.time()-24*3600  )
       return result 

   def cimis_eto( self, eto_data ):
       #print "eto_data",eto_data
       cimis_eto              = CIMIS_ETO( eto_data )
       cimis_results          = cimis_eto.get_eto(time = time.time()-24*3600)
       result                 = cimis_results["eto"]
       return result 

   def sruc1_eto(self,  eto_data ):
       messo_eto            = Messo_ETO(eto_data)
       messo_results        = messo_eto.get_daily_data(time = time.time())
       result               = self.calculate_eto(eto_data["altitude"], messo_results)
       return result 


   def hybrid_eto( self, eto_data ):
       messo_eto            = Messo_ETO(eto_data)
       messo_results        = messo_eto.get_daily_data(time = time.time())
       redis_key            = eto_data["rollover"]
       #print redis_key
       redis_data_json      = self.redis_handle.lrange(redis_key, 0,24) 
       #for i in range(0,24):
       #    print i, messo_results[i]
       if len(redis_data_json) < 24 :
           #print redis_data_json
           raise
       for i in range(0,24):
           temp = messon_result[i]
           redis_data                        = json.dumps(redis_data_json[i])
           temp["Humidity"]                  = redis_data[i]["air_humidity"]
           temp["TC"]                        = self.convert_to_C(redis_data[i]["air_temperature"])
       result = self.calculate_eto(eto_data["altitude"], messo_results)
       return result



       
   def cimis_rain( self, eto_data ):
       cimis_eto         = CIMIS_ETO( eto_data )
       cimis_results     = cimis_eto.get_eto(time = time.time()-24*3600)
       result            = cimis_results["rain"]
       return result 


   def sruc1_rain( self, eto_data ):
       messo_precp            =  Messo_Precp(eto_data)
       result                 =  messo_precp.get_daily_data(time = time.time())
       return result 

   #
   #  ETO Calculation
   #
   #
   #
   def calculate_eto( self, alt, hourly_results):
         alt = alt*0.3048
         pressure = 101.3*(((293-.0065*alt)/293)**5.26)
         ETod = 0
         day_of_year = time.localtime().tm_yday
         dr = 1+.033*math.cos(2*3.14159/365*day_of_year)
         delta = .409*math.sin(2*3.14159/365*day_of_year-1.39) 
         lat  = 3.14159/180*33.2
         omega = math.acos( -math.tan(lat)*math.tan(delta))
         ra = 24*60/3.14159*.0820*dr*((omega*math.sin(delta)*math.sin(lat))+(math.cos(delta)*math.cos(lat)*math.sin(omega) ))
         rso = (.75+2e-5*alt)*ra

         for i in hourly_results:
             #ETo COMPUTATIONAL PROCEDURE 
             #The CIMIS Penman Equation was developed for use with hourly weather data. Required input data for the ETo computation include hourly means of air temperature (Ta; units of degrees C), vapor  
             #pressure deficit (VPD; units of kilopascals: kPa), wind speed (U2; units of m/s), and net radiation (Rn: units of mm/hr of equivalent evaporation). Hourly values of ETo (EToh) in mm/hr are   
             #computed using the following: 
             #EToh = W*Rn + (1-W)*VPD*FU2              (1) 
             #where W is a dimensionless partitioning factor, and FU2 is an empirical wind function (units: mm/hr/kPa). Daily values of ETo are computed by simply summing the twenty-four hourly EToh 
             #values computed from Eq. 1 for the period ending at midnight (end of AZMET day). Specific computational procedures used to obtain the required parameters for Eq. 1 are provided below. 
             #Net Radiation (Rn) 
             #CIMIS originally measured Rn using instruments known as net radiometers. CIMIS abandoned the use of net radiometers in the early 1990s for a variety of reasons. AZMET chose not use net  
             #radiometers and has computed hourly net radiation since network inception (1986) using a simple, clear sky estimation procedure that uses solar radiation (SR) expressed in units of MJ/m*m/hr 
             #and mean hourly vapor pressure (ea; units: kPa). The procedure is provided below: 
            P = pressure
            U2 = i["wind_speed"]
           
            tc = i["TC"]
            es = .6108*math.exp(17.27*tc/(tc+273.3))
            ea = es*i["Humidity"]/100.
            VPD  = es- ea
            
            #For Daytime Conditions (SR>=0.21 MJ/m*m/hr): 
            
            SR  = i["SolarRadiationWatts/m^2"] 
            if SR > 10:
                FU2 = 0.03 + 0.0576*U2
                
                         
            else:  #For Nighttime Conditions (SR<0.21 MJ/m*m/hr): 
                
                
                FU2 = 0.125 + 0.0439*U2
                             
            
            SR = .72*SR
            Rn = SR/(694.5*(1-0.000946*tc))
            S = es*(597.4-0.571*tc)/(0.1103*(tc+273.16)**2)
            G = 0.000646*P*(1+0.000949*tc)
            W = S/(S+G)
         
            
            RL = 4.903*(10 **-9)*(.34-.14*math.sqrt(ea))*((i["TC"]+273.3)**4)*277.8/24
            RL = RL/(694.5*(1-0.000946*tc))
            ETRL = -W*RL
            ETR  = W*Rn
            EHUM = (1-W)*VPD*FU2
           
            ETH  = ETRL+ETR+EHUM
            #print ETH/25.4,EHUM,ETR,ETRL
            ETod = ETod+ETH
            
         return ETod/25.4

   def convert_to_C( self,deg_f):
       return (def_f *9.0)/5.0 + 32.0

class CIMIS_ETO(object):
  #fetch from cimis site
  def __init__( self, access_data):
     
     self.cimis_data   = access_data
     self.app_key      = "appKey="+self.cimis_data["api-key"]
     self.cimis_url    = self.cimis_data["url"]
     self.station      = self.cimis_data["station"]

  def get_eto( self,  time=time.time()-1*ONE_DAY  ): # time is in seconds for desired day
     date =  datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d')
     
     url = self.cimis_url+"?"+self.app_key+"&targets="+str(self.station)+"&startDate="+date+"&endDate="+date
     
     req = urllib2.Request(url)
     response = urllib2.urlopen(req)
     temp = response.read()
     data = json.loads(temp)
     #print "data",data
     return {"eto":float(data["Data"]["Providers"][0]["Records"][0]['DayAsceEto']["Value"]), "rain":float(data["Data"]["Providers"][0]["Records"][0]['DayPrecip']["Value"])}

class CIMIS_SPATIAL(object):
  #fetch from cimis site
  def __init__( self,access_data ):
     self.cimis_data = access_data
     self.app_key = "appKey="+self.cimis_data["api-key"]
     self.cimis_url = self.cimis_data["url"]
     self.latitude   = self.cimis_data["latitude"]
     self.longitude  = self.cimis_data["longitude"]

  def get_eto( self, time=time.time()-1*ONE_DAY  ): # time is in seconds for desired day

     date =  datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d')
     lat_long = "lat="+str(self.latitude)+",lng="+str(self.longitude)      
     url = self.cimis_url+"?"+self.app_key+"&targets="+lat_long+"&startDate="+date+"&endDate="+date
     
     req = urllib2.Request(url)
     

     response = urllib2.urlopen(req)
     
     temp = response.read()
     #print temp
     data = json.loads(temp)
     return float(data["Data"]["Providers"][0]["Records"][0]['DayAsceEto']["Value"])


class Messo_ETO(object):
   def __init__( self,access_data ):
       self.messo_data          =   access_data 
       self.app_key             =   self.messo_data["api-key"]
       self.url                 =   self.messo_data["url"]
       self.station             =   self.messo_data["station"]
       self.token               =   "&token="+self.app_key

   def get_daily_data( self, time = time.time()  ):
     date_1 =  datetime.datetime.fromtimestamp(time-1*ONE_DAY).strftime('%Y%m%d')
     date_2 =  datetime.datetime.fromtimestamp(time-0*ONE_DAY).strftime('%Y%m%d')
     start_time = "&start="+date_1+"0800"
     end_time   = "&end="+date_2+"0900"

     
     url =   self.url+ "stid="+self.station+self.token+start_time+end_time+"&vars=relative_humidity,air_temp,solar_radiation,peak_wind_speed,wind_speed&obtimezone=local"
    
     #print "url",url
     req = urllib2.Request(url) 
     #print "req",req
     response = urllib2.urlopen(req)
     temp = response.read()
     data = json.loads(temp)
     #print "data",data
     station = data["STATION"]
     #print data.keys()
     #print data["UNITS"]
     station = station[0]
     station_data = station["OBSERVATIONS"]
    
     keys = station_data.keys()
     #print "keys",keys
     return_value = []
 
     
     #print "len",len(station_data["wind_speed_set_1"])
     for i in range(0,24):
       temp                              = {}
       temp["wind_speed"]                = station_data["wind_speed_set_1"][i]
       temp["peak_wind_speed"]           = station_data["peak_wind_speed_set_1"][i]
       temp["Humidity"]                  = station_data["relative_humidity_set_1"][i]
       temp["SolarRadiationWatts/m^2"]   = station_data["solar_radiation_set_1"][i]
       temp["TC"]                        = station_data["air_temp_set_1"][i]
       return_value.append(temp)
     return return_value


class Messo_Precp(object):
   def __init__( self, access_data ):
       self.messo_data          =   access_data
       self.app_key             =   self.messo_data["api-key"]
       self.url                 =   self.messo_data["url"]
       self.station             =   self.messo_data["station"]
       self.token               =   "&token="+self.app_key


   def get_daily_data( self,  time = time.time()):
     date_1 =  datetime.datetime.fromtimestamp(time-1*ONE_DAY).strftime('%Y%m%d')
     date_2 =  datetime.datetime.fromtimestamp(time-0*ONE_DAY).strftime('%Y%m%d')
     start_time = "&start="+date_1+"0800"
     end_time   = "&end="+date_2+"0900"

     
     url =   self.url+"stid="+self.station+self.token+start_time+end_time+"&obtimezone=local"
    
     
     req = urllib2.Request(url) 
     response = urllib2.urlopen(req)
     temp = response.read()
     data = json.loads(temp)
     station = data["STATION"]
     station = station[0]
     station_data = station["OBSERVATIONS"]
    
     
     rain = float(station_data["total_precip_value_1"])/25.4
     return rain
     
     #print "len",len(station_data["wind_speed_set_1"])
     for i in range(0,24):
       temp                              = {}
       temp["wind_speed"]                = station_data["wind_speed_set_1"][i]
       temp["peak_wind_speed"]           = station_data["peak_wind_speed_set_1"][i]
       temp["Humidity"]                  = station_data["relative_humidity_set_1"][i]
       temp["SolarRadiationWatts/m^2"]   = station_data["solar_radiation_set_1"][i]
       temp["TC"]                        = station_data["air_temp_set_1"][i]
       return_value.append(temp)
     return return_value
     

       
if __name__ == "__main__":

   import time
   import construct_graph 
   import io_control.construct_classes
   import io_control.new_instrument
   import py_cf

   gm = construct_graph.Graph_Management("PI_1","main_remote","LaCima_DataStore")
   #
   # Now Find Data Stores
   #
   #
   #
   data_store_nodes = gm.find_data_stores()
   # find ip and port for redis data store
   data_server_ip   = data_store_nodes[0]["ip"]
   data_server_port = data_store_nodes[0]["port"]
   # find ip and port for ip server
   
   redis_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 12 )

   #
   #
   # find eto sources
   #
   #
   eto_sources = gm.match_relationship("ETO_ENTRY")
   #
   # find eto data stores
   eto_data_stores = gm.match_relationship("ETO_STORE")
   #
   #  Make sure that there is a data store for every eto_source
   #
   #
   eto_source_temp_list  = gm.form_key_list( "measurement", eto_sources )
   eto_store_temp_list   = gm.form_key_list( "name", eto_data_stores )
   assert len(set(eto_source_temp_list)^set(eto_store_temp_list)) == 0, "graphical data base error"
     
   #
   # find rain sources
   # 
   rain_sources = gm.match_relationship("RAIN_ENTRY")
   #
   # find rain stores
   #
   rain_data_stores = gm.match_relationship( "RAIN_STORE" )

   rain_source_temp_list  = gm.form_key_list( "measurement", rain_sources )
   rain_store_temp_list   = gm.form_key_list( "name", rain_data_stores )
   temp = gm.match_relationship("ETO_SITES")
   eto_integrated = temp[0]["measurement"]
   temp = gm.match_relationship("RAIN_SOURCES")
   rain_integrated =  temp[0]["measurement"]

   assert len(set(rain_source_temp_list)^set(rain_store_temp_list)) == 0, "graphical data base error"

   #
   #
   #
   status_stores = gm.match_relationship("CLOUD_STATUS_STORE")


   queue_name    = status_stores[0]["queue_name"]

   status_queue_class = rabbit_cloud_status_publish.Status_Queue(redis_handle, queue_name )
  
   eto_default = .20
  
   eto_calc  =  ETO_Calculators( redis_handle )
   eto = Eto_Management( redis_handle            = redis_handle,
                         eto_default             = eto_default,
                         status_queue_class      = status_queue_class,
                         eto_sources             = eto_sources, 
                         eto_data_stores         = eto_data_stores,
                         rain_sources            = rain_sources,
                         rain_data_stores        = rain_data_stores,
                         eto_calc                = eto_calc,          
                         eto_integrated          = eto_integrated, 
                         rain_integrated         = rain_integrated   )

  

   #
   # Adding chains
   #
   cf = py_cf.CF_Interpreter()

   cf.define_chain("test_generator",True)
   cf.insert_link( "link_1","SendEvent", ["DAY_TICK",0] )
   cf.insert_link( "link_2","WaitEvent", ["TIME_TICK"] ) 
   cf.insert_link( "link_3","Enable_Chain",[["eto_make_measurements"]])
   cf.insert_link( "link_4", "SendEvent",    [ "HOUR_TICK",0 ] )
   cf.insert_link( "link_5","WaitEventCount", ["TIME_TICK",2,0] )
   cf.insert_link( "link_6", "Disable_Chain",[["eto_make_measurements"]])   
   cf.insert_link( "link_7","One_Step",[eto.print_result_1] )
   cf.insert_link( "link_8", "SendEvent",    [ "HOUR_TICK",0 ] )
   cf.insert_link( "link_9","Halt",[])

   cf.define_chain("eto_time_window",True)
   cf.insert_link( "link_1","WaitEvent", ["DAY_TICK"] )
   cf.insert_link( "link_2","One_Step", [ eto.generate_new_sources ])
   cf.insert_link( "link_3","WaitTod",["*",8,"*","*" ])    
   cf.insert_link( "link_4","Enable_Chain",[["eto_time_window"]])
   cf.insert_link( "link_5","WaitTod",["*",18,"*","*" ]) 
   cf.insert_link( "link_6","One_Step", [ eto.check_for_eto_update ] )
   cf.insert_link( "link_6", "Disable_Chain",[["eto_time_window"]])
   cf.insert_link( "link_7", "Reset", [] )


   cf.define_chain("eto_make_measurements",False)
   cf.insert_link( "link_0", "Log",          ["Enabling chain"] )
   cf.insert_link( "link_1", "Code",         [ eto.make_measurement ] )
   cf.insert_link( "link_2", "WaitEvent",    [ "HOUR_TICK" ] )
   cf.insert_link( "link_3", "Reset",[])

   #
   # Executing chains
   #
   cf_environ = py_cf.Execute_Cf_Environment( cf )
   cf_environ.execute()

   
 
