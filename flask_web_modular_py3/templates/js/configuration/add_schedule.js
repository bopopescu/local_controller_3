function check_duplicate( new_schedule )
{   var i;
       
    for( i = 0; i < schedule_list.length; i++ )
    {
          if( schedule_list[i] == new_schedule )
          {
             return false;
           }
     }
     return true;
} 


function add_function(event, ui) 
{
   new_schedule = $("#new_schedule" ).val()
   if( check_duplicate( new_schedule ) )
   {
          alert(new_schedule)

           
          load_new_schedule_data( new_schedule )
          //load_controls( working_data )
          $("#define-schedule").hide()
          $("#edit_panel").show();
          
          
          
    }
    else
    {
       alert("duplicate schedule "+ $("#new_schedule" ).val())
    }
   
}

function load_new_schedule_data( schedule)
{
      working_data = {} 
      working_data["description"]      = ""
      working_data["step_number"]      = 0
      working_data["start_time"]       = [0, 0]
      working_data["link"]             = schedule+".json"
      working_data["end_time"]         = [0, 0]
      working_data["controller_pins"]  = []
      working_data["steps"]   = []
      working_data["dow"]     = [0, 0, 0, 0, 0, 0, 0] 
      //working_data["name"]    = edit_schedule
}

$(document).ready(
 function()
 {
    
      
      $( "#action_button" ).bind( "click", add_function );
      initialize_edit_functions();


  //initialize_edit_panel();
  //initialize_start_panel();
  //initialize_edit_a_step_panel();
  //initialize_edit_a_valve_panel();
  $("#edit_panel").hide();
 }
)

/*
   function load_new_schedule_data()
   {
      working_data = {} 
      working_data["description"]      = ""
      working_data["step_number"]      = 0
      working_data["start_time"]       = [0, 0]
      working_data["link"]             = edit_schedule+".json"
      working_data["end_time"]         = [0, 0]
      working_data["controller_pins"]  = []
      working_data["steps"]   = []
      working_data["dow"]     = [0, 0, 0, 0, 0, 0, 0], 
      working_data["name"]    = edit_schedule
   }

   function check_radio_selection()
   {  
        var update_flag;
        var item;
        var schedule;

        return_value = [false,null]
        for( i = 0; i < schedule_list.length; i++ )
        {
            item = "#"+schedule_list[i]
            if( $(item).is(":checked") == true )
	    {
              return_value = [ true, schedule_list[i] ]
            }
         }
         return return_value	              

   }

   function copy_schedule_data( new_schedule )
   {
         var status;
         var copy_schedule
         status = check_radio_selection()
         if( status[0] == true )
         {
           copy_schedule            = status[1]
           schedule_data           = JSON.parse(JSON.stringify( schedule_data))
           working_data            = schedule_data[copy_schedule]
           working_data["link"]    = new_schedule+".json"
           working_data["name"]    = new_schedule
           return_value = true;
        } 
        else
        {
           return_value = false
        }

       return return_value;

   }

  
*/
