#
#
#  setup web_server_py3.py
#
#
#


import flask
from flask import Flask
from flask import render_template,jsonify,request
from flask_httpauth import HTTPDigestAuth
auth = HTTPDigestAuth()

@auth.get_password
def get_pw(self,username):
   if username in users:
      return web_users.get(username)
   return None



app = Flask(__name__)
app.config['SECRET_KEY']      = startup_dict["SECRET_KEY"]
app.config["DEBUG"]           = startup_dict["DEBUG"]
app.template_folder           = 'flask_web_modular/templates'
app.static_folder             = 'flask_web_modular/static'



