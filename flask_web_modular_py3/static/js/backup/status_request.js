 
 
function system_state_init()
{    var g,h,i
     var alarm_data;
     var  queue_interval_id;
     var  nintervalId;
     var data = [];
     var conversion_factor_index;
     var conversion_factor;
     var conversion_factor_array;


     var ajax_success = function(data)
     {
       var temp
       var temp_1
       var tempDate
      

       var date = new Date( data.sprinkler_time_stamp  * 1000);
       tempDate = new Date()
       
       $("#time_stamp").html("Time:  "+tempDate.toLocaleDateString() + "   " + tempDate.toLocaleTimeString() )

       $("#controller_time_stamp").html("Ctr Time: "+ date.toLocaleDateString() + "   " + date.toLocaleTimeString() )
       $("#flow_rate").html("GPM:  "+parseFloat(data.global_flow_sensor_corrected).toFixed(2));
       $("#op_mode_a").html("Mode: "+data.sprinkler_ctrl_mode)
       $("#schedule").html("Schedule: "+data.schedule_name)
       $("#step").html("Step:   "+data.schedule_step)
       $("#time").html("Step Time:  "+data.schedule_time_max)
       $("#duration").html("Duration: "+parseFloat(data.schedule_time_count).toFixed(2)) 
       $("#rain_day").html("Rain Day: "+data.rain_day)
       $("#coil_current").html("Coil ma: "+parseFloat(data.coil_current).toFixed(2))
       $("#master_valve").html("Master Valve: "+data.MASTER_VALVE_SETUP )
       $("#eto_management").html("ETO Management: "+data.ETO_MANAGE_FLAG )
       $("#suspend").html("Suspension State:  "+data.SUSPEND )
       $("clean_filter_limit").html("Suspension State:  "+data.SUSPEND )
       $("#suspend").html("Suspension State:  "+data.SUSPEND )
       $("#clean_filter_limit").html("Filter Cleaning Limit (Gallon):  "+parseFloat(data.CLEANING_INTERVAL).toFixed(2) )
       $("#clean_filter_value").html("Filter Cleaning Accumulation (GPM):  "+parseFloat(data.cleaning_sum).toFixed(2 ))


     }

     status_request = function()
     {
            json_object = {}
            json_object["hash_name"] = "CONTROL_VARIABLES"
            json_object["key_list"] = ["sprinkler_time_stamp","global_flow_sensor_corrected", "sprinkler_ctrl_mode","schedule_name","schedule_step","schedule_time_max",
                        "schedule_time_count","rain_day","coil_current","MASTER_VALVE_SETUP","ETO_MANAGE_FLAG","SUSPEND","CLEANING_INTERVAL","cleaning_sum" ]
            var json_string = JSON.stringify(json_object);
            
            $.ajax({
                    type: "POST",
                    url: '/ajax/get_redis_hkeys',
                    dataType: 'json',
                    async: true,
                    contentType: "application/json",
                    data: json_string,
                    success: ajax_success,
                    error: function () 
		    {
		      
                       alert('/ajax/get_redis_hkeys'+"  Server Error Request Not Successful");
		   
		       
                    }
              })
           
	  
     }
 
    

   $( "#status_panel"  ).bind({ popupafteropen: status_request })


  } 
system_state_init()

