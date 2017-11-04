
import json
from .Common_Elements_py3  import Common_Elements
class Composite_Elements(object):

   def __init__( self, render_template, redis_handle, app_files ):
      self.redis_handle = redis_handle
      common_element = Common_Elements(app_files)
      self.get_schedule_data = common_element.get_schedule_data
      
   def composite_statistics(self,schedule_index, field_index):
       history = 14
       schedule_data = self.get_schedule_data()
       schedule_list = sorted(list(schedule_data.keys()))
       schedule_name = schedule_list[schedule_index]
       
       step_number = schedule_data[schedule_name]["step_number"]
       limit_list = []
       limit_exits_list = []
       for i in range(0,step_number):
              limit_list.append( "limit_data:unified:"+schedule_name+":"+str(i+1))
              limit_exits_list.append(self.redis_handle.exists(limit_list[-1]))

       step_list = []
       step_exists_list = []
       for i in range(0,step_number):
              step_list.append( "log_data:unified:"+schedule_name+":"+str(i+1))
              step_exists_list.append(self.redis_handle.exists(step_list[-1]))

       field_list = self.get_field_list(limit_list, limit_exits_list )
              
       data_object = []
       
       for i in range(0,len(step_list)):
           
           
           if step_exists_list[i] and limit_exits_list[i] :
               temp_entry = {}
               self.get_limit_data("limit_data:unified:"+schedule_name+":"+str(i+1))
               self.get_schedule_data( history,"log_data:unified:"+schedule_name+":"+str(i+1))
               temp_entry[i] = {}
               for j in field_list:
                   temp_field_element = {}
                   temp_field_element["limit"] = self.assemble_limit_data(j)
                   temp_field_element["data"]  = self.assemble_field_data(j)
 
           else:
               temp_entry = None
           data_object.append(data_object)

       print( data_object)        
       return "SUCCESS"

   def get_field_list(self, limit_list, limit_exits_list ):
       return [] 
       
   def get_limit_data(self, redis_key ):
        pass
        
   def get_schedule_data(self, history, redis_key ):
       pass

   def assemble_limit_data(self, field):
       pass

   def assemble_field_data(self,field):
       pass   
       