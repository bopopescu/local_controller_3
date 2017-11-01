
var data_length = 0
var draw_array = []
var x_start_range = 0
var x_start_index = 0
var v_min = Number.MAX_SAFE_INTEGER;
var v_max = -Number.MAX_SAFE_INTEGER;

var v_min
var v_max_ref 
var hh = {}
var selected_field;
var selected_attribute;    

function make_refresh()
{
   let schedule_id  =    $("#schedule_select").val()
   let step_id      =    $("#step_select").val()
   let temp     = "/detail_statistics/"+schedule_id+"/"+step_id
   
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
}

 
function display_new_field_attribute()
{
   selected_field       =    $("#field_select").val()
   selected_attribute   =    $("#attribute_select").val()
  
   alert(selected_field+":"+selected_attribute)
   $( "#change_field_attribute" ).popup( "close" )
}    


function cancel_field_attribute()
{
     
     $( "#change_field_attribute" ).popup( "close" )
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

 
$(document).ready(
 function()
 {  
   
    
   draw_array = []

   selected_field       =  field_list[0]
   selected_attribute   =  sub_field_list[0]   
 
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
     
   $("#save_schedule_step").bind("click",make_refresh);
   $( "#schedule_select").bind("change",schedule_change);
   $("#cancel_schedule_step").bind("click",cancel_schedule_step);
   $("#change_schedule_step").on("popupafteropen", populate_schedule_step ); 


   $("#save_field_attribute").bind("click", display_new_field_attribute);
   $("#field_select").bind("change",field_change);
   $("#cancel_field_attribute").bind("click",cancel_field_attribute);
   $("#change_field_attribute").on("popupafteropen", populate_field_attribute );                      
                           
   //display_data(ref_field_index)
   
  //$("#cancel_index_changes").bind("click",cancel_field_index);
  //$("#make_index_changes").bind("click", save_field_index );
  //$("#change_index").on("popupafteropen", change_field_index );
                          

  //$("#cancel_time_changes").bind("click",cancel_time_index);                          
  //$("#make_time_changes").bind("click", save_time_index )
  //$("#change_time_index").on("popupafteropen", change_time_index );
                    
  //$("#cancel_vertical_changes").bind("click",cancel_vertical_index);
  //$("#make_vertical_changes").bind("click", save_vertical_index )
  //$("#change_vertical_index").on("popupafteropen", change_vertical_index );

  //$("#footer-button_4").bind("click",make_refresh)
  })

  /*
  function change_field_index()
{
    
    $("#field_index").empty()
    for( i = 0; i < field_keys.length; i++)
    {
        
        $("#field_index").append($("<option></option>").val(i).html(field_keys[i]));
    } 

    $("#field_index")[0].selectedIndex = ref_field_index;
    $("#field_index").selectmenu("refresh")
}
function change_time_index()
{
    $("#time_slider_1").val(x_start_index*100).slider('refresh');
    $("#time_slider_2").val(x_start_range*100).slider('refresh');
    
}
function change_vertical_index()
{
    
    v_min_ref = v_min
    v_max_ref = v_max
    auto_scale()
    $("#v_slider_1").prop({
        min: v_min,
        max: v_max
     }).slider("refresh");
     $("#v_slider_1").val(v_min_ref).slider("refresh")
      
    $("#v_slider_2").prop({
        min: v_min,
        max: v_max
     }).slider("refresh");
     $("#v_slider_2").val(v_max_ref).slider("refresh")
     v_min = v_min_ref 
     v_max = v_max_ref
 }
 
function cancel_field_index()
{
     
     $( "#change_index" ).popup( "close" )
}

function save_field_index()
{
    ref_field_index = $("#field_index").val()
    v_min = Number.MAX_SAFE_INTEGER
    v_max = -Number.MAX_SAFE_INTEGER 
    x_start_index = .75
    x_start_range = .25    
    display_data( ref_field_index )
    $( "#change_index" ).popup( "close" )
}
    
  
function cancel_time_index()
{
     
     $( "#change_time_index" ).popup( "close" )
}
function save_time_index()
{
    
    x_start_index = ($("#time_slider_1").val()/100);
    x_start_range = ($("#time_slider_2").val()/100); 
    display_data( ref_field_index )
    $( "#change_time_index" ).popup( "close" )
    
}    


function cancel_vertical_index()
{
  
     $( "#change_vertical_index" ).popup( "close" )
}
function save_vertical_index()
{
    v_min = $("#v_slider_1").val()
    v_max = $("#v_slider_2").val()
     display_data( ref_field_index )

    $( "#change_vertical_index" ).popup( "close" )
}


function prepare_data( )
{
  data_length = time_data.length
  let temp_keys = Object.keys(time_data[0])
  
  field_keys = []
  for( i =0; i< temp_keys.length; i++)
  {
     if( (temp_keys[i] != "time_stamp") &&(temp_keys[i] != "namespace"))
     {
       
        field_keys.push(temp_keys[i])
     }
  }
  draw_array = []
  time_data.reverse()
  /*
  for( i = 0; i < data_length; i++)
  {
     
     temp_data = [ new Date(time_data[i]["time_stamp"]),time_data[i][field_keys[0]] ]
     
     draw_array.push(temp_data)
  }

  x_start_index = .75
  x_start_range = .25
  v_min = Number.MAX_SAFE_INTEGER;
  v_max = -Number.MAX_SAFE_INTEGER;
  
  
}

function auto_scale()
{

  for( i = 0; i < draw_array.length;i++)
  {
     if( v_min > draw_array[i][1] )
     {
        v_min = draw_array[i][1] 
     }
     if( v_max < draw_array[i][1] )
     {
        v_max = draw_array[i][1] 
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
}


function display_data( index )
{

  draw_array = []
  let field_key_ref = field_keys[index]
  $("#field_description").html("Current Selected Stream is:  "+field_key_ref )
  temp_x = Math.round(time_data.length *x_start_index)
  temp_x_range = Math.round(x_start_range *time_data.length)

  if( ( temp_x + temp_x_range ) >= time_data.length)
  {
     temp_x_range = time_data.length - temp_x
  } 
  
 
  for( let i = temp_x; i < temp_x+ temp_x_range; i++)
  {
    
     
     temp_data = [ new Date(time_data[i]["time_stamp"]),time_data[i][field_key_ref] ]
     draw_array.push(temp_data)
  }
   x_axis  = "time"
   y_axis  = field_key_ref
   if( v_min == Number.MAX_SAFE_INTEGER)
   {
      auto_scale()
   }

   hh.updateOptions( { 'file': draw_array,
                        'valueRange': [v_min, v_max ],
                        labels: [x_axis, y_axis]

                        } )
  
} 
*/