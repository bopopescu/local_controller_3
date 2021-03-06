$(document).ready(
 function()
 {
   var controller_pin_data = {}
   function controller_pin_control()
   {
    
     var schedules_pins = {}
     var schedules = []
     var schedules_steps = {}
     var schedules_start_times = {}
     var schedules_end_times = {}
     var schedules_dow = {}
     var controller_pin_data = {}
     var composite_limit_values = {}
     var schedule_name;
     

    
  
    $("#controller_run_time").empty()
    for( var i = 5; i <= 60; i++ )
    {
          $("#controller_run_time").append('<option value='+i+'>'+i+'  minutes </option>');	
	
    }
     $("#controller_run_time")[0].selectedIndex = 0;
     $("#controller_run_time").selectmenu();
     $("#controller_run_time").selectmenu("refresh");

  
   $("#controller_pin_turn_off").bind("click",function(event,ui)
   {
       
  
      
       var result = confirm("Do you want to make mode change");
       if( result == true )
       {    // making update
            $.ajax
            ({
                    type: "POST",
                    url: '/ajax/controller_pin_turn_off.html',
                    dataType: 'json',
                    async: true,
	            contentType: "application/json",
                   
                    data: "[]",
                    success: function () 
		    {
                       alert("Changes Made");
		      
		       
                    },
                    error: function () 
		    {
                       alert('/ajax/controller_pin_turn_off.html'+"  Server Error Change not made");
		       
		       
                    }
              })
       }
     
       
   });// change start time     
   
   $("#controller_select").bind("change",function(event,ui)
   {
        var index;
	
	index = $("#controller_select")[0].selectedIndex;
        populate_pins( index );
   });
   
   
   $("#controller_pin_turn_on").bind("click",function(event,ui)
   {
       
  
       var valve_group_index;
       var valve_index;
       var run_time;
       var temp;
       
       
    $("#controller_run_time")[0].selectedIndex
       valve_group_index     =  $("#controller_select")[0].selectedIndex
       valve_index           =  $("#select_pin")[0].selectedIndex
       run_time              =  $("#controller_run_time").val()
       
       temp = controller_pin_data[ valve_group_index ].io[valve_index]
      
       var json_object = {}
     
       json_object["controller"]  = temp["controller"];
       json_object["pin"]         = temp["pin"]
       json_object["run_time"]    = run_time;

       var json_string = JSON.stringify(json_object);
       
       
       
       var result = confirm("Do you want to make mode change");
       if( result == true )
       {    // making update
            $.ajax
            ({
                    type: "POST",
                    url: '/ajax/controller_pin_turn_on.html',
	            contentType: "application/json",
                    dataType: 'json',
                    async: true,
                    //json object to sent to the authentication url
                    data: json_string,
                    success: function () 
		    {
                       alert("Changes Made");
		      
		       
                    },
                    error: function () 
		    {
                       alert('/ajax/controller_pin_turn_on.html'+"  Server Error Change not made");
		       
		       
                    }
              })
       }
     
       
   });// change start time 
     
   function populate_pins( index )
   {
     var pins;
     
     pins = controller_pin_data[index].pins;
     $("#select_pin").empty()
     for( var i = 1; i <= pins.length; i++ )
     {
          $("#select_pin").append('<option value='+i+'>valve: '+i+'   '+pins[i-1]+ ' </option>');	
	
     }
     $("#select_pin")[0].selectedIndex = 0;
     $("#select_pin").selectmenu();
     $("#select_pin").selectmenu("refresh");
   }
   
   
   function controller_pins_success( data )
   {
  
     controller_pin_data = data;
     $("#controller_select").empty()
     for( var i = 0; i < controller_pin_data.length; i++ )
     {
        $("#controller_select").append('<option value='+controller_pin_data[i].name+'>'+"valve group:  "+controller_pin_data[i].name+'</option>');	
     }
     $("#controller_select")[0].selectedIndex = 0;
     $("#controller_select").selectmenu();
     $("#controller_select").selectmenu("refresh");
     
     populate_pins( 0)

   }
   
   
   
   load_controller_pins = function()
   {
	
         $.ajax(
         {
                    type: "GET",
                    url: '/ajax/get_system_file/valve_group_assignments.json',
                    dataType: 'json',
                    async: true,
                    //json object to sent to the authentication url
                    success: controller_pins_success,
              
                    error: function () 
		    {
                       alert('/ajax/get_system_file/valve_group_assignments.json' +"   "+"Server Error Change not made");
		       
		       
                    }
         });
   }
    
    $( "#op_mode" ).bind( "change", function(event, ui) 
     {  
        var temp_index
        
	temp_index = $("#op_mode")[0].selectedIndex;
	$("#schedule_div").hide()
	switch( temp_index)
	{
	    
	    
	  case 1:  // Queue Schedule  Step Time
	      $("#schedule_div").show()
	    break;
	    


   

   

	}
     });


     $( "#change_mode" ).bind( "click", function(event, ui) 
     {
       var mode;
       var schedule_name;
       var step;
       var run_time;
       
       mode          =  $("#op_mode").val()
       valve_group_index     =  $("#controller_select")[0].selectedIndex
       valve_index           =  $("#select_pin")[0].selectedIndex
       run_time              =  $("#controller_run_time").val()
       
       temp = controller_pin_data[ valve_group_index ].io[valve_index]
      
       var json_object = {}
       json_object["command"]      = mode
       json_object["controller"]  = temp["controller"];
       json_object["pin"]         = temp["pin"]
       json_object["run_time"]    = run_time;

       var json_string = JSON.stringify(json_object);
       

     
       
       
       var result = confirm("Do you want to make mode change");
       if( result == true )
       {    // making update
            $.ajax
            ({
                    type: "POST",
                    url: "/ajax/native_mode_change",
                    dataType: 'json',
	            contentType: "application/json",
                    async: true,
                    //json object to sent to the authentication url
                    data: json_string,
                    success: function () 
		    {
                       alert("Changes Made");
		      
		       
                    },
                    error: function () 
		    {
                       alert('/ajax/mode_change'+"  Server Error Change not made");
		       
		       
                    }
              })
       }// if
       
     });// change start time


  
   load_controller_pins()
   $("#schedule_div").hide()
         
       
     
  } // end of function



  controller_pin_control();


 
 
 }
)

