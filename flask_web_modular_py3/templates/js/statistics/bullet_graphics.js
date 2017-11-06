
var canvas_id_array = []
var window_width = 0
var context_array = []
var canvas_height = 5*14
var canvas_draw_pixel = 5





function _initialize_a_canvas_(step_index)
{
     
     let canvas_id = document.getElementById("canvas"+step_index)
     
     canvas_id_array.push(canvas_id)
     canvas_id.height = canvas_height+5
     canvas_id.width  = window_width    
     context =  canvas_id.getContext("2d"); 
     context_array.push(context)
     context.font="15px sans-serif";  
     context.fillStyle = "Grey";
     context.fillRect(70,0,window_width,canvas_height );
     context.fillStyle = "Black"
     context.textAlign = "left";
     context.fillText("Step "+(step_index+1),10,canvas_height*.5);
                
}




function bullet_initialize_canvas( step_number)
{
    window_width  = $( window ).width()*.95
    for( i = 0; i < step_number; i++ )
    {
        _initialize_a_canvas_(i,window_width)
    }
}

function _draw_major_grid_( context,fillStyle)
{
    context.fillStyle = fillStyle
    let size_base = (window_width - 70)/10
    for( i = 1; i< 10 ; i++)
    {
        let size_ref = 70+(size_base*i)
        console.log(size_ref)
        context.fillRect(size_ref,0,1,canvas_height)
    }
}


function _draw_minor_grid_( context,fillStyle)
{
    context.fillStyle = fillStyle
    let size_base = (window_width - 70)/20
    for( i = 1; i< 20 ; i++)
    {
        let size_ref = 70+(size_base*i)
        console.log(size_ref)
        context.fillRect(size_ref,0,1,canvas_height)
    }
}

function _draw_limit_( context, value, fillStyle,  pixel_step )
{  
    
    context.fillStyle = fillStyle
    context.fillRect(70,0,70+value*pixel_step ,canvas_height)

}

function _draw_values_( context, values, fillStyle,  pixel_step )
{  
    
    context.fillStyle = fillStyle
    let y_value = canvas_height-4
    for( i =0; i< values.length; i++ )
    {
        
        context.fillRect(70,y_value,70+values[i]*pixel_step ,3)
        y_value -= 5
    }
}        

function canvas_draw( canvas_index, value_array , limit,std_array, max_value )
{
    // fill canvas grey
    // fill limit value
    // fill values 
    // fill std
    // fill grid
    let context = context_array[canvas_index]
    
    context.fillStyle = "Grey";  // replace Grey for production
    context.fillRect(70,0,window_width,canvas_height );
    pixel_start = 70
    pixel_range = window_width-pixel_start;
    pixel_step = pixel_range/max_value
    
    _draw_limit_( context, limit, "Black" , pixel_step )
    _draw_values_( context, value_array, "Orange" , pixel_step )
    _draw_minor_grid_( context,"Green")
    _draw_major_grid_( context,"Red")
        
} 