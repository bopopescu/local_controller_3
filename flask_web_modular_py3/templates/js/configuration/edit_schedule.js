
var schedule_name = null;


function close_button(event, ui) 
{
          
          $("#define-schedule").show()   
          $("#edit_panel").hide();
}


function save_button(event, ui) 
{
     var i;
     var dow;
     var url;
     ;
     // fetch data from time page
     // fetch data from steps page
     // make confirm post

/*

     dow = []
     dow.push( dow_filter("sunday") )
     dow.push( dow_filter("monday") )
     dow.push( dow_filter("tuesday") )
     dow.push( dow_filter("wednesday") )
     dow.push( dow_filter("thursday") )
     dow.push( dow_filter("friday"))
     dow.push( dow_filter("saturday") )

     

     working_data["dow"] = dow;     
     working_data["start_time"]  =  eval($("#starting_time").val()) 
     working_data["end_time"] =  eval($("#ending_time").val()) 

     name = working_data["name"]
     schedule_data[name] = working_data;
     schedule_list = Object.keys(schedule_data)
     $("#define-schedule").show()   
     $("#edit_panel").hide();
     make_change(template_type,name) 
*/
 
}

function function_choice(event, ui)
{

  if( $("#function_choice").val() == "1" )
  {
      
      alert("show steps panel")
  }
  else
  {
     alert("show time panel")
  }
 
}


function set_schedule_name( sched_name )

{

   schedule_name = sched_name;
   $("#edit_panel_header").html( "Modify Setup For Schedule: "+sched_name);

}



function get_schedule_name()
{
    return schedule_name
}


function initialize_edit_functions()
{
  
  $( "#edit_panel_save" ).bind( "click", save_button );
  $( "#edit_panel_cancel" ).bind( "click", close_button );
  $( "#function_choice").bind("change", function_choice );
  // initialize time control
  // intialize steps control
  // hide pannel
}

function edit_schedule_enable()
{
    // initialize time panel
    // initalize steps pannel
    // show time panel
}

