


class Cluster_Control:

   def __init__( self , cf):
      self.clusters       = {}
      
      self.chain_list = set([])
      self.cf             = cf
      

   def define_cluster( self, cluster_id, list_of_chains, initial_chain):

       set_chains = set(list_of_chains)
       set_chains.add(initial_chain)
       self.validate_chain_list(list_of_chains)
      
       self.validate_cluster(cluster_id, False)
       self.clusters[cluster_id] = {}
       self.clusters[cluster_id]["initial_chain"] = initial_chain
       self.clusters[cluster_id]["chains"] = set(list_of_chains)
       self.clusters[cluster_id]["states"] = {}
       self.clusters[cluster_id]["suspension_state"] = False
       set_intersect = set_chains - self.chain_list

       if len( set_intersect ) != len(list_of_chains):
           raise ValueError("the following chains have already been defined ",(set_intersect))
       self.chain_list =  self.chain_list | set_chains
       self.clusters[cluster_id]["chains"] =  set_chains



   def define_state( self, cluster_id, state_id, list_of_chains):
       self.validate_chain_list(list_of_chains)
       set_chains = set(list_of_chains)
       self.validate_cluster(cluster_id, True)
       self.validate_state_id( cluster_id, state_id )       
       set_diff = set_chains - self.clusters[cluster_id]["chains"] 
       if len( set_diff ) != 0:
          raise ValueError("invalid states for cluster,  invalid states ",(cluster_id,state_id, set_diff))
       self.clusters[cluster_id]["states"][state_id] = set_chains

   def dump_chains( self ):
      return self.chain_list

   def dump_clusters( self):
      return self.clusters

   def validate_clusters_state(self, cf_handle ):
       return_value = []
       valid_chains = cf_handle.chain_map.keys()
       for i in self.clusters.keys():
           for j in self.clusters[i]["chains"]:
               if j not in valid_chains:
                   return_value.append(j)
               else:
                  position = cf_handle.chain_map[j]
                  cf_handle.chains[position]["auto_start"] = False
                  cf_handle.chains[position]["active"] = False
       if len( return_value ) != 0:
           raise ValueError("following chains are not valid",(return_value))


   def reset_cluster( self,cluster_id, *args):
       self.disable_cluster_states(  self.cf, self.clusters[cluster_id]["chains"])
       self.reset_cluster_states( self.cf, [self.clusters[cluster_id]["initial_chain"]] )

   def suspend_cluster( self,cluster_id, *args):
       if self.clusters[cluster_id]["suspension_state"] == False:
          self.clusters[cluster_id]["suspension_state"] = True
          for i in self.clusters[cluster_id]["chains"]:
              position = self.cf_handle.chain_map[i]
              chain    = self.cf_handle.chains[position]
              if chain["active"] == True:
                   self.cf_handle.suspend_chain_code(self, [i])

   def resume_cluster( self,cluster_id, *args):
       if self.clusters[cluster_id]["suspension_state"] == True:
          self.clusters[cluster_id]["suspension_state"] = True
          for i in self.clusters[cluster_id]["chains"]:
              position = self.cf_handle.chain_map[i]
              chain    = self.cf_handle.chains[position]
              if chain["suspended"] == True:
                   self.cf_handle.resume_chain_code(self, [i])
              
              

   # parameter[1] is the cluster id
   # parameter[2] is the state id      
   def set_configuration_reset(self, cf_handle, chainObj, parameters, event):
       cluster_id, state_id = self.validate_parameters( parameters)     
       enabled_states, disable_states = self.analyize_cluster_state( cluster_id, state_id)
       self.disable_cluster_states( cf_handle, disable_states)
       self.reset_cluster_states( cf_handle, enabled_states)
       return "DISABLE"



   # parameter[1] is the cluster id
   # parameter[2] is the state id
   def set_configuration_no_reset( self, cf_handle, chainObj, parameters, event ):
       cluster_id, state_id = self.validate_parameters( parameters)     
       enabled_states, disable_states = self.analyize_cluster_state( cluster_id, state_id)
       current_enabled_states = self.determine_enabled_states( cf_handle, enabled_states)
       states_to_reset = enabled_states - current_enabled_states
       self.disable_cluster_states( cf_handle, disable_states)
       self.reset_cluster_states( cf_handle, states_to_reset)
       return "DISABLE"


   '''
   The next set of functions are internal worker functions
   '''
   def validate_parameters( self, parameters ):
       cluster_id = parameters[0]
       state_id   = parameters[1]
       self.validate_cluster( cluster_id, True)
       self.validate_state_id( cluster_id, state_id, True)
       return cluster_id,state_id


   def determine_enabled_states( self, cf, enabled_states):
       return_value = set()
       for i in enabled_states:          
           position = cf.chain_map[i]         
           if cf.chains[position]["active"]:
               return_value.add(i)
               
       
       return return_value

   def  disable_cluster_states( self, cf, states_to_reset):
        for j in states_to_reset:
            position = cf.chain_map[j]
            cf.chains[position]["auto_start"] = False  # allow reset before chain flow starts
            cf.disable_chain_base(j)
 
   def  reset_cluster_states( self, cf, states_to_reset):

        for j in states_to_reset:
            position = cf.chain_map[j]
            cf.chains[position]["auto_start"] = True  # allow reset before chain flow starts
            cf.enable_chain_base(j)

   def validate_cluster( self, cluster_id, condition):
       if condition == True:
           
           if cluster_id not in self.clusters:
               raise ValueError("cluster_id is not defined")
       else:
           if cluster_id  in self.clusters:
               raise ValueError("cluster_id is already defined")

       
   def validate_state_id( self, cluster_id, state_id , flag = False):
       if flag == False:
           if state_id  in self.clusters[cluster_id]["states"]:
               raise ValueError("duplicate definition for cluster %s and state_id %s ",(cluster_id,state_id))
       else:
           if state_id not in self.clusters[cluster_id]["states"]:
               raise ValueError("bad state definition  ",(cluster_id,state_id))


   def validate_chain_list( self, chain_list):
       if isinstance(chain_list,list):
          pass
       else:
            raise ValueError("list of chains should be a list instead of %s", type(chain_list))

   def analyize_cluster_state( self, cluster_id, state_id ):
       total_chains = self.clusters[cluster_id]["chains"]
       enabled_chains = self.clusters[cluster_id]["states"][state_id]
       disabled_chains = total_chains - enabled_chains
       return enabled_chains, disabled_chains

if __name__ == "__main__":

   from .chain_flow    import CF_Base_Interpreter
   cf = CF_Base_Interpreter()
   cluster_control = Cluster_Control(cf)
   cf = CF_Base_Interpreter()
   test_1_list = []
   for i in range(0,10):
      test_1_list.append("Chain_1_"+str(i))
      cf.define_chain("Chain_1_"+str(i), True)
      cf.insert_link("test1", "Log", ["Chain_1 is printed"])
      cf.insert_link("test2", "Reset", [])

   cluster_control.define_cluster( "Test_1", test_1_list, "Chain_1_2")
   cluster_control.define_state( "Test_1", "state_1", ["Chain_1_1",])

   cluster_control.validate_clusters_state(cf)

   cluster_control.set_configuration_no_reset( cf,"",["Test_1","state_1"], "")

   cluster_control.set_configuration_reset( cf,"",["Test_1","state_1"], "")
  

   print(cluster_control.dump_chains())
   print(cluster_control.dump_clusters())
   for i in cf.chains:
       print(i["name"],i["active"])
 
   cf.execute()
