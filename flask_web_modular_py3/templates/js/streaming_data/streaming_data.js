var field_keys = []
var data_length = 0
var draw_array = []
var x_start_range = 0
var x_start_index = 0
var v_min = Number.MAX_SAFE_INTEGER;
var v_max = -Number.MAX_SAFE_INTEGER;
var ref_field_index
var v_min
var v_max_ref 
var hh = {}

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
  */
  x_start_index = .75
  x_start_range = .25
  v_min = Number.MAX_SAFE_INTEGER;
  v_max = -Number.MAX_SAFE_INTEGER;
  ref_field_index = 0
  
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
 
$(document).ready(
 function()
 {  
   
    
   prepare_data( )

    
   limit_low = 0
   limit_high = 40
   x_axis  = "time"
   y_axis  = field_keys[0]
   hh = new Dygraph(document.getElementById("div_g"), draw_array,
                          {
                            width  : $(window).width()*.9,
                            height : $(window).height()*.65,
                            drawPoints: true,
                            showRoller: true,
                            valueRange: [limit_low, limit_high ],
                            labels: [x_axis, y_axis]
                          });
     
     
 
   display_data(0)
   
  $("#cancel_index_changes").bind("click",cancel_field_index);
  $("#make_index_changes").bind("click", save_field_index );
  $("#change_index").on("popupafteropen", change_field_index );
                          

  $("#cancel_time_changes").bind("click",cancel_time_index);                          
  $("#make_time_changes").bind("click", save_time_index )
  $("#change_time_index").on("popupafteropen", change_time_index );
                    
  $("#cancel_vertical_changes").bind("click",cancel_vertical_index);
  $("#make_vertical_changes").bind("click", save_vertical_index )
  $("  #change_vertical_index").on("popupafteropen", change_vertical_index );


  })
