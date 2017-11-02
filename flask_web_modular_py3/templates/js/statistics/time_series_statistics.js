
function make_refresh()
{
   let schedule_id  =    $("#schedule_select").val()
   let step_id      =    $("#step_select").val()
   let field_id     =    $("#field_select")[0].selectedIndex
   let attribute_id     =    $("#attribute_select")[0].selectedIndex
   let temp     = "/detail_statistics/"+schedule_id+"/"+step_id+"/"+field_id+"/"+attribute_id
   
   window.location.href = temp
}    


function cancel_schedule_step()
{
     
    
}

function schedule_change()
{
  
 
}

function populate_schedule_step()
{
    
    
 
}





function display_new_schedule()
{
   let schedule_id  =    $    ("#schedule_select")[0].selectedIndex
   let step_id      =         $("#step_select")[0].selectedIndex
   let field_id     =         $("#field_select")[0].selectedIndex
   let schedule_step     =    $("#attribute_select")[0].selectedIndex
   let display_number    =    $("#display_number_select")[0].selectedIndex
   let temp     = "/detail_statistics/"+schedule_id+"/"+step_id+"/"+field_id+"/"+schedule_step+"/"+display_number
   
   window.location.href = temp
}

function schedule_change()
{
     schedule_index = $("#schedule_select").val()

    let step_number = schedule_data[ schedule_list[schedule_index ] ]["step_number"]
    $("#step_select").empty()
    for( i = 0; i < step_number; i++)
    {
        
        $("#step_select").append($("<option></option>").val(i).html(i+1));
    } 

    $("#step_select")[0].selectedIndex = 0;
    $("#step_select").selectmenu("refresh")
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

    $("#schedule_select").val(schedule_id);
    $("#schedule_select").selectmenu("refresh")
    
    $("#step_select").empty()
    for( i = 0; i < step_number; i++)
    {
        
        $("#step_select").append($("<option></option>").val(i).html(i+1));
    } 

    $("#step_select")[0].selectedIndex = step;
    $("#step_select").selectmenu("refresh")
    ppopulate_fields_select()
}

   // field
function display_field_value()
{
    ;
}
function cancel_field_index()
{
    ;
}
function populate_fields_select()
{
    ;
}                      
                           
                          
      // step index
function display_step_index()
{
    ;
}
function cancel_step_index()
{
    ;
}
function  populate_step_index()
{
    ;
}
   
   // displayr number
function display_display_number()
{
    ;
}
function cancel_display_number()
{
    ;
}
function populate_display_number()
{
    ;
} 

 
$(document).ready(
 function()
 {  
   
    
   draw_array = []

 
 
   limit_low = 0
   limit_high = 40
   x_axis  = "time"
   y_axis  = ""
   hh = new Dygraph(document.getElementById("div_g"), draw_array,
                          {
                            width  : $(window).width()*.9,
                            height : $(window).height()*.65,
                            drawPoints: true,
                            showRoller: true,
                            valueRange: [limit_low, limit_high ],
                            labels: [x_axis, y_axis]
                          });
   irrigation_data.reverse()
                          
   //display_data()
    // schedule step                    
   $("#save_schedule_step").bind("click",display_new_schedule);
   $("#schedule_select").bind("change",schedule_change);
   $("#cancel_schedule_step").bind("click",cancel_schedule_step);
   $("#change_schedule_step").on("popupafteropen", populate_schedule_step ); 

   // field
   $("#save_field_attribute").bind("click", display_field_value);
   $("#cancel_field_index").bind("click",cancel_field_index);
   $("#change_field_index").on("popupafteropen", populate_fields_select );                      
                           
                          
      // step index
   $("#save_field_index").bind("click", display_step_index);
   $("#cancel_step_index").bind("click",cancel_step_index);
   $("#change_step_inde").on("popupafteropen", populate_step_index ); 
   
   // displayr number
   $("#save_display_number").bind("click", display_display_number);
   $("#cancel_display_number").bind("click",cancel_display_number);
   $("#change_display_nunber").on("popupafteropen", populate_display_number );                      
                     
   
  })

  
  
  
 /* 
  
  var data_length = 0
var draw_array = []
var x_start_range = 0
var x_start_index = 0

var v_max_ref 
var hh = {}
var selected_field;
var selected_attribute;
var draw_data;



function auto_scale()
{
   v_min = Number.MAX_SAFE_INTEGER;
   v_max = -Number.MAX_SAFE_INTEGER;

  for( i = 0; i < draw_array.length;i++)
  {
      if( v_min > draw_array[i][2] )
     {
        
        v_min = draw_array[i][2] 
     }
     if( v_max < draw_array[i][2] )
     {
        v_max = draw_array[i][2] 
     }
     
   }
   
   if( v_min < 0 )
   {
      v_min = 1.25*v_min
   }
   else
   { 
      v_min = .75 *v_min
   }
   if( v_min == 0 )
   {
      v_min = -.5
   }
   if( v_max > 0 )
   {
      v_max = 1.25*v_max
   }
   else
   { 
      v_max = .75 *v_max
   }
   if( v_max == 0 )
   {
      v_max = .5
   }
   
   return_value = [ v_min,v_max]
   return return_value
 

}
function display_data( field_name,attribute_name )
{
  
  
  $("#field_description").html("Current Selected Measurement Field/Attribute is:  "+field_name+":"+attribute_name )
 
 
  
  draw_array = []
  for( let i = 0; i < irrigation_data.length; i++)
  {
     
     var item = irrigation_data[i]
     field_data = item["fields"]
     limit_field_data = limit_data["fields"]
     if( !(field_name in field_data) )
     {
         break;
     }
     
     limit_field = limit_field_data[field_name]
     data_field = field_data[field_name]
     if( !(attribute_name in data_field ))
     {
         break;
     }
     // valid point
     limit_point = limit_field[attribute_name]
     data_point = data_field[attribute_name];
     time_data = new Date(item["time"]*1000)
     draw_array.push([time_data,limit_point ,data_point])

  }
  
  
   x_axis  = "time"
   y_axis  = "data"
   let scale = auto_scale()
   

   hh.updateOptions( { 'file': draw_array,
                        'valueRange': scale,
                        labels: ["time", "limit","data"]

                        } )
  
} 
    

function make_refresh()
{
   let schedule_id  =    $("#schedule_select").val()
   let step_id      =    $("#step_select").val()
   let field_id     =    $("#field_select")[0].selectedIndex
   let attribute_id     =    $("#attribute_select")[0].selectedIndex
   let temp     = "/detail_statistics/"+schedule_id+"/"+step_id+"/"+field_id+"/"+attribute_id
   
   window.location.href = temp
}    


function cancel_schedule_step()
{
     
     $( "#change_schedule_step" ).popup( "close" )
}

function schedule_change()
{
   schedule_index = $("#schedule_select").val()

   let step_number = schedule_data[ schedule_list[schedule_index ] ]["step_number"]
   $("#step_select").empty()
    for( i = 0; i < step_number; i++)
    {
        
        $("#step_select").append($("<option></option>").val(i).html(i+1));
    } 

    $("#step_select")[0].selectedIndex = 0;
    $("#step_select").selectmenu("refresh")
 
}

function populate_schedule_step()
{
    
    
    $("#schedule_select").empty()
    for( i = 0; i < schedule_list.length; i++)
    {
        
        $("#schedule_select").append($("<option></option>").val(i).html(schedule_list[i]));
    } 

    $("#schedule_select").val(schedule_id);
    $("#schedule_select").selectmenu("refresh")
    
    $("#step_select").empty()
    for( i = 0; i < step_number; i++)
    {
        
        $("#step_select").append($("<option></option>").val(i).html(i+1));
    } 

    $("#step_select")[0].selectedIndex = step;
    $("#step_select").selectmenu("refresh")
    populate_field_attribute()
}

 
function display_new_field_attribute()
{
   selected_field       =    $("#field_select").val()
   selected_attribute   =    $("#attribute_select").val()
    
  
   display_data( selected_field,selected_attribute )
   $( "#change_field_attribute" ).popup( "close" )
}    


function populate_time_attribute()
{
     
     $( "#change_time_step" ).popup( "close" )
}

function field_change()
{
    ; // not needed
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
    
    $("#attribute_select").empty()
    for( let i = 0; i <  sub_field_list.length ; i++)
    {
        
        $("#attribute_select").append($("<option></option>").val(sub_field_list[i]).html(sub_field_list[i]));
    } 
    $("#attribute_select").val(selected_attribute)
    
    $("#attribute_select").selectmenu("refresh")
}
*/