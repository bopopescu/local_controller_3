import math
import numpy as np
from scipy.optimize import curve_fit

class Curve_Fit:

   def __init__( self ):
       pass

   def curve_fit_function( self, x, a,b,c):
       return (a*x*x)+(b*x)+c

   def compute_curve_error( self, new_curve, ref_curve, x_range):
       return_value = {}
       error_abs = 0
       error     = 0

       for i in range(6,x_range):
           data1 = self.curve_fit_function( i, new_curve[0],new_curve[1],new_curve[2] )
           data2 = self.curve_fit_function( i, ref_curve[0],ref_curve[1],ref_curve[2] )

           error_abs = error_abs + math.fabs( data1 - data2 )
           error     = error + (data1 - data2)
       return_value["error"] = error
       return_value["error_abs"] = error_abs
       return return_value

       

   def compute_raw_error( self, curve, x_range, y_data):
       return_value = {}
       error_abs = 0
       error     = 0

       for i in range(6,x_range):
           data = self.curve_fit_function( i, curve[0],curve[1],curve[2] )
           error_abs = error_abs + math.fabs( y_data[i] - data )
           error     = error + ( y_data[i] - data )
       return_value["error"] = error
       return_value["error_abs"] = error_abs
       return return_value


   def curve_fit( self, x_range, y_data, return_data ):
       
       return_value["x_range"]   = x_range
       return_value["y_data"]    = y_data
       
       x_data_np = np.asarray( range(6,x_range))
       y_data_np = np.asarray( y_data[6:] )
       a,b    = curve_fit(self.curve_fit_function, x_data_np, y_data_np )
       return_data["new_curve"] = a
       if "ref_curve" not in return_data:
           return_data["ref_curve"] = None
       if return_data["ref_curve"] == None:
          return_data["ref_curve"] = return_data["new_curve"]
       return_data["raw_error_new"] = self.compute_raw_error( return_data["new_curve"], x_range, y_data )
       return_data["raw_error_ref"] = self.compute_raw_error( return_data["ref_curve"], x_range, y_data )
       return_data["curve_error"] = self.compute_curve_error( return_data["new_curve"],
                                   return_data["ref_curve"],x_range)
       return return_data

if __name__ == "__main__":
   import random

   curve_fit_class = Curve_Fit()
   return_value = {}
   x_range = 60
   y = []
   for i in range(0,60):
     y.append(80 - .2*i -.01*i*i + random.randint(-5,5))
   curve_fit_class.curve_fit(  x_range, y, return_value )
   print( return_value)
   

