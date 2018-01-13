#
#
# Code for test web socket
#
#
#
from flask_socketio import SocketIO
class Load_Web_Socket_Handler(object):

   def __init__( self, app, render_template ):
       self.app      = app
       self.socket_io = SocketIO(app)

  