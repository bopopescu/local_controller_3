
var data_length = 0
var draw_array = []
var x_start_range = 0
var x_start_index = 0

var v_max_ref 
var hh = {}
var selected_field;
var selected_attribute;
var draw_data;




function make_refresh()
{
   let schedule_id  =    $("#schedule_select").val()
   
   
   let temp     = "/composite_statistics/"+schedule_id+"/"+field_id
   
   window.location.href = temp
}    


function cancel_schedule_step()
{
    
     
     $( "#change_schedule_step" ).popup( "close" )
}


function populate_schedule_step()
{
    
    
    $("#schedule_select").empty()
    for( i = 0; i < schedule_list.length; i++)
    {
        
        $("#schedule_select").append($("<option></option>").val(i).html(schedule_list[i]));
    } 

    $("#schedule_select").val(schedule_index);
    $("#schedule_select").selectmenu("refresh")
    
 }   

 
function display_new_field_attribute()
{
   selected_field       =    $("#field_select").val()
   field_id             =    $("#field_select")[0].selectedIndex
    
  
   
   $( "#change_field_attribute" ).popup( "close" )
}    


function cancel_field_attribute()
{
     
     $( "#change_field_attribute" ).popup( "close" )
}



function populate_field_attribute()
{
   
    
    $("#field_select").empty()
    for( let i = 0; i < field_list.length; i++)
    {
        
        $("#field_select").append($("<option></option>").val(field_list[i]).html(field_list[i]));
    } 

    $("#field_select").val(selected_field)
    $("#field_select").selectmenu("refresh")
    
    
}

 
$(document).ready(
 function()
 {  
   
    
   draw_array = []

   bullet_initialize_canvas( step_number)
   canvas_draw( 0, [5,4,3,2,1] , 3 ,[.25,.25,.25,.25] ,  10 )
   selected_field       =  field_list[field_id]

   let field_name = field_list[field_id]
                     
   
   $("#save_schedule_step").bind("click",make_refresh);
   
   $("#cancel_schedule_step").bind("click",cancel_schedule_step);
   $("#change_schedule_step").on("popupafteropen", populate_schedule_step ); 


   $("#save_field_attribute").bind("click", display_new_field_attribute);
   
   $("#cancel_field_attribute").bind("click",cancel_field_attribute);
   $("#change_field_attribute").on("popupafteropen", populate_field_attribute);                      
                           
   
  })

  