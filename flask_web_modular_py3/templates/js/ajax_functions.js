
/*
**
**
** Ajax functions
**
**
*/


function ajax_get( url_path, error_message, success_function )
{
	
   $.ajax(
   {
       type: "GET",
       url: url_path,
       dataType: 'json',
       async: true,
       //json object to sent to the authentication url
       success: success_function,
              
       error: function () 
		    {
           alert(error_message);  // replace this
		       
		       
      }
   });
}

function ajax_post_confirmation(url_path, data, confirmation_string, 
                                       success_message, error_message )
{
 
   var result = confirm("Do you want to make mode change");  // change this
   if( result == true )
   {
       var json_string = JSON.stringify(data);
       $.ajax ({  type: "POST",
                  url: url_path,
                  dataType: 'json',
	                 contentType: "application/json",
                  async: true,
                  data: json_string,
                  success: function () 
		                {
                       alert(success_message);  // fix this
		                 },

                   error: function () 
		                {
                       alert(error_message);  // fix this
		                 }
           })
   }
}

function ajax_post_get(url_path, data, success_function, error_message) 
{
     var json_string = JSON.stringify(data);

     $.ajax ({  type: "POST",
                  url: url_path,
                  dataType: 'json',
	                 contentType: "application/json",
                  async: true,
                  data: json_string,
                  success: success_function,

                   error: function () 
		                {
                       alert(error_message);  // fix this
		                 }
           })
   
}
 
 
