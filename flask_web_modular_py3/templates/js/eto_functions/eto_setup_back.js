/*
{"recharge_ratio_index":3,"sprayer_radius_index":11,"capacity_eto":0.18,
"recharge_rate":0.21446217997892789,"sprayer_efficiency_index":2,
"soil_depth_index":0,"crop_utilization_index":5,
"recharge_eto":0.06,
"sprayer_radius":3,"pin":9,
"salt_flush_index":2,
"sprayer_rate_index":13,
"controller":"satellite_1",
"soil_type_index":0}
*/


ref_class_name = ""
ref_parent_panel = ""

function find_index()
{
   var i;
   for( i=0; i< eto_data.length; i++)
   {
       if( $("#eto_emiter_id_"+i).is(':checked') == true )
       {
          return i;
       }
    }
    return  -1;  // no item selected
}
function calculate_initial_value( default_value, field_index,array_index = 0 )
{
   if( eto_data.length == 0 )
   {
       return default_value
   }
   else
   {
       if( eto_data[array_index].hasOwnProperty(field_index) == true)
       {      
           return eto_data[array_index][field_index]
       }
       else
       {
          return default_value
       }
   }
}

class Parameter_Setup 
{
   constructor(
               save_id,
               cancel_id,
               reset_id,
               display_tag,
               div_tag,
               input_tag,
               field_tag,
               display_string,
               field_index,
               default_value
                       ) 
   {
       
       //this.save_id = save_id;
       //this.cancel_id = cancel_id;
       //this.reset_id = reset_id;
       this.display_tag = display_tag;
       this.div_tag = div_tag;
       this.input_tag = input_tag
       this.field_tag = field_tag
       this.display_string = display_string
       this.field_index    = field_index
       this.value = calculate_initial_value( default_value, field_index)
       $(input_tag).val(this.value)    
       $(div_tag).hide()
       $(cancel_id ).click( this.close)
       $(reset_id ).click( this.reset)
       $(save_id ).click( this.save)
       $(field_tag).on("slidestop", input_tag, this.update_display)
   }       
      
  open( class_name, parent_panel)
  {
   
    ref_class_name = class_name
    ref_parent_panel = parent_panel

    $(ref_class_name.div_tag).show()
    ref_class_name.set_reset_value(ref_class_name.get_value())

    $(ref_class_name.input_tag).val(this.value)
    $(ref_class_name.display_tag ).html(ref_class_name.display_string  
           + $(ref_class_name.input_tag  ).val() )   
    $(parent_panel).hide()
 
    

  }

  set_reset_value(value)
  {
     this.reset_value = value
  }

  get_reset_value()
  {
    return this.reset_value
  }  


  set_value(value)
  {
     this.value = value
  }
  get_value()
  {
    return this.value
  }  
  close(event, ui)  
  {
    ref_class_name.reset(event,ui)
    $(ref_class_name.div_tag).hide()  
    $(ref_parent_panel).show()
  }
  save( event,ui)
  {
    ref_class_name.close(event,ui)
  }

  reset( event,ui)
  { 
    ref_class_name.set_value(ref_class_name.get_reset_value())
    $(ref_class_name.input_tag).val(ref_class_name.get_value())
    $(ref_class_name.display_tag ).html(ref_class_name.display_string  
           + ref_class_name.get_value())  
    $(ref_class_name.input_tag ).slider("refresh")
    
  }

  update_display (event) 
  {
   
    ref_class_name.set_value($(ref_class_name.input_tag  ).val())
    $(ref_class_name.display_tag ).html(ref_class_name.display_string  
           + $(ref_class_name.input_tag  ).val() )
  }
}  


class Station_Setup 
{
   constructor(  )
   {
       this.sprayer_rate       = "sprayer_rate"
       this.tree_radius        = "tree_radius"
       this.sprayer_default    = 14.0
       this.radius_default     = 6.0
       this.sprayer_value      = calculate_initial_value( this.sprayer_default, this.sprayer_rate)
       this.tree_value         = calculate_initial_value( this.radius_default,  this.tree_radius)
       this.div_tag            = "#station_setup_set"
       this.save_tag           = "#station_save"
       this.cancel_tag         = "#station_cancel"
       this.station_reset      = "#station_reset"
       this.station_add_div    = "#station_add_controls"
       this.controller         = "#controller"
       this.valve              = "#valve"
       this.station_display    = "#station_display"
       this.station_sprayer_display_label   = "Select Sprayer Rate (Gallons/Hour) "
       this.station_sprayer_display         = "#station_sprayer_rate_display"
       this.station_sprayer_rate            = "#station_sprayer_rate"
       this.station_tree_radius_label       = "Select Tree Radius (feet)  " 
       this.station_tree_radius_display     = "#station_radius_display"
       this.station_tree_radius             = "#station_tree_radius"



      $(this.div_tag).hide()

  }


  set_index( index )
  {
     this.index = index
  }
  get_index()
  {
     return this.index
  }  
  open( class_name, parent_panel,add_flag, index)
  {
   
    ref_class_name = class_name
    ref_parent_panel = parent_panel
    ref_class_name.set_index( index)
    $(this.div_tag).show()
    $(parent_panel).hide()
    if( add_flag == true )
    {
       $("#station_add_controls").show()
       // load controls
    }
    else
    {
       $("#station_add_controls").hide()
       
    }
  
    
  }
  

 
}

function main_menu(event,ui)
{
   var index
   var choice

   choice = $("#action-choice-a").val()
   alert(choice)
   if( choice == "recharge")
   {
       min_eto.open(min_eto,"#main_panel")
   }
   if( choice == "crop_util")
   {
       crop_utilization.open(crop_utilization,"#main_panel")
   }
   
   if( choice == "salt")
   {
       salt_flush.open(salt_flush,"#main_panel")
   }

   
   if( choice == "sprayer")
   {
       sprayer_efficiency.open(sprayer_efficiency,"#main_panel")
   }

   
   if( choice == "edit")
   {   
       index = find_index()
       if( index >= 0 )
       {
           station_setup.open(station_setup,"#main_panel", add=false,index = index )
       }       
       else
       {
          set_status_bar("No Resources Selected !!!!")
       }  
   }

   if( choice == "add")
   {   
       index = find_index()
       if( index >= 0 )
       {
           station_setup.open(station_setup,"#main_panel", add=true,index = index )

       }
       else
       {
          set_status_bar("No Resources Selected !!!!")
       }  
   }

   if( choice == "delete")
   {
       var result = confirm("Do you wish to delete eto entry?  ");  
       if( result == true )
       {  
           index = find_index()
           if( index >= 0 )
           {
               eto_data.splice(index, 1);
               save_data();
           }
           else
           {
              set_status_bar("No Resources Selected !!!!")            
           }
     }
   }

   $("#action-choice-a")[0].selectedIndex = 0;
   $("#action-choice-a").selectmenu('refresh');
}

function save_data()
{
  ; // tbd
}

$(document).ready(
function()
{
   
   min_eto = new Parameter_Setup(  "#min_eto_save", "#min_eto_cancel", 
                                  "#min_eto_reset", "#min_eto_display", "#min_eto_set", 
                                  "#min_eto_interval","#min_eto_field","Recharge ETO Value: ", 
                                  "recharge_eto", 0.06)
  
    

   crop_utilization = new Parameter_Setup(   
                                            "#crop_utilization_save", 
                                            "#crop_utilization_cancel", 
                                            "#crop_utilization_reset", 
                                            "#crop_utilization_display", 
                                            "#crop_utilization_set", 
                                            "#crop_utilization_interval",
                                            "#crop_utilization_field",
                                            "Crop Utilization Value   " ,
                                            "crop_utilization_value",.8)  

   salt_flush = new Parameter_Setup(  
                                     "#salt_flush_save", 
                                     "#salt_flush_cancel", 
                                     "#salt_flush_reset", 
                                     "#salt_flush_display", 
                                     "#salt_flush_set", 
                                     "#salt_flush_interval",
                                     "#salt_flush_field",
                                     "Salt Fush Value ",
                                     "salt_flush_value",.1 )
                                                      
 

   sprayer_efficiency = new Parameter_Setup(  
                                             "#sprayer_efficiency_save", 
                                             "#sprayer_efficiency_cancel", 
                                             "#sprayer_efficiency_reset", 
                                             "#sprayer_efficiency_display", 
                                             "#sprayer_efficiency_set", 
                                             "#sprayer_efficiency_interval",
                                             "#sprayer_efficiency_field",
                                             "Sprayer Effiency Value : ",
                                             "sprayer_efficiency",.9 )  

   station_setup = new Station_Setup( )

   $("#action-choice-a").bind('change',main_menu)
   $("#action-choice-a")[0].selectedIndex = 0;
   $("#action-choice-a").selectmenu('refresh');
   
    
}
)

function calculate_data( sprayer_rate,
                         tree_radius,
                         sprinkler_efficiency,
                         salt_flush,
                         crop_utilization )

{
        // effective volume is ft3/hr
        // sprayer rate is in Gallons/hr
        // 1 gallon is 0.133681 ft3
           
        effective_rate = sprayer_rate*sprayer_efficiency/crop_utilization*(1+salt_flush)
        effective_volume = 0.133681 * effective_rate
        effective_area =  sprayer_radius*sprayer_radius*3.14159
        return (effective_volume/effective_area)*12; // converting the eto to inches
}

function load_controllers(  )
{ 
     
   controller_labels = {}
   controller_list   = []
   controller_values = {}
   for( i=0; i<pin_list.length; i++ )
   {
       name   = pin_list[i]["name"]
       length = pin_list[i]["pins"].length;
         
       controller_labels[name] = []
       controller_list.push(name)
       controller_values[name] = []
       
       count = 0;
       for( j = 0; j < length; j++)
       {
            
           temp_value = pin_list[i]["pins"][j];

           if( match_step_valve(j,name) )
           {
               
               ; //controller_labels[name].push("I/O:  "+j+ "    ----- Defined in Irrigation Step Donot Select  ");
           }

           else
           {
               controller_labels[name].push("I/O:  "+(j+1)+ "    Description : "+temp_value);
               controller_values[name].push(j+1)
               count = count +1;
           }

       }

   }
   $("#controller").empty() 
   for( i= 0; i< controller_list.length; i++)
   {
       $("#controller").append($("<option></option>").val(controller_list[i]).html(controller_list[i]));
   }
   $("#valve_controller").selectmenu("refresh");
   load_pins();
 
}

function load_pins()
{
    var controller_index;

    controller_index = $("#valve_controllera")[0].selectedIndex;
    var select_pins = controller_labels[controller_list[controller_index]]
    
    $("#valve_valvea").empty()
    for( i = 0; i < select_pins.length; i++)
    {
        
        $("#valve_valvea").append($("<option></option>").val(i+1).html(select_pins[i]));
    } 
   
    
    $("#valve_valvea").selectmenu("refresh")
}

function match_current_valve( index, controller )
{
  if( controller != current_valve[valve_index][0] )
  {
      return false;
  }
  else
  {
     if( (index+1) == current_valve[valve_index][1] )
     {
       return true;
      }
  }
  return false;


}



/*

    $( "#soil_type_id" ).change(  function(event, ui) 
    {   var soil_index
       
        local_data["soil_type_index"]  = $("#soil_type_id")[0].selectedIndex;
        
        calculate_data();
     });

    $( "#soil_depth_id" ).change(  function(event, ui) 
    {   var soil_depth_index
        
        local_data["soil_depth_index"] = $("#soil_depth_id")[0].selectedIndex;
        calculate_data();       
     });

    $( "#recharge_ratio_id" ).change(  function(event, ui) 
    {  
        
        local_data["recharge_ratio_index"]  = $("#recharge_ratio_id")[0].selectedIndex;
        calculate_data();         
     });

    $( "#sprayer_radius_id" ).change(  function(event, ui) 
    {   var sprayer_radius_id
        
        local_data["sprayer_radius_index"]  = $("#sprayer_radius_id")[0].selectedIndex;
        calculate_data();     
     }); 


    $( "#sprayer_rate_id" ).change(  function(event, ui) 
    {   var sprayer_rate_id
        
        local_data["sprayer_rate_index"]  = $("#sprayer_rate_id")[0].selectedIndex;
        calculate_data();         
     });

    $( "#sprayer_efficiency_id" ).change(  function(event, ui) 
    {   var sprayer_efficiency_id
        
        local_data[ "sprayer_efficiency_index"]  = $("#sprayer_efficiency_id")[0].selectedIndex;
        calculate_data();     
     });


    $( "#salt_flush_id" ).change(  function(event, ui) 
    {   var salt_flush_id
        
        local_data["salt_flush_index"]  = $("#salt_flush_id")[0].selectedIndex;
        calculate_data();         
     });

    $( "#crop_utilization_id" ).change(  function(event, ui) 
    {   
        
        local_data["crop_utilization_index"]  = $("#crop_utilization_id")[0].selectedIndex;
        calculate_data();         
     });

    $( "#edit_panel_save" ).click(  function(event, ui) 
    {   
        
         
 
       var json_data = {}
       var json_string;
       var url;
       var result = confirm("Do you want to change schedule data ?");
       if( result == true )
       {    // making update
             if( add_flag == true )
             {
               
                eto_data.push( local_data );
             }
             else
             {
                eto_data[ref_index] = local_data;
             }
             json_object = eto_data
             var json_string = JSON.stringify(json_object);
             url = window.location.href;
             $.ajax
             ({
                    type: "POST",
                    url: '/ajax/save_app_file/eto_site_setup.json',
                    dataType: 'json',
                    async: true,
                    contentType: "application/json",
                    data: json_string,
                    success: function () 
		    {
                       window.location.href = url;
  
                    },
                    error: function () 
		    {
                       alert('/ajax/save_app_file/eto_site_setup.json'+"  Server Error Change not made");

		      
		       
                    }
              })
      }

     });

    $( "#edit_panel_cancel" ).click(  function(event, ui) 
    {   
        $("#main_panel").show()
        $("#station_setup").hide()
                 
     });
    $( "#edit_panel_reset" ).click(  function(event, ui) 
    {   
          load_controls(ref_index);
       
     });


 
     function find_index()
     {
       var i;
     

       
       for( i=0; i< eto_data.length; i++)
       {
           if( $("#eto_emiter_id_"+i).is(':checked') == true )
           {
               return i;
           }
        }
       return  -1;  // no item selected
    
     
     }
     $("#action-choice-a").bind('change',function(event,ui)
     {
       var index
       

       if( $("#action-choice-a").val() == "edit" )
       {
            index = find_index()
            if( index >= 0 )
            {
                  load_controls(index)
                  $("#add_controls").hide()
                  $("#main_panel").hide()
                  $("#station_setup").show()
  
            }
            else
            {
                alert("No Eto Resource Selected")            
            }

       }
       if( $("#action-choice-a").val() == "delete" )
       {       
               index = find_index()
               if( index >= 0 )
               {
                  eto_data.splice(index, 1);
                  save_data();
               }
               else
               {
                alert("No Eto Resource Selected")            
                }

           
       }
       if( $("#action-choice-a").val() == "add" )
       {
            add_controls()
            $("#add_controls").show()
            $("#main_panel").hide()
            $("#station_setup").show()

       }
       $("#action-choice-a")[0].selectedIndex = 0;
       $("#action-choice-a").selectmenu('refresh');
     })

  $( "#valve_controllera" ).bind( "change", valve_panel_controller_select );
  $( "#valve_valvea").bind("change",valve_panel_valve_select );
  $("#main_panel").show();
  $("#station_setup").hide();
  function save_data()
  {   
        
         
 
       var json_data = {}
       var json_string;
       var url;
       var result = confirm("Do you want to change schedule data ?");
       if( result == true )
       {    
             json_object = eto_data
             var json_string = JSON.stringify(json_object);
             url = window.location.href;
             $.ajax
             ({
                    type: "POST",
                    url: '/ajax/save_app_file/eto_site_setup.json',
                    dataType: 'json',
                    async: true,
                    contentType: "application/json",
                    data: json_string,
                    success: function () 
		    {
                       window.location.href = url;
  
                    },
                    error: function () 
		    {
                       alert('/ajax/save_app_file/eto_site_setup.json'+"  Server Error Change not made");

		      
		       
                    }
              })
      }

     }
  });

*/
