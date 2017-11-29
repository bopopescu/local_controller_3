var field_keys = []
var data_length = 0
var draw_array = []
var x_start_index = 0
var x_start_range = 1.0 
var v_min
var v_max_ref 
var hh = {}

function make_refresh()
{
   let  selected_index = $("#field_index").val()
   let temp = '/control/display_past_actions/'+selected_index

   window.location.href = temp
}    
    
function change_field_index()
{
    
    $("#field_index").empty()
    for( i = 0; i < field_keys.length; i++)
    {
        
        $("#field_index").append($("<option></option>").val(field_keys[i]).html(field_keys[i]));
    } 

    $("#field_index").val(ref_field_index)
    $("#field_index").selectmenu("refresh")
}

function cancel_field_index()
{
     
     $( "#change_index" ).popup( "close" )
}

   
  


function prepare_data( )
{
  data_length = time_data.length
 
  
  field_keys = Object.keys(events)
  field_keys.sort()
 
  time_data.reverse()
  
 

}


function display_data( index )
{

   
  
} 

function radio_select()
{
 
    $("#description").html( "Event Data: "+JSON.stringify(time_data[this.value].data) )
}
 
$(document).ready(
 function()
 {  
   
   
   prepare_data( )

     
 
   display_data(ref_field_index)
   
  $("#cancel_index_changes").bind("click",cancel_field_index);
  $("#make_index_changes").bind("click", make_refresh );
  $("#change_index").on("popupafteropen", change_field_index );
  $('input[type=radio][name=radio-choice]').change(radio_select); 

  
  })
